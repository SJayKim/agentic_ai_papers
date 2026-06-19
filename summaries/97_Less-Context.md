# 97. Less Context, Better Agents: Efficient Context Engineering for Long-Horizon Tool-Using LLM Agents

> 📄 **저자**: Abhilasha Lodha, Mahsa Pahlavikhah Varnosfaderani, Abir Chakraborty, Abhinav Mithal (Microsoft)
> 📚 **학회/발표 기관**: arXiv preprint (Microsoft)
> 📅 **발표 날짜**: 2026.06
> 🔗 **arXiv**: https://arxiv.org/abs/2606.10209
> 💻 **코드**: 명시되지 않음 (재현용 아티팩트는 Appendix A~J에 알고리즘/스코어링 로직/통계 헬퍼 코드 형태로 제공)

---

## Problem

엔터프라이즈 워크플로우에서 자율 에이전트로 배포된 LLM은 "verbose tool response"로 인한 컨텍스트 윈도우 폭주와 과도한 추론 비용이라는 치명적 병목에 직면한다.
구체적으로 Microsoft Dynamics 365 F&O(D365 F&O)를 MCP 프록시로 다루는 호텔 경비 itemization 작업에서, 각 도구 응답은 폼 메타데이터·중첩된 폼 상태·네비게이션 breadcrumb·시스템 정보 등 의사결정과 무관한 토큰을 500~3,000개씩 담고 있다.
영수증 1건을 4~22개(중앙값 8, 최대 23) 개별 라인 아이템으로 분해해야 하고 각 라인마다 생성·입력·검증을 위한 다수 도구 호출이 필요하므로, 15~30회 도구 상호작용에서 누적 컨텍스트가 50,000~150,000+ 토큰까지 불어나 토큰 예산을 빠르게 소진한다.
처리 비용은 컨텍스트 길이에 선형 비례하므로 full-history 유지는 프로덕션 스케일에서 비용상 비현실적이며, 업계에서 "context rot"이라 부르는 현상(토큰 수 증가에 따라 hard limit 도달 전에 모델의 실효 recall이 저하)이 동일하게 나타난다.
특히 이 작업은 미할당 잔액이 정확히 $0.00에 도달해야만 완료로 인정되는 strict zero-residual 기준을 가지므로, 부분 완료가 곧 실패이며 회계 오류·정책 위반·수작업 교정 비용을 유발한다.

---

## Motivation

저자들의 핵심 직관은 컨텍스트 엔지니어링, 즉 "각 스텝에서 에이전트 컨텍스트에 무엇을 남길지 의도적으로 관리"하는 것이 모델 재학습 없이 추론 시간(inference-time)에만 작동하는 실용적 해법이라는 점이다.
파인튜닝을 하지 않는 frozen 에이전트를 택한 이유는, 이 방식이 LLM 백엔드에 portable하고 즉시 적용 가능하며 프로덕션 배포 시 별도 학습 파이프라인이 불필요하기 때문이다.
또 다른 직관은 오래된 도구 상호작용이 superseded(이미 갱신되어 폐기된) 폼 상태를 기술하므로, full-history 유지가 단순히 중복(redundant)이 아니라 능동적으로 해롭다(actively detrimental)는 가설이다.
즉 stale 폼 상태를 남기면 현재 시스템 상태에 대한 이해를 흐려 잘못된 필드 할당이나 네비게이션 오류를 일으킨다고 본 것이다.
따라서 (1) 최근 도구 상호작용으로 컨텍스트를 제한하면 task 관련 집중도가 올라가고 overflow를 막으며, (2) 가지치기된(pruned) 컨텍스트를 자동 요약하면 큰 토큰 오버헤드 없이 task 수준 상황 인식을 보존한다는 두 가설을 검증하고자 한다.

---

## Method

핵심은 토큰 단위 압축(LLMLingua/Selective Context)이나 외부 메모리 스토어(MemoryBank/LongMem)와 구별되는, "도구 call/response 쌍 전체"라는 semantic 단위에서 동작하는 recency 기반 가지치기 + 자동 요약 정책이다.
폼 상태(컨트롤명, 잔액 등)는 verbatim으로 읽어야 하므로, 보존된 상호작용의 정확한 텍스트는 손대지 않고 오직 완전한 단위(complete unit)만 evict하거나 요약한다.

평가 시스템은 4개 컴포넌트로 구성된다.
첫째, itemization 워크플로우를 실행하는 주 에이전트 GPT-5(상세 시스템 프롬프트 포함).
둘째, 에이전트의 follow-up 질문/확인 요청에 응답하는 "사용자 모델" GPT-4.1(C2~C4에만 존재, 완료 프로토콜 정의).
셋째, D365 F&O 폼 상호작용을 21개 이산 도구(폼 도구 13 + 데이터 도구 6 + API 도구 2)로 노출하는 MCP 서버.
넷째, human-in-the-loop 없이 에이전트-도구 루프와 컨텍스트 로직, 메트릭을 관리하는 비대화형(non-interactive) 평가 하네스.

컨텍스트 구성은 Algorithm 1(CONSTRUCTCONTEXT)로 정확히 명세된다.
전체 메시지 history H, 유지할 최근 도구 쌍 개수 N(pruning window), 요약 window W를 입력으로 받는다.
1단계: H 안의 tool 메시지 수 c를 센 뒤, evict할 쌍 개수 d = max(0, c−N)를 계산한다 (d=0이면 H 그대로 반환).
2단계: H를 순서대로 순회하며 오래된 tool 메시지부터 d개를 evict 리스트 E로 옮기되, 그 직전의 assistant tool-call 메시지도 함께 E로 이동시켜 "쌍 단위"로 제거한다 (나머지는 유지 리스트 K에 append).
3단계: W≠0이고 evict된 것이 있으면, E에서 가장 최근의 W개(W=−1이면 전부)를 SUMMARIZE 함수로 압축한다.
4단계: 생성된 요약을 "Summary of previous tool calls: s" 형태의 단일 메시지로 만들어, K에서 가장 이른 evict 위치(earliest evicted position)에 삽입한 뒤 K를 반환한다.

요약 내용은 어떤 폼이 열렸고, 어떤 컨트롤과 상호작용했으며, 어떤 버튼을 눌렀고, 어떤 데이터를 입력했는지를 담는 generic한 진행 보고로, running balance를 명시적으로 계산하지는 않는다.
C4의 요약은 evict 이벤트당 정확히 1회의 추가 LLM 호출만 소비한다.

4개 실험 구성은 컨텍스트 관리의 점진적 진화를 나타낸다.
C1(GPT-5 only, 사용자 모델 없음): 동기 부여용 ablation으로, N=∞에 사용자 모델도 없어 비대화형 하네스에서 에이전트가 질문 후 멈추면 워크플로우가 통째로 stall된다.
C2(GPT-5 + 사용자 모델, Full Context): N=∞(eviction 없음), full conversation history 유지 — 표준 관행이자 컨텍스트 엔지니어링 비교의 primary 베이스라인.
C3(Last 5 Tool Calls): N=5, W=0 — 최근 5개 도구 쌍만 유지하고 이전은 요약 없이 폐기 (5개는 라인 1개당 2~3 도구 호출 기준 약 2회 itemization 사이클의 working memory).
C4(Last 5 + Summarization): N=5, W=3 — 5개 유지에 더해 pruning 경계 직전 3개 상호작용을 요약해 재삽입.
컨텍스트 엔지니어링 효과를 격리하기 위해 사용자 모델을 C2~C4에 걸쳐 동일하게 고정하고, 모든 주장은 C2→C3→C4 비교(컨텍스트 정책만 변화)에 근거한다.

---

## Key Contribution

1. 도구 사용 에이전트를 위한 semantic-level 컨텍스트 엔지니어링 정책을 형식화했다 — 도구 call/response 쌍 전체에 대한 recency 기반 가지치기 + evict된 쌍의 자동 요약 — 그리고 정확한 구성 알고리즘(Algorithm 1)을 제공해 토큰 단위 prompt 압축 및 외부 메모리 스토어와 명확히 구별했다.
2. 라이브 D365 F&O 환경의 50-task 호텔 경비 벤치마크에서, 사용자 모델을 고정한 채 recency pruning과 pruning+summarization이 complete itemization을 71.0% → 79.0% → 91.6%로 끌어올리면서 동시에 토큰을 62.7%, 런타임을 60.2% 절감함을 보였다.
3. run-to-run 분산, 95% 신뢰구간(Student's t 및 pooled Wilson score), effect-size 분석을 보고하고, pruning window N과 summary window W에 대한 민감도 분석을 제공했다.
4. 6개 모드 per-category 실패 taxonomy를 제시하고, 5개 경비 유형(3개 구조적 카테고리로 그룹화)에 걸친 일반화 증거와 두 번째 모델 패밀리(Claude Sonnet 4.5)에 대한 cross-model 증거를 제공했다.
5. 결과를 "보편적 일반화의 증명"이 아니라 "한 부류의 엔터프라이즈 도구 사용 워크플로우에 대한 강력한 증거"로 명시적으로 한정(scope)하며, 접근법의 범위와 한계를 솔직히 논의했다.

---

## Experiment & Results

벤치마크는 D365 F&O에서 MCP 프록시로 실행되는 50개 호텔 경비 itemization 태스크(4~23 라인, 중앙값 8)이며, 모든 수치는 5회 독립 실행 평균이고 메트릭은 에이전트 self-report가 아닌 저장된 폼 상태의 독립 read-back으로 계산된다.
C1(사용자 모델 없음)은 99.6% 태스크가 최소 1개 라인을 생성했음에도 complete itemization은 8.0%, 평균 금액 할당은 58.89%에 그쳐, GPT-5가 비대화형 하네스에서 워크플로우를 완료까지 끌고 가지 못함을 보였다.
C2(Full Context)는 complete itemization 71.0%, 평균 금액 92.03%, at-least-one 100%를 달성했으나 총 1,480,996 토큰(베이스라인 대비 +177.9%, input-to-output 비율 594.7:1)과 14.56시간(베이스라인의 4.73배)을 소비해 프로덕션에 비현실적이었다.
C3(Last 5)는 complete 79.0%(C2 대비 +8pp), 평균 96.92%로 성능이 오르면서 동시에 토큰을 535,274개(full 대비 −63.9%), 시간을 5.39시간(−63.0%)으로 줄여, 더 적은 컨텍스트가 성능·효율 양쪽에서 우월하다는 counterintuitive 결과를 냈다.
C4(Last 5 + Summarization)는 complete 91.6%, <10% remaining 99.6%, 평균 금액 99.64%로 전 메트릭 최고를 기록했고, 이는 C3 대비 +12.6pp, C2 대비 +20.6pp이며 토큰은 553,374개(C3 대비 +3.4%), 시간은 5.79시간(+7.4%)으로 오버헤드가 미미했다.
C2는 C4 대비 2.68배 토큰을 쓰면서도 더 낮은 완료율을 보여 "더 많은 컨텍스트가 성능을 보장하지 않음"을 입증했고, 전 구성에서 input 토큰이 총 토큰의 99.75~99.87%를 차지했다.
통계적으로 C4의 Wilson 95% CI [87.5, 94.4]는 C3 [73.5, 83.6]와 깨끗이 분리되며, run-level 표준편차도 C3 ±8.2 대비 C4 ±1.7로 가장 안정적이었다(요약이 pruning이 노출한 분산을 흡수).
실패 taxonomy에서 stale-state reference는 C2 34/73(47%)에서 C3 6/53(11%)로 급감했으나 premature termination이 9→18로 세 배 증가했고, C4는 이를 18→3으로 6배 줄여 전체 non-completion을 73→21(71% 감소)시켰다.
일반화 측면에서 C2→C4 향상은 Travel +19.0pp, Meals & Gifts +20.5pp로 Hotel(+20.6pp)과 일관됐고, 민감도 sweep은 N=5(N=3은 −5pt, N=10은 +1pt 미만에 토큰 +53%)와 W=3(W=5/full-hist는 토큰 4~11% 추가에 유의미한 정확도 향상 없음)이 두 곡선의 knee임을 확인했다.
Cross-model에서 Claude Sonnet 4.5는 사용자 모델 없이도 stall하지 않아 베이스라인이 이미 88.0%였고, pruning+summarization이 complete를 92.0%→94.5%로 ~5.6% 시간 프리미엄에 향상시켜 GPT-5의 +7.4%와 유사한 패턴을 보였다.

---

## Limitation

저자들이 명시한 한계로, 핵심 연구가 D365 F&O 호텔 경비 itemization이라는 단일 도메인에 집중되어 있고, 5개 경비 유형과 Sonnet 4.5로 확장했음에도 결과를 "보편적 일반화의 증명이 아닌 한 부류의 워크플로우에 대한 증거"로 명시적으로 한정한다.
(N=5, W=3) 운영점은 비교 명료성을 위해 고정한 값으로, 민감도 sweep이 robustness를 확인했으나 joint tuning이나 task별 adaptive window sizing은 미래 과제로 남겼다.
요약기가 단일 free-form LLM pass라서 structured/learned compressor(예: ACON)나 provider-native compaction API와의 head-to-head 비교가 아직 수행되지 않았다.
잔여 실패 모드(wrong subcategory mapping, duplicate/skipped, navigation error, residual mismatch)는 대체로 policy-invariant한 모델 수준 추론·tool-binding 오류로, 23-entry 호텔 subcategory 카탈로그의 near-synonym 모호성(Room tax vs. Non-Room tax 등)이 컨텍스트 정책과 무관하게 이를 증폭시켜 recency/요약 기반 정책의 headroom을 제한한다.
독자 관점에서는 importance-pruning(시간상 최근이 아니라 가장 최근에 참조된 N개 유지) 같은 대안이 정성적 논의에만 그쳤고, 사용자 모델(GPT-4.1)을 별도 LLM으로 두는 평가 설정이 실제 인간 사용자 환경과 다를 수 있다는 점, 그리고 8.4% 잔여 미완료율 때문에 프로덕션 배포 시 flagged 케이스에 대한 human review 유지가 여전히 필요하다는 실제적 영향이 남는다.

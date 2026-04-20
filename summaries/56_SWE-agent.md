# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

> **논문 정보**: John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press (Princeton University)
> **arXiv**: 2405.15793 (2024.05, NeurIPS 2024)
> **코드**: https://github.com/SWE-agent/SWE-agent

---

## Problem

LLM 에이전트가 실세계 소프트웨어 엔지니어링 태스크(GitHub 이슈 해결)를 자동화하려면 대규모 코드베이스를 탐색·검색·편집·테스트해야 한다.
그러나 기존 접근은 LM 에이전트를 Linux 쉘·Python 인터프리터 등 **인간 사용자를 위해 설계된 인터페이스**에 그대로 노출시킨다.
쉘 환경에서 LM 에이전트는 작은 파일 세그먼트를 편집할 단순 명령조차 신뢰성 있게 생성하지 못하며, 잘못된 편집에 대한 피드백이 부재해 오류가 누적된다.
비대화형 RAG 파이프라인(BM25 검색 → 단일 패치 생성)은 SWE-bench에서 최고 3.79% 해결률에 머물러 실용성이 부족하다.
Vim·VSCode에서 영감을 받은 iterative search 같은 "사람에게 친숙한" UI도 LM에게는 next/prev를 끝까지 반복 호출하게 만들어 예산과 컨텍스트를 소진시킨다.
SWE-bench 전체 2,294개 중 이전 SOTA가 풀 수 있었던 것은 87개에 불과했다.
HumanEvalFix Python에서도 GPT-4 직접 호출 기준 47.0%로 단순 버그 수정조차 한계가 뚜렷했다.
결과적으로 "LM 가중치 수정 없이, 인터페이스만으로" 에이전트 성능을 크게 끌어올릴 수 있는 체계적 설계 원칙이 부재했다.

---

## Motivation

HCI 연구는 좋은 UI가 인간 생산성을 크게 향상시킨다는 것을 오랫동안 입증해 왔다(Cooper et al.).
저자들은 "LM 에이전트는 자신만의 능력과 한계를 가진 새로운 카테고리의 최종 사용자"라고 규정한다.
IDE가 인간 개발자의 인지적 부담을 줄여주듯, LM 에이전트에게도 전용 **Agent-Computer Interface(ACI)**가 필요하다는 것이 핵심 주장이다.
LM의 특성—긴 문서에서 중간 정보를 놓치기(Lost in the Middle), distracting context에 취약, 긴 bash 옵션을 잘 못 다룸—은 인간과 다르므로 인터페이스 설계 원칙도 달라야 한다.
저자는 이를 "HCI 유저 스터디와 유사한 체계적 행동 실험"으로 접근하여 ACI를 설계하고 평가한다.
즉 (1) 에이전트 궤적을 수동 검토해 어려움을 식별·개선하고, (2) 윈도우 크기·히스토리 처리·decoding temperature에 대한 그리드 서치를 수행한다.
이 접근은 LM 가중치를 건드리지 않고 인터페이스 레이어만으로 downstream 성능을 개선할 수 있음을 보이는 것이 목표다.
더 나아가 ACI 연구는 HCI와 심리학의 시너지처럼, LM의 본질에 대한 통찰을 주는 학문적 도구가 될 수 있다고 제안한다.

---

## Method

SWE-agent는 LM과 ACI의 결합으로 구성되며, 각 턴마다 ReAct 방식으로 Thought + Action을 생성하고 환경 피드백을 받는다.

1. **ACI 설계 원칙 1 — 단순한 액션**: bash의 수십 옵션 대신 소수 옵션·간결 문서를 갖는 커스텀 명령을 정의하여 demonstration/fine-tuning 필요성을 줄인다.
2. **ACI 설계 원칙 2 — 간결·효율적 액션**: 파일 탐색·편집 같은 중요 연산을 다중 턴 합성이 아니라 단일 액션으로 통합한다.
3. **ACI 설계 원칙 3 — 풍부하되 간결한 피드백**: 편집 후 업데이트된 파일 뷰를 즉시 보여주되 불필요한 세부는 제거한다.
4. **ACI 설계 원칙 4 — 가드레일로 오류 전파 방지**: code linter를 edit에 통합해 잘못된 편집을 즉시 감지·폐기하고 재시도를 유도한다.
5. **Search/Navigation 컴포넌트**: `search_dir`, `search_file`, `find_file` 세 가지를 제공하며, 결과가 임계치 초과 시 요약 + "더 구체적인 쿼리로 재시도" 힌트를 반환한다(Summarized Search).
6. **File Viewer**: `open` 후 `scroll_up/scroll_down/goto`로 100줄 윈도우를 이동하고, 전체 경로·총 라인 수·위아래 생략 라인 수·라인 번호 접두를 일관된 포맷으로 표시한다.
7. **File Editor**: `edit [start]:[end]` 명령이 시작/끝 라인·교체 텍스트 3인수를 받아 다중 라인 블록 교체를 단일 턴에 수행하고, 편집 직후 자동으로 업데이트된 뷰를 반환한다.
8. **Linting 가드레일**: edit 적용 전 linter를 실행해 구문 오류가 새로 도입되면 에러 + 주변 스니펫을 보여주고 편집을 폐기하여 재시도시킨다.
9. **Context Management**: 시스템 프롬프트, 커스텀 명령 문서, demonstration, ReAct 형식 지침을 공급하고 malformed generation은 에러 메시지로 재생성을 유도한다.
10. **History Processor**: 히스토리 중 최근 5개 observation만 펼쳐서 유지하고 나머지는 축약하여 context window 부담을 줄인다(Last 5 Obs. 기본값).
11. **실행 환경**: Linux 쉘 위에 ACI를 쌓아 일반 Linux 유틸리티(`python`, `pytest` 등 실행 포함)도 함께 사용 가능하다.
12. **제출 메커니즘**: 에이전트가 `submit`을 호출하거나 인스턴스당 $4 예산 초과 시 현재 코드베이스 상태에서 자동으로 diff 패치를 생성·제출한다.
13. **설정 탐색**: 개발 세트에서 윈도우 크기, 히스토리 길이, temperature 등 하이퍼파라미터를 그리드 서치하여 최종 구성을 확정했다.

---

## Key Contribution

1. **ACI 개념의 정식화**: 인간용 UI와 구분되는 "LM 에이전트용 인터페이스" 개념을 명명·정의하고 4대 설계 원칙을 제시했다.
2. **SWE-bench SOTA 달성**: 비대화형 RAG 최고 3.79% 대비 3.3배인 12.47%를 GPT-4 Turbo로 달성하고 Lite에서 18.00%를 기록했다.
3. **Shell-only 대비 대폭 개선**: 동일 LM(GPT-4 Turbo) 기준 Shell-only 11.00% → SWE-agent 18.00%로 +7.0%p, 상대 64% 향상을 ablation으로 입증했다.
4. **HumanEvalFix 압도적 갱신**: Python 87.7%, JS 89.7%, Java 87.9%로 기존 최고 WaveCoder-DS-6.7B(각 57.9/52.4/57.3)를 30%p 이상 상회했다.
5. **LM 이식성 검증**: 동일 ACI를 Claude 3 Opus에도 적용해 Full 10.46%, Lite 13.00%를 달성하여 GPT-4 전용 설계가 아님을 보였다.
6. **오픈소스 공개**: 코드, 데이터, 리더보드를 swe-agent.com에 공개하여 후속 ACI 연구의 기반을 제공했다.
7. **행동 분석 프레임워크 제공**: 286개 성공 궤적과 248개 실패 궤적을 수치화·범주화하여 에이전트가 실패하는 구체적 양상을 실증했다.

---

## Experiment

벤치마크는 SWE-bench Full 2,294개, SWE-bench Lite 300개, HumanEvalFix(Python/JS/Java) 3종이다.
LM은 GPT-4 Turbo(gpt-4-1106-preview, 128k context)와 Claude 3 Opus(claude-3-opus-20240229, 200k context)를 주로 사용하고 Llama 3·DeepSeek Coder는 context window 등 이유로 하위 성능이라 제외했다.
메인 메트릭은 pass@1 해결률(% Resolved)과 resolved 인스턴스 평균 API 비용($ Avg. Cost)이며 인스턴스당 $4 예산 초과 시 자동 제출한다.
메인 결과: SWE-agent w/ GPT-4 Turbo가 Full 12.47%(286/2,294, $1.59), Lite 18.00%(54/300, $1.67)를 달성했다.
Claude 3 Opus 버전은 Full 10.46%($2.59), Lite 13.00%($2.18)로 동일 ACI의 LM 이식성을 확인했다.
RAG 베이스라인(Claude 3 Opus)은 Full 3.79%·Lite 4.33%($0.25)에 그쳐, SWE-agent Lite가 비용 6.7배·해결률 4.2배 우위였다.
Shell-only + GPT-4 Turbo는 Lite 11.00%($1.46), demonstration 제거 시 7.33%($0.79)로 떨어져 demo 중요성도 확인된다.
HumanEvalFix에서 SWE-agent w/ GPT-4 Turbo는 Python 87.7%, JS 89.7%, Java 87.9%로 직전 최고 WaveCoder-DS-6.7B(57.9/52.4/57.3)를 크게 앞섰다.
ACI Ablation(Lite, 기본 18.0%): edit w/o linting 15.0%(-3.0), No edit 10.3%(-7.7)로 linting 가드레일과 edit 액션의 기여가 가장 크다.
검색 ablation: Iterative search 12.0%(-6.0)는 심지어 No search 15.7%(-2.3)보다도 낮아, 인간친화적 UI가 오히려 해로울 수 있음을 보였다.
파일 뷰어 창 크기: 30 lines 14.3%(-3.7), Full file 12.7%(-5.3)로 100-line 윈도우가 최적점이었다.
컨텍스트 관리: Full history 15.0%(-3.0), w/o demo 16.3%(-1.7)로 최근 5 observation만 유지하는 전략이 우월했다.
궤적 통계: 성공은 중앙값 12 스텝·$1.21로 빠르게 끝나는 반면 실패는 평균 21 스텝·$2.52로 느리게 끝나며, resolved 인스턴스의 93.0%가 예산 소진 전에 제출됐다.
실패 모드 분포(n=248, GPT-4o 자동 라벨링, 저자 일치도 87%): Incorrect Implementation 39.9%, Failed to Recover from Edit 23.4%, Failed to Find Edit Location 12.9%, Overly Specific 12.1%, Relevant File 못 찾음 4.8%, Gave Up 2.4%, Can't Reproduce 2.4%, Ran Out of Time 2.0%.
편집 신뢰성: 전체 궤적 중 51.7%(1,185/2,294)가 1회 이상 linting 실패를 겪었으며, 첫 시도 성공률 90.5%, 1회 실패 후 회복 57.2%로 실패가 누적될수록 회복이 급감했다.
Pass@k(6 runs, Lite): k=1 약 18%에서 k=6 약 30% 중반대로 증가해 variance와 탐색 여지가 상당함을 확인했다.

---

## Limitation

저자 지적 1 — **잘못된 구현 실패(52.0%)**: 전체 실패의 절반이 Incorrect/Overly Specific Implementation으로, ACI를 아무리 개선해도 LM의 코드 추론 능력 한계는 그대로 노출된다.
저자 지적 2 — **편집 회복 실패(23.4%)**: linting으로 오류를 알려줘도 에이전트가 연쇄적 실패 후 회복하지 못해, 가드레일이 만능은 아니다.
저자 지적 3 — **예산 한계의 본질적 제약**: resolved 인스턴스 93%가 예산 소진 전 끝내므로 단순히 $4 → 더 큰 예산을 준다고 성능이 크게 오르지 않을 것으로 저자 스스로 예상한다.
저자 지적 4 — **LM별 성능 편차**: Llama 3(8k context), 소형 DeepSeek Coder 등 많은 오픈소스 모델은 context window와 일반 추론 부족으로 SWE-agent 설정에서 subpar였다.
독자 관점 1 — **SE 도메인 국한**: ACI 설계가 search/view/edit에 맞춰져 있어 GUI 태스크·웹 내비게이션·멀티모달 컴퓨터 제어로의 일반화는 별도 설계가 필요하다.
독자 관점 2 — **LM 가중치 불변 가정**: LM을 고정하고 인터페이스만 조정하는 접근은 강력하지만, fine-tuning과 결합했을 때의 상호작용은 본 논문에서 다루지 않는다.
독자 관점 3 — **비용 대비 절대 성능**: Full 12.47%는 여전히 과반에 한참 못 미치며 실무 투입에는 부족하고, 인스턴스당 $1.59~$2.59의 추론 비용도 스케일업의 병목이다.
독자 관점 4 — **평가 인프라 편향**: SWE-bench 12개 Python 리포지토리와 unit test 기반 평가에 국한되어, 대규모 엔터프라이즈 코드베이스·다언어·비테스트 태스크에 대한 외적 타당성은 검증이 필요하다.

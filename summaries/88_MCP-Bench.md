# 88. MCP-Bench: Benchmarking Tool-Using LLM Agents with Complex Real-World Tasks via MCP Servers

> 📄 **저자**: Zhenting Wang, Qi Chang, Hemani Patel, Shashank Biju, Cheng-En Wu, Quan Liu, Aolin Ding, Alireza Rezazadeh, Ankit Shah, Yujia Bao, Eugene Siow (Center for Advanced AI, Accenture / UC Berkeley)
> 📚 **학회/발표 기관**: arXiv preprint (Accenture)
> 📅 **발표 날짜**: 2025.08
> 🔗 **arXiv**: https://arxiv.org/abs/2508.20453
> 💻 **코드**: https://github.com/Accenture/mcp-bench

---

## Problem

기존 tool-use 벤치마크는 실제 에이전트가 마주하는 복잡성을 제대로 반영하지 못한다.
ToolBench, BFCL v3 같은 초기 벤치마크는 수많은 API를 모았지만, 이 API들은 본질적으로 고립된 기능(isolated functionality)을 위해 설계되어 입출력이 자연스럽게 연결되지 않는다.
그 결과 태스크가 몇 단계짜리 도구 호출로 축소되거나, 인위적으로 꿰맞춘(artificially stitched) 파이프라인에 의존하게 된다.
τ-Bench는 인터페이스가 호환되는 소수 API를 골라 더 깔끔한 조합을 가능케 했지만, 2개 도메인·28개 도구로 커버리지가 좁아 멀티 도메인 워크플로의 복잡성을 담지 못한다.
MCP-RADAR, MCPEval 등 MCP 기반 최신 벤치마크조차 서버 몇 개·도구 수십 개에 그쳐 워크플로가 "단일 검색 후 요약" 수준으로 짧다.
또한 기존 벤치마크들은 태스크에 도구 이름이나 실행 단계를 명시적으로 제공하므로, 지시가 불충분할 때 어떤 도구가 적합한지 추론하는 능력(fuzzy instruction 하 계획 능력)을 전혀 시험하지 못한다.

---

## Motivation

실제 LLM 에이전트는 여행·헬스케어·금융 등에서 여러 도구를 연쇄 호출하고, 구조화된 출력을 추론하며, 상호 의존적 연산을 조율해야 한다.
이런 능력을 평가하려면 합성·정적 API가 아니라, 함께 작동하도록 설계된 상보적(complementary) 도구 집합을 가진 실제 서버 생태계가 필요하다는 것이 핵심 직관이다.
MCP(Model Context Protocol)는 서버 간 일관된 호출 스키마를 표준으로 제공하므로, 하나의 서버 안에서 자연스러운 의존성 사슬(intra-server dependency chain)과 서버를 넘나드는 멀티홉 워크플로(cross-server)를 동시에 구성할 수 있다.
예컨대 과학 계산 서버는 데이터 로딩·행렬 연산·시각화 도구를 통합 제공하여 진짜 도구 간 결합을 만들어낸다.
저자들은 또한 멀티 목표 태스크(항공·호텔·교통 동시 조율), 중간 도구 출력을 인용하는 근거 기반 추론(information grounding), 금융 도구와 뉴스 소스를 결합하는 cross-domain orchestration 같은 시나리오가 기존 벤치마크에서 빠져 있음을 관찰했다.
이를 종합적으로 평가할 표준적이고 확장 가능한 플랫폼이 필요하다는 것이 MCP-Bench의 동기다.

---

## Method

MCP-Bench는 라이브 MCP 서버 생태계 위에 자동 태스크 합성과 다면적 평가를 결합한 벤치마크다.

1. **MCP 서버 수집**: 11개 기능 도메인에 걸친 28개의 production급 라이브 MCP 서버를 모아, 총 250개의 구조화 도구를 노출한다.
도메인 비중은 Media & Entertainment와 Research & Knowledge가 각 14.3%로 가장 크고, Finance·Science·Software Development가 각 10.7%다.
서버당 도구 수는 단일 도구 서버(Call for Papers, FruityVice 등)부터 BioMCP(35개), Scientific Computing(26개), Medical Calculator(22개)까지 폭넓다.

2. **POMDP 형식화**: 에이전트를 (S,A,O,T,R,U,Σ) 튜플의 POMDP로 형식화하며, Σ는 사용 가능한 MCP 서버 집합이다.
도구 호출은 ⟨서버, 도구이름, 파라미터⟩ 형태의 구조화된 액션으로 표현된다.

3. **멀티턴 실행(Algorithm 1)**: 각 라운드 t에서 계획 정책 π_plan이 도구 계획을 생성하고, 실행 정책 π_exec이 도구를 호출한 뒤, 압축 정책 π_compress가 관측 결과를 요약한다.
이 압축 단계는 일부 도구가 매우 긴 출력을 반환할 때 컨텍스트 윈도우 폭주를 막는 핵심 장치다.
종료 신호가 나오거나 최대 T_max=20 라운드에 도달할 때까지 반복하고, 전체 trajectory를 본 후 π_final이 최종 답을 생성한다.

4. **태스크 합성 — 의존성 사슬 발견**: 도구의 입출력 시그니처를 분석해 한 도구의 출력이 다음 도구의 입력으로 흐르는 의존성 사슬을 찾고, 이를 자연어 지시로 번역한다.
inherent 의존성과 scenario-based 의존성을 모두 분석하며, 멀티 서버 설정에서는 cross-server 의존성을 강조해 선형·병렬·하이브리드 구조 패턴을 만든다.
태스크 합성 LLM으로는 o4-mini를 사용한다.

5. **자동 품질 필터링**: 생성된 각 태스크를 2차원으로 평가한다 — Solvability(사용 가능 도구로 완수 가능한가)와 Practical utility(실제 사용자 니즈를 반영하는가).
임계값(solvability 9.0/10, utility 5.0/10)에 미달하면 폐기하여 벤치마크 품질을 유지한다.

6. **태스크 퍼징(fuzzing)**: 통과한 태스크를 명시적 도구 이름·실행 단계를 제거한 fuzzy·instruction-minimal 변형으로 재작성한다.
단, 과학 계산·단위 변환처럼 정밀 입력이 필요한 도메인에서는 모든 수치·구체 파라미터를 보존하여 수학적 풀이 가능성을 유지한다.

7. **fuzzy 환경 강화**: 모든 태스크에 10개의 distractor 서버를 붙여 인스턴스당 100개 이상의 추가 도구를 노출, 검색 정밀도를 stress-test한다.

8. **규칙 기반 평가**: 실행 trace에서 4개 차원을 측정한다 — Tool Name Validity Rate(존재하는 도구만 호출했는가), Schema Compliance Rate(입력 스키마 준수), Execution Success Rate(런타임 성공), Dependency Compliance(의존성 순서).

9. **LLM-as-a-Judge 평가**: o4-mini 판정자가 세 축을 루브릭으로 채점한다 — Task Completion(task fulfillment, information grounding), Tool Usage(tool appropriateness, parameter accuracy), Planning Effectiveness(dependency awareness, parallelism & efficiency).
각 sub-dimension은 1~10점으로 매겨 평균 후 [0,1]로 정규화한다.

10. **Prompt Shuffling & Score Averaging**: 루브릭 축·하위 차원의 순서를 무작위로 5회 섞어 독립 채점한 뒤 평균내어, 판정자가 프롬프트 순서에 민감해지는 편향을 완화한다.

---

## Key Contribution

1. 28개 라이브 MCP 서버에 걸친 250개 도구를 노출하여 intra-server 의존성 사슬과 cross-server orchestration을 동시에 가능케 한 현실적 tool-use 벤치마크를 제시했다.
2. 의존성 사슬 발견 → 품질 필터링 → 태스크 퍼징의 구조화된 합성 파이프라인으로, 실제 도구 의미에 grounding된 복잡·멀티홉 태스크의 fuzzy 지시를 자동 생성한다.
3. 규칙 기반 실행 검사와 루브릭 기반 LLM-as-a-Judge를 결합한 견고한 평가 프레임워크로, 실행 정확성과 전략적 추론을 종합 평가한다.
4. 20개 최신 LLM을 104개 도전적 태스크로 평가한 대규모 실증 연구를 통해, 현실적·복잡 tool-use 시나리오에서 에이전트 능력의 지속적 약점을 드러냈다.
5. 고립된 API 벤치마크와 실제 생태계 사이의 간극을 메워, agentic 추론·도구 사용 능력을 엄밀히 평가하는 표준적·확장 가능 플랫폼을 제공한다.

---

## Experiment & Results

20개 대표 LLM을 평가했다 — llama-3-1-8b/70b/3-3-70b/3-2-90b-vision, mistral-small-2503, nova-micro-v1, gpt-4o-mini/gpt-4o, gemma-3-27b, gemini-2.5-flash-lite/2.5-pro, kimi-k2, gpt-oss-20b/120b, qwen3-30b/235b, glm-4.5, claude-sonnet-4, o3, gpt-5.
저수준 스키마 능력은 이미 수렴했다 — o3·gpt-5·gpt-oss-120b·qwen3-235b·gpt-4o 모두 schema compliance와 valid tool naming에서 98%를 넘겼고, 중간 규모 모델도 95% 이상을 달성했다.
종합 점수(Overall Score)는 gpt-5가 0.749로 최고, o3가 0.715, gpt-oss-120b가 0.692로 뒤를 이었다.
반면 소형 모델 llama-3-1-8b-instruct는 0.428에 그쳐, 실행 성공률은 적절했음에도 dependency awareness·parallelism에서 크게 뒤처졌다.
가장 큰 격차는 planning effectiveness에서 나타났다 — gpt-5의 dependency awareness는 평균 0.649(본문 서술 기준 0.76), 약한 모델들은 0.30을 넘기 어려웠다.
멀티 서버 설정에서 약한 모델은 성능이 눈에 띄게 하락했다 — llama-3-1-8b는 단일 서버 0.438에서 멀티 서버 0.415로, nova-micro-v1은 0.520에서 0.471로 떨어졌다.
반면 gpt-5는 양쪽 설정에서 약 0.75로 안정적이었고(단일 0.749, 멀티 0.750), o3와 qwen3-235b는 0.70 이상을 유지해, 진짜 차별자는 실행 품질이 아니라 스케일링에 대한 견고성임을 보였다.
실행 비용도 큰 차이를 보였다 — llama-3-1-8b는 태스크당 평균 17.3 라운드·155.6 도구 호출을 소비한 반면, qwen3-235b는 4.0 라운드·16.4 호출, o3는 6.3 라운드·28.3 호출로 훨씬 효율적이었다.
gpt-5는 9.2 라운드·78.9 호출로 깊은 추론과 통제된 호출 예산의 중간 지점을 택했다.
어블레이션에서 prompt shuffling+score averaging은 모델 간 변동계수(CV)를 16.8%→15.1%로 낮추고, 인간 동의 점수를 1.24→1.43(만점 2)로 높여 판정 안정성을 개선했다.

---

## Limitation

저자들은 품질 임계값(solvability 9.0, utility 5.0)을 높게 설정해 벤치마크 무결성을 확보하는 대신 태스크 수가 줄어드는(reduced quantity) 트레이드오프를 명시한다.
최종 태스크가 104개(단일 서버 56, 2서버 30, 3서버 18)로 비교적 적어, 도메인·난이도별 통계적 일반화에는 한계가 있다.
태스크 합성과 LLM-as-a-Judge가 모두 단일 모델(o4-mini)에 의존하므로, 합성 편향과 판정 편향이 평가에 전파될 수 있다는 점은 독자 관점의 우려다.
라이브 MCP 서버에 의존하기 때문에 서버 가용성·API 변경·네트워크 실패에 따라 결과 재현성이 흔들릴 수 있고, 실제로 execution success rate가 100%가 아닌 점이 이를 시사한다.
또한 정답 trajectory가 고정된 ground truth가 아니라 루브릭 기반 판정이라, 점수의 절대값보다 모델 간 상대 비교에 더 적합하다는 한계가 있다.
parallelism efficiency 점수가 최상위 모델(gpt-5 0.339)에서도 낮게 머무는데, 이것이 모델의 한계인지 평가 메트릭의 보수성인지는 추가 검증이 필요하다.

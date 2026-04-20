# AgentSquare: Automatic LLM Agent Search in Modular Design Space

> **논문 정보**: Yu Shang, Yu Li, Keyu Zhao, Likai Ma, Jiahe Liu, Fengli Xu, Yong Li (Tsinghua University)
> **arXiv**: 2410.06153v3 (2025.02.27) | **학회**: -
> **코드**: https://github.com/tsinghua-fib-lab/AgentSquare

---

## Problem

현재 LLM 에이전트 시스템 설계는 대부분 수작업(hand-crafted)에 의존하며, 특정 태스크에 맞춰 전문가가 직접 아키텍처를 설계해야 한다.

이러한 태스크 특화 설계는 새로운 태스크에 대한 적응력이 크게 떨어지고, 설계 비용과 전문 지식 의존도가 높다.

기존 자동 최적화 연구인 OPRO와 Promptbreeder는 프롬프트 수준의 rewriting에 국한되어 탐색 공간이 제한적이다.

ADAS와 같은 코드 공간 전체 검색 방식은 유연하지만, 기존 연구에서 검증된 모듈들을 명시적으로 재조합하는 능력이 부족하다.

서로 다른 코드베이스에 분산된 에이전트 모듈들의 강점을 체계적으로 결합할 수 있는 표준화된 프레임워크가 부재하다.

LangChain, AutoGPT 등 기존 LLM 워크플로우 프레임워크는 operation-level 컴포넌트만 제공할 뿐 module-level 검색을 지원하지 않는다.

에이전트 평가 비용이 매우 높아 GPT-4o 기반 ALFWorld 평가 1회에 약 $60이 소요되어, 대규모 검색이 경제적으로 지속 불가능하다.

멀티 에이전트 시스템 최적화 연구들은 역할 분배와 상호작용 패턴에 초점을 두어 단일 에이전트의 모듈 수준 최적화 문제와는 직교적인 접근이다.

---

## Motivation

LLM 에이전트 연구 커뮤니티에서 CoT, ToT, Voyager, Generative Agents, DEPS 등 다양한 성공적 모듈이 개별적으로 개발되었으나, 이들을 표준화된 인터페이스로 통합하여 재조합할 수 있는 플랫폼이 없다.

기존 에이전트 아키텍처를 Planning, Reasoning, Tool Use, Memory 네 가지 기본 모듈로 추상화하면, 모듈 간 조합을 통해 방대한 설계 공간(1,050개 이상의 조합)을 체계적으로 탐색할 수 있다.

모듈 수준의 표준화된 IO 인터페이스를 정의하면, 서로 다른 연구에서 나온 모듈들을 플러그인 방식으로 쉽게 통합하고 확장할 수 있다.

프롬프트 수준 최적화만으로는 초기 상태의 이웃 영역에 탐색이 한정되어 지역 최적해에 갇히기 쉬우므로, 모듈 재조합이라는 더 넓은 탐색 메커니즘이 필요하다.

반대로 기존 모듈 조합만 탐색하면 상한선이 제한되므로, 프로그램 수준의 새로운 모듈 생성(모듈 진화)이 보완되어야 한다.

AutoML의 Neural Architecture Search에서 영감을 받아, 에이전트 아키텍처에도 유사한 자동 검색 패러다임을 적용할 수 있다.

평가 비용 문제는 in-context surrogate 모델로 후보를 사전 필터링하면 크게 완화될 수 있으며, 이는 NAS의 performance predictor와 유사한 접근이다.

표준화된 모듈 설계 공간은 연구 공동체가 축적한 에이전트 설계 자산을 재활용하고 해석 가능한 설계 인사이트를 도출하는 플랫폼이 될 수 있다.

---

## Method

1. **MoLAS 문제 정의**: LLM 에이전트 A = (P, R, T, M)로 정의하며, P(Planning), R(Reasoning), T(Tool Use), M(Memory) 네 모듈의 최적 조합을 찾는 최적화 문제 arg max Eval_d(P, R, T, M)로 공식화한다.

2. **문헌 리뷰 기반 설계 공간 구축**: NeurIPS, ICML, ICLR 최근 3년 논문을 체계적으로 리뷰하여 "LLM", "Agent", "Large Language Model" 키워드의 16개 인기 에이전트를 4개 모듈 카테고리로 분류.

3. **표준화된 IO 인터페이스 정의**: Planning은 (task type, task description, feedback)→plan, Reasoning은 (task description, tool_instruction, feedback)→reasoning result, Tool Use는 (task description, tooluse_instruction, feedback)→tool response, Memory는 current situation→add or retrieve 구조로 통일. 총 1,050개 이상의 조합 공간 확보.

4. **에이전트 워크플로우**: 태스크 d 수신 → Planning이 서브태스크 {s1,...,sn}로 분할 → Reasoning이 각 si를 순차 해결 → 내부 지식 한계 시 Tool Use 호출 → Memory가 관찰·경험을 동적으로 write/retrieve → 환경 상호작용 → 피드백 기반 재계획의 trial-and-error 루프.

5. **초기화(Initialization)**: seed 에이전트와 실제 성능 v로 구성된 글로벌 experience pool E = {(P, R, T, M, v)} 구축. 모듈 풀은 seed 에이전트에서 추출한 표준화 모듈로 초기화.

6. **모듈 재조합(Module Recombination)**: self-adaptive proposer LLM π_θ가 초기 에이전트 A^0_r = (P0, R0, T0, M0), 태스크 설명 d, 모듈 풀, 경험 풀을 입력받아 A_r = π_θ(A^0_r, d, N, P, R, T, M, E)로 N개의 자식 에이전트를 제안 — 한 번에 한 모듈만 대체하는 방식.

7. **모듈 진화(Module Evolution)**: FunSearch에서 영감을 받은 evolutionary meta-prompt를 사용하는 module-programming LLM π_ξ가 프로그램 수준에서 새로운 모듈을 생성. A_e = π_ξ(A^0_e, d, N, P, R, T, M, E)로 새 모듈을 생성하여 모듈 풀에 추가하고, 각 새 모듈이 초기 에이전트를 개별적으로 mutate.

8. **실제 환경 테스트**: 모듈 진화로 생성된 자식 에이전트는 경험 풀에 없는 신규 모듈이므로 반드시 실제 태스크 환경에서 평가하여 성능을 측정하고 experience pool E에 업데이트.

9. **성능 예측기(Performance Predictor)**: in-context surrogate model π_p가 v' = π_p(A', d, P, R, T, M, E)로 과거 조합 성능을 바탕으로 신규 에이전트 성능을 예측. 실제 평가의 약 0.025% 비용으로 신뢰할 수 있는 추정 제공.

10. **예측기의 사용 범위**: 모듈 재조합 단계에서만 예측기를 사용하여 비유망 후보를 스킵. 모듈 진화 단계는 신규 모듈이 과거 데이터에 없으므로 실제 평가를 유지.

11. **에피소드 교대 구조**: 진화(Evolution)와 재조합(Recombination)이 에피소드 단위로 교대로 실행되며, 각 단계의 최고 성능 에이전트가 다음 단계의 초기 에이전트가 되는 순환 구조.

12. **검색 종료 조건**: 5회 연속 반복 동안 성능 개선이 없으면 검색 종료. 공정한 비교를 위해 모든 기준선과 동일한 few-shot 예제 수 사용.

13. **ADAS 코드 재활용**: 모듈 진화의 최적화 절차는 ADAS의 오픈소스 코드 일부를 재활용하여 구현, 공정한 비교와 재현성 확보.

---

## Key Contribution

1. **MoLAS 문제 최초 정의**: LLM 에이전트를 4개 모듈(Planning, Reasoning, Tool Use, Memory)의 조합으로 추상화하고 표준화된 IO 인터페이스 기반의 모듈형 설계 공간을 최초로 제안.

2. **1,050개 이상의 조합 공간**: 16개 인기 에이전트에서 추출한 모듈로 구성된 확장 가능한 모듈 풀과 설계 공간을 제공, 커뮤니티의 집단적 연구 결과를 통합하는 플랫폼 역할.

3. **AgentSquare 이중 메커니즘 프레임워크**: 모듈 진화(코드 수준 새 모듈 생성)와 모듈 재조합(기존 모듈 간 전략적 결합)을 결합하여 제한적 프롬프트 rewriting과 비구조적 코드 검색의 한계를 동시에 극복.

4. **In-context 성능 예측기**: 실제 평가 비용의 0.025% 수준으로 후보 에이전트의 성능을 예측하여 대규모 검색을 경제적으로 지속 가능하게 함.

5. **6개 벤치마크 SOTA**: Webshop, ALFWorld, SciWorld, M3Tool, TravelPlanner, PDDL에서 인간 설계 에이전트 대비 평균 17.2% 성능 향상, 다른 자동 검색 방법 대비 평균 약 7.4% 향상.

6. **해석 가능한 설계 인사이트**: 검색된 에이전트(예: ALFWorld의 TD Planning + SF-ToT Reasoning + Generative Agents Memory)가 왜 효과적인지 인간 해석 가능한 설계 원칙을 자동 도출.

7. **ADAS 대비 효율성 우위**: 동일 토큰 예산 하에 6개 중 5개 태스크에서 ADAS를 능가, 모듈형 검색이 비구조적 코드 검색보다 효율적임을 실증.

---

## Experiment & Results

- **벤치마크 구성**: Webshop(웹), ALFWorld(체화), SciWorld(체화), M3Tool(도구), TravelPlanner(도구), PDDL(게임) — 4개 도메인 6개 태스크로 다양한 시나리오 커버.

- **기반 모델**: GPT-4o 및 GPT-3.5-turbo-0125 두 모델로 검증.

- **GPT-4o 기준 AgentSquare 성능**: Webshop 0.607, ALFWorld 0.695, SciWorld 0.781, M3Tool 0.524, TravelPlanner 0.583, PDDL 0.669.

- **인간 설계 최고 대비 개선율**: Webshop +14.1%, ALFWorld +26.1%, SciWorld +20.5%, M3Tool +30.6%, TravelPlanner +6.0%, PDDL +6.0%, 전체 평균 **17.2%** 향상.

- **다른 검색 방법 대비 개선율**: Webshop +8.4%, ALFWorld +8.1%, SciWorld +11.0%, M3Tool +12.8%, TravelPlanner +2.5%, PDDL +1.4% — 모든 태스크에서 우위.

- **핵심 인간 설계 기준 성능(ALFWorld)**: CoT 0.405, Self-refine 0.567, ToT 0.437, HuggingGPT 0.481, Voyager 0.425, Generative Agents 0.477, DEPS 0.459, OPENAGI 0.510.

- **검색 기준 방법 성능(ALFWorld)**: Random 0.620, Bayesian 0.634, OPRO 0.380, ADAS 0.543 — AgentSquare 0.695가 모두 상회.

- **ADAS 대비(Webshop)**: AgentSquare 0.607 vs ADAS 0.521, 동일 토큰 예산에서 17% 우위.

- **Ablation (GPT-4o)**: 모듈 진화 제거 시 ALFWorld 0.695→0.649, SciWorld 0.781→0.736, PDDL 0.669→0.614로 하락.

- **Ablation (재조합 제거)**: ALFWorld 0.695→0.616, TravelPlanner 0.583→0.280, M3Tool 0.524→0.481로 급락 — 재조합 제거 영향이 진화 제거보다 큼.

- **성능 예측기 검증**: 6개 태스크 모두에서 예측 성능과 실제 성능의 높은 상관관계 확인. ALFWorld GPT-4o에서 실제 평가 비용의 0.025%만 소요.

- **검색 궤적**: ALFWorld에서 15회 반복, Webshop에서 18회 반복 내 안정적 수렴. Random/Bayesian은 방향성 없이 정체, OPRO는 수정 공간 제한으로 미미한 개선.

- **발견된 최고 에이전트(ALFWorld)**: Planning=TD(신규), Reasoning=SF-ToT(신규), Memory=Generative Agents(기존) 조합 — 신규 모듈과 기존 모듈의 혼합.

- **발견된 최고 에이전트(Webshop)**: Planning=IO, Reasoning=HTSS(신규), Memory=Dilu — 태스크별 적응적 모듈 선택.

- **비용 효율성**: AgentSquare 검색 결과 에이전트는 성능-비용 Pareto frontier의 최적점에 위치, 검색 비용은 일회성이며 모듈 재사용 가능.

---

## Limitation

설계 공간이 Planning/Reasoning/Tool Use/Memory 4개 모듈로 고정되어 멀티모달 인식, 안전성, 자기 반영 등의 모듈은 명시적으로 다루지 못한다.

단일 에이전트 최적화에 초점을 두어, 다중 에이전트 시스템의 역할 배분이나 상호작용 패턴 최적화와는 직교적 접근이어서 통합적 프레임워크가 부재하다.

검색 과정의 LLM API 호출 비용이 여전히 발생하며, 특히 모듈 진화 단계의 실제 환경 평가가 태스크당 수십~수백 달러 수준의 비용 부담을 유발한다.

성능 예측기가 모듈 재조합에서만 사용되고 신규 모듈이 포함되는 모듈 진화에는 적용할 수 없어, 진화 단계의 비용 절감에 구조적 한계가 있다.

초기 모듈 풀의 다양성과 품질이 검색 결과의 상한선에 영향을 주며, seed 에이전트 선정의 편향이 결과에 누적될 수 있다.

GPT-4o와 GPT-3.5에서만 실험하여 오픈소스 LLM(Llama, Qwen 등)이나 다른 상용 모델에서의 일반화 가능성은 미검증 상태이다.

6개 벤치마크가 주로 정형화된 평가 환경에 국한되어, 실제 오픈월드 장기 태스크(예: MineCraft 장시간 생존)나 산업 응용에서의 효과는 추가 검증이 필요하다.

모듈 간 인터페이스가 고정되어 있어 모듈 간 고도 결합(tight coupling)이 필요한 최신 아키텍처(예: 메모리-계획의 동적 통합)를 완전히 표현하지 못하는 표현력의 한계가 존재한다.

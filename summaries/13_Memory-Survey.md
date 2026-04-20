# Memory in the Age of AI Agents: A Survey — Forms, Functions and Dynamics

> **논문 정보**: Yuyang Hu, Shichun Liu, Yanwei Yue, Guibin Zhang 외 다수 (NUS, Renmin Univ., Fudan Univ., PKU, NTU, Oxford 등 15개 기관)
> **arXiv**: 2512.13564v2 (2026.01.13) | **학회**: -
> **코드**: https://github.com/Shichun-Liu/Agent-Memory-Paper-List

---

## Problem

Foundation model 기반 에이전트가 급속히 발전하면서 메모리(memory)는 장기 추론, 지속적 적응, 복잡한 환경과의 효과적 상호작용을 지탱하는 핵심 역량으로 부상했다.

그러나 에이전트 메모리 연구 분야는 심각한 단편화(fragmentation) 문제를 겪고 있다.

"에이전트 메모리"라 칭하는 연구들이 동기, 구현, 가정, 평가 프로토콜에서 근본적으로 상이하며, 통합적 이해를 저해한다.

declarative, episodic, semantic, parametric memory 등 느슨하게 정의된 용어들이 산발적으로 확산되면서 개념적 혼란이 가중되었다.

기존의 장기/단기 메모리(long/short-term memory) 기반 분류법은 2025년에 폭증한 도구 증류(tool distillation), 메모리 보강 test-time scaling 등 새로운 방법론을 포괄하지 못한다.

특히 LLM memory, RAG, context engineering과 agent memory 사이의 경계가 모호하여 연구자들이 관련 개념을 혼동하는 사례가 빈번하다.

MemoryBank, MemGPT 같은 초기 "LLM memory" 시스템들이 실제로는 agentic 도전과제를 다루었음에도 잘못된 범주에 속해왔다.

이러한 개념적 파편화와 분류 체계의 공백을 해결하지 않고는 기존 연구를 체계화하거나 새로운 신흥 트렌드를 유의미하게 연결할 수 없다.

---

## Motivation

에이전트 메모리는 개인화 챗봇, 추천 시스템, 소셜 시뮬레이션, 금융 분석 등 실용적 도메인 전반에서 능동적 메모리 관리를 필수로 요구한다.

AGI 연구의 핵심 목표인 "환경 상호작용을 통한 지속적 자기 진화"는 근본적으로 에이전트 메모리에 뿌리를 둔다.

기존 서베이(Zhang et al., 2025s; Wu et al., 2025g)의 분류 체계는 급격한 방법론적 진보 이전에 수립되어 현재 연구 범위와 복잡성을 충분히 반영하지 못한다.

2025년에 등장한 tool distillation 기반 메모리 프레임워크와 memory-augmented test-time scaling 같은 신흥 방향은 기존 분류 스킴에서 저평가되어 있다.

따라서 본 서베이는 에이전트 메모리를 엄밀히 정의하고 LLM memory/RAG/context engineering과의 관계를 명확히 구분하고자 한다.

Forms-Functions-Dynamics 3축 통합 프레임워크를 제안하여 기존 정의를 화해시키고 신흥 트렌드를 연결하는 개념적 기반을 제공하는 것이 목표이다.

또한 미래 연구의 방향을 제시하기 위해 벤치마크·오픈소스 프레임워크 자원과 8대 프론티어 분석을 함께 제공한다.

궁극적으로 메모리를 "agentic intelligence의 first-class primitive"로 재정립하는 개념적 토대를 마련한다.

---

## Method — 분류 체계 (Taxonomy)

본 서베이는 에이전트 메모리를 Forms(형태), Functions(기능), Dynamics(동역학)의 3축으로 분석하는 통합 분류 체계를 제안한다.

### 1. Forms 축 — 메모리를 무엇이 담는가?

1. **Token-level Memory**: 외부에서 접근·수정·재구성 가능한 이산 단위(텍스트/비주얼/오디오 토큰)로 저장. 투명하고 편집 용이하여 가장 흔한 형태이며 연구량이 가장 많음.
2. **Flat Memory (1D)**: 유닛 간 위상이 없는 누적형. Chunk(Mem0, MemOS), Dialogue(MemGPT, MemoryBank), Experience pool(ExpeL, AWM, ReasoningBank), Summary(Think-in-Memory, RMM) 등.
3. **Planar Memory (2D)**: 단일 층 그래프/트리 구조. Tree(MemTree, TME), Graph(A-Mem, Mem0^g, M3-Agent, D-SMART) 등 관계형 의존성 포착.
4. **Hierarchical Memory (3D)**: 다층 상호 연결. Pyramid(G-Memory, CAM), Multi-Layer(HiAgent, HippoRAG, SGMem)로 수직 추상화와 cross-layer 추론 지원.
5. **Parametric Memory**: 모델 파라미터에 통계 패턴으로 인코딩. Internal(SFT/RL을 통한 가중치 업데이트, Retroformer, Early experience)과 External(어댑터·LoRA 등)로 구분.
6. **Latent Memory**: 모델 내부 hidden state·연속 표현. Generate(MemoryLLM, M+, MemGen이 새 잠재 표현 생성), Reuse(KV 캐시 재활용), Transform(잠재 표현 변환)의 3개 패러다임.
7. **Adaptation**: 세 형태 간의 상호 전환 및 결합 전략(예: 파라메트릭 내재화, latent→token 역사상).

### 2. Functions 축 — 에이전트에 메모리가 왜 필요한가?

8. **Factual Memory**: 사용자·환경에 대한 검증 가능한 사실 지식. User factual(선호·페르소나)과 Environment factual(외부 세계 상태)로 세분.
9. **Experiential Memory**: 과거 궤적에서 증류한 절차적 지식. Case-based(원시 trajectory 보존, Memento), Strategy-based(전이 가능 insight, ReasoningBank), Skill-based(실행 가능 코드·API, Voyager), Hybrid.
10. **Working Memory**: 단일 태스크 인스턴스 내 일시적 컨텍스트 관리. Single-turn(입력 압축)과 Multi-turn(상태 통합·계층적 폴딩, HiAgent, ReSum).

### 3. Dynamics 축 — 메모리가 어떻게 운용·진화하는가?

11. **Memory Formation F(M_t, φ_t)**: 원시 데이터를 지식 단위로 변환. Semantic summarization, Knowledge distillation, Structured construction, Latent representation, Parametric internalization의 5대 기법.
12. **Memory Evolution E(M_form)**: 새 메모리를 기존 저장소와 통합. Consolidation(로컬/클러스터/글로벌), Update(갈등 해결 + 모델 편집), Forgetting(시간/빈도/중요도 기반)의 3단계.
13. **Memory Retrieval R(M_t, o_t, Q)**: 검색 시점·의도 결정 → 쿼리 구성(분해/재작성) → 검색 전략(어휘/의미/그래프/하이브리드/생성적) → 후처리(재랭킹/필터링/집계).
14. **Formal agent-memory coupling**: 에이전트 정책 a_t = π_i(o_t, m_t, Q)에 메모리 신호 m_t를 주입하며, 세 연산자(F, E, R)의 호출 빈도·패턴이 다양한 시스템 거동을 산출.
15. **Boundary disambiguation**: LLM memory(내부 KV/아키텍처), RAG(정적 외부 지식), Context engineering(리소스 관리)과 대비하여, agent memory는 "지속적·자가 진화하는 인지 상태"로 정의.

---

## Key Contribution

1. **Forms-Functions-Dynamics 3축 통합 분류 체계** 수립으로 에이전트 메모리 연구의 파편화된 개념을 체계적으로 통합하고, LLM memory·RAG·context engineering과의 관계를 Venn diagram으로 명확히 시각화.
2. **기능 중심 세분화**: 장기/단기 이분법을 넘어 Factual/Experiential/Working 메모리의 세 갈래 기능 분류를 제안하고 각각을 carrier/form/task/optimization 4차원으로 교차 분석.
3. **형식적 수학 프레임워크**: 에이전트 메모리 시스템을 Formation(F), Evolution(E), Retrieval(R) 연산자로 수학적으로 형식화하여 다양한 시스템을 통일된 언어로 기술 가능하게 함.
4. **200편 이상 포괄적 커버리지**: 107페이지 규모로 200편 이상의 관련 논문을 분석하고 대표 벤치마크 15개 이상 및 오픈소스 프레임워크 14개를 종합 정리.
5. **8대 프런티어 심층 분석**: (i) 검색→생성 메모리 패러다임 전환, (ii) 자동화된 메모리 관리, (iii) RL-memory 통합, (iv) multimodal memory, (v) multi-agent shared memory, (vi) world model용 memory, (vii) trustworthiness, (viii) human cognition 연결.
6. **3형태 × 3기능 교차 매핑**: Token/Parametric/Latent × Factual/Experiential/Working를 교차해 빈 조합과 혼용 조합을 드러내고 대표 시스템(예: G-Memory, Zep, AriGraph)을 배치.

---

## Experiment & Results — 커버리지·벤치마크·프레임워크 정리

본 서베이는 107페이지에 걸쳐 에이전트 메모리 연구를 다각도로 정량 분석한다.

### 분류 체계별 커버리지

1. **Token-level Memory**는 전체 메모리 연구의 약 70% 이상을 차지. Flat(1D) 30편+, Planar(2D) 10편+, Hierarchical(3D) 8편+을 체계적으로 비교.
2. **Parametric Memory**는 Internal/External 방식으로 15편+ 방법론 분석.
3. **Latent Memory**는 Generate/Reuse/Transform 패러다임에서 12편+ 접근법 조사.

### 기능별 분포

4. **Factual Memory**는 User factual 25편+, Environment factual 15편+ 방법론을 Carrier/Form/Task/Optimization 4차원으로 비교.
5. **Experiential Memory**는 Case-based 15편+, Strategy-based 18편+, Skill-based 15편+ 방법론 분석(prompt engineering 다수이나 RL/SFT 기반도 증가 추세).
6. **Working Memory**는 Single-turn 10편+, Multi-turn 15편+ 방법론 정리. RL 기반 최적화가 최신 트렌드(MemAgent, MEM1, Memory-R1 등).

### 대표 벤치마크 (Section 6.1)

7. **MemBench**: 약 53,000 샘플 규모의 메모리 벤치마크.
8. **LoCoMo**: 300 샘플 장기 대화 평가셋.
9. **LongMemEval**: 500 샘플 장기 메모리 평가.
10. **StreamBench**: 평생 학습(lifelong learning) 평가용.
11. **SWE-bench Verified**: agentic 소프트웨어 공학 태스크 검증.
12. **HotpotQA** 등 long-document QA가 agent memory 평가에 빈번히 사용되는 gray area 사례로 지적.

### 오픈소스 프레임워크 (14개)

13. **MemGPT**(초기 virtual OS-style 메모리), **Mem0 / Mem0^g**(그래프 결합형), **MemOS**, **Zep**, **A-Mem**, **Memary**, **G-Memory**, **HippoRAG**, **AriGraph**, **MemoryBank** 등을 Factual/Experiential/Multimodal/Structure/Evaluation 5차원으로 비교.
14. RL 통합 프레임워크(MemAgent, RMM, MemSearcher, MEM1, Mem-alpha, Memory-R1)가 2025년에 급증하는 트렌드로 포착.

### 프런티어 분석

15. 8가지 미래 연구 프런티어 각각에 대해 "Look-Back + Future Perspective" 구조로 정리하여 향후 3~5년 연구 로드맵 제시.

---

## Limitation

서베이 논문이라는 속성상 통제된 실험적 비교는 수행되지 않으며, 분류 체계의 이론적 우수성에도 불구하고 각 카테고리 간 정량적 성능 비교가 부재하다.

2025년 하반기 에이전트 메모리 연구가 폭발적으로 증가하여, 서베이 시점 이후 발표된 중요 논문들이 누락될 수밖에 없는 구조적 한계가 있다(저자들도 GitHub issue로 누락 신고를 요청).

에이전트 메모리 벤치마크들이 각기 다른 메트릭과 설정을 사용하며, 통합된 평가 프로토콜이 아직 존재하지 않아 방법론 간 공정 비교가 어렵다.

현존 연구 대부분이 텍스트 중심이며, 진정한 omnimodal(텍스트+비전+오디오+센서) 메모리 시스템에 대한 분석은 제한적이다.

대부분의 분석이 학술 벤치마크에 초점을 맞추어, 실제 산업 환경에서의 메모리 시스템 배포 경험이나 확장성·비용 문제에 대한 논의가 제한적이다.

Forms-Functions-Dynamics 3축이 상호 배타적이지 않고 많은 시스템이 여러 조합에 걸쳐 있어, 실제 분류 시 애매한 경계 사례가 빈번하게 발생한다.

신뢰성(trustworthiness), 프라이버시, 메모리 공격(memory attack)에 관한 연구가 아직 초기 단계여서 해당 섹션이 상대적으로 얕게 다뤄졌다.

인간 인지 과학(episodic/semantic/procedural memory)과의 연결은 영감 수준에 머물러 있으며, 구체적 계산 모델로의 번역은 미완성이다.

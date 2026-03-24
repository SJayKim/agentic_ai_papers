# Memory in the Age of AI Agents: A Survey

**논문 정보**
- 제목: Memory in the Age of AI Agents: A Survey — Forms, Functions and Dynamics
- 저자: Yuyang Hu, Shichun Liu, Yanwei Yue, Guibin Zhang 외 다수 (NUS, RUC, Fudan, PKU, NTU 등)
- arXiv: 2512.13564v2 (2026년 1월 13일 개정)
- GitHub: https://github.com/Shichun-Liu/Agent-Memory-Paper-List
- 총 107페이지

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 에이전트에서 메모리(memory)가 핵심 구성요소로 부상했음에도 불구하고, 관련 연구가 파편화되어 있고 용어 정의가 불일치한 상황이다. 기존 분류 체계(장기/단기 메모리)는 현대 에이전트 메모리 시스템의 다양성과 역동성을 포착하기에 불충분하다. 이 서베이는 (1) 에이전트 메모리의 형태(Form)는 무엇인가, (2) 에이전트가 메모리를 필요로 하는 기능적 이유(Function)는 무엇인가, (3) 메모리가 시간에 따라 어떻게 작동하고 진화(Dynamics)하는가, (4) 향후 유망한 연구 방향은 무엇인가에 답하고자 한다. |
| **Motivation** | 기존 서베이들(Zhang et al. 2025; Wu et al. 2025)은 2025년 급격히 등장한 방법론적 발전(경험으로부터 재사용 가능한 도구를 증류하는 프레임워크, 메모리 증강 테스트-타임 스케일링 등)을 반영하지 못하고, 개념적 파편화로 인해 "에이전트 메모리" 논문들이 구현 방식, 목적, 가정에서 크게 다르다. 특히 기존 분류 체계(declarative, episodic, semantic, parametric 등)의 혼재가 개념적 명확성을 저해하므로, 통합된 새로운 분류 체계가 필요하다. |
| **Method** | **Forms–Functions–Dynamics** 삼각 구조를 통일된 분석 렌즈로 사용한다. (1) **Forms(형태)**: 메모리를 담는 아키텍처적 표현 방식 — Token-level, Parametric, Latent 3종으로 분류. (2) **Functions(기능)**: 에이전트가 메모리를 필요로 하는 이유 — Factual(사실적), Experiential(경험적), Working(작업) 메모리 3종으로 분류. (3) **Dynamics(역동성)**: 메모리의 생성(Formation), 진화(Evolution), 검색(Retrieval) 3단계 생애주기(lifecycle)로 분석. 이 프레임워크는 에이전트 메모리를 LLM 메모리, RAG, Context Engineering과 개념적으로 구분하는 공식적 정의와 함께 제시된다. |
| **Key Contribution** | (1) Forms–Functions–Dynamics 관점에서의 최신 에이전트 메모리 다차원 분류 체계 제시. (2) 서로 다른 메모리 형태와 기능적 목적 간의 적합성 및 상호작용에 대한 심층 분석 — 어떤 메모리 형태가 어떤 태스크에 적합한지 가이드 제공. (3) 에이전트 메모리의 미래 연구 방향 및 미개척 영역 식별(RL 통합, 멀티모달 메모리, 멀티에이전트 공유 메모리, 신뢰성 등). (4) 벤치마크 및 오픈소스 프레임워크의 종합적 자원 컬렉션 구축. |
| **Experiment/Results** | **주요 발견사항:** (1) Token-level 메모리는 투명성·수정 용이성 면에서 강점이 있으며 챗봇, 개인화 에이전트에 적합하다. (2) Parametric 메모리는 암묵적·추상적이며 역할극, 추론 집약적 태스크에 적합하지만 업데이트 비용이 높다. (3) Latent 메모리는 머신 네이티브이며 멀티모달 통합과 엣지 배포에 유리하나 해석 불가능성이 단점이다. (4) 기능적으로 Factual 메모리는 일관성·적응성을 보장하고, Experiential 메모리는 지속적 능력 향상에 기여하며, Working 메모리는 단일 태스크 내 추론을 지원한다. (5) 메모리 역동성에서 Formation(생성)→Evolution(진화: Consolidation/Updating/Forgetting)→Retrieval(검색: 4단계 파이프라인)의 생애주기가 확인된다. (6) RL 기반 메모리 시스템으로의 패러다임 전환이 진행 중이며, 검색 중심에서 생성 중심 메모리로의 이동이 관찰된다. |
| **Limitation** | (1) 급격히 확장하는 문헌으로 인한 누락 가능성 인정. (2) 멀티모달 메모리 연구는 시각 모달리티에 집중되어 있으며 오디오 등 타 모달리티는 상대적으로 미탐구 상태. (3) 완전한 RL 기반 메모리 시스템은 아직 초기 단계로, 수동 엔지니어링에 여전히 의존. (4) 신뢰성(개인정보, 해석가능성, 환각 저항성) 측면은 미개척 영역으로 남아 있다. (5) 멀티에이전트 공유 메모리, 월드 모델용 메모리는 아직 충분히 발전하지 않은 상태. |

---

## 선택 요소

| 항목 | 내용 |
|------|------|
| **Taxonomy/분류 체계** | 아래 참조 |

---

## 상세 분류 체계

### 1. Forms (형태): 메모리를 담는 표현 방식

#### 1.1 Token-level Memory (토큰 수준 메모리)
메모리를 인간이 읽을 수 있는 이산 토큰(텍스트)으로 저장. 투명성·수정 용이성이 높고 plug-and-play 방식으로 다양한 모델과 통합 가능.

- **Flat Memory (1D)**: 단순 리스트/시퀀스 구조. MemGPT, MemoryBank, mem0 등.
- **Planar Memory (2D)**: 노드 간 링크를 통해 집단적 시너지 가능한 그래프/KV 구조. Zep, AriGraph, HippoRAG 등.
- **Hierarchical Memory (3D)**: 다층 추상화 계층 구조. GraphRAG, HiAgent, G-Memory 등.
- **Adaptation**: 태스크에 따른 메모리 형태 선택 가이드라인 제공.

#### 1.2 Parametric Memory (파라메트릭 메모리)
메모리를 모델 파라미터에 직접 인코딩.

- **Internal Parametric Memory**: 원본 모델 파라미터 내부에 직접 저장. Pre/Mid/Post-train 단계별 접근법.
  - Pre-train: LMLM, HierMemLM, StreamingLLM
  - Mid-train: Agent-Founder, Early Experience
  - Post-train: Character-LM, MEND, ROME, MEMIT 등 모델 편집 기법
- **External Parametric Memory**: LoRA, Adapter 등 보조 파라미터에 저장. MLP-Memory, K-Adapter, WISE, ELDER, Retroformer 등.

#### 1.3 Latent Memory (잠재 메모리)
모델 내부 표현(KV 캐시, 활성화값, 숨겨진 상태)에 암묵적으로 메모리 저장.

- **Generate**: 보조 모델이 잠재 임베딩 생성. Gist, AutoCompressor, MemoryLLM, Titans, MemGen.
- **Reuse**: 이전 계산의 KV 캐시 직접 재사용. Memorizing Transformers, LONGMEM.
- **Transform**: 기존 잠재 상태를 압축/변환. SnapKV, PyramidKV, H2O, R3Mem.

---

### 2. Functions (기능): 에이전트가 메모리를 필요로 하는 이유

#### 2.1 Factual Memory (사실적 메모리) — 장기 메모리
명시적인 선언적 사실(대화 이력, 사용자 선호, 환경 상태)을 저장·검색. 일관성(Consistency), 일관성(Coherence), 적응성(Adaptability) 보장.

- **User Factual Memory**: 인간-에이전트 상호작용 일관성 유지.
  - Dialogue Coherence: MemGPT, MemoryBank, mem0, RMM, D-SMART
  - Knowledge Persistence: MemoryLLM, HippoRAG, WISE
  - Shared Memory Access: MetaGPT, GameGPT, G-Memory
- **Environment Factual Memory**: 외부 세계 상태(문서, 리소스, 타 에이전트 역량) 관련 사실 유지.

#### 2.2 Experiential Memory (경험적 메모리) — 장기 메모리
과거 태스크 실행에서 전략적·절차적 지식 누적. 에이전트의 문제 해결 능력을 지속적으로 향상.

- **Case-based Memory**: 구체적 사례(솔루션, 궤적) 저장. MapCoder, Synapse, ExpeL, JARVIS-1, Early Experience
- **Strategy-based Memory**: 추상적 인사이트, 워크플로우 저장. H2R, ReasoningBank, AgentKB, AWM
- **Skill-based Memory**: 재사용 가능한 함수·코드베이스 저장. LEGOMem, Memp, SkillWeaver, Voyager, DGM
- **Hybrid Memory**: 여러 유형 혼합.

#### 2.3 Working Memory (작업 메모리) — 단기 메모리
단일 태스크/세션 내 능동적 컨텍스트 관리를 위한 용량 제한적 작업 공간.

- **Single-turn Working Memory**: 단일 턴 내 추론 지원.
  - Input Condensation: LongLLMLingua, ICAE, AutoCompressors
  - Observation Abstraction: Synapse, Context-as-memory, VideoAgent
  - Cognitive Planning: PRIME, Agent-S, KARMA, SayPlan
- **Multi-turn Working Memory**: 다중 턴에 걸친 컨텍스트 관리.
  - State Consolidation: Mem1, MemSearcher, ReSum
  - Hierarchical Folding: Context-folding, AgentFold, DeepAgent

---

### 3. Dynamics (역동성): 메모리의 작동과 진화 과정

#### 3.1 Memory Formation (메모리 생성)
환경과의 상호작용에서 발생하는 정보적 산출물로부터 메모리를 형성하는 과정.

- **Semantic Summarization**: 텍스트 요약을 통한 메모리 생성. RecurrentGPT, Memento, MemoryBank
- **Knowledge Distillation**: 궤적에서 재사용 가능한 지식 증류. ExpeL, AgentRR, H2R, Mem-α
- **Structured Construction**: 토폴로지 구조(그래프)로 정보 조직화.
  - Entity-level: KGT, Mem0g, D-SMART, AriGraph, Zep
  - Chunk-level: RAPTOR, MemTree, A-MEM, G-Memory
- **Latent Representation**: 잠재 임베딩으로 경험 인코딩. MemoryLLM, MemGen, CoMEM
- **Parametric Internalization**: 외부 메모리를 모델 파라미터로 내재화.
  - Knowledge Internalization: ROME, MEMIT, CoLoR
  - Capability Internalization: SFT, DPO, GRPO 기반 방법들

#### 3.2 Memory Evolution (메모리 진화)
새로운 메모리를 기존 메모리와 통합하는 동적 진화 과정.

- **Consolidation (통합)**: 단기 흔적을 장기 지식으로 변환.
  - Local Consolidation: RMM, VLN Memory
  - Cluster-level Fusion: PREMem, TiM, CAM
  - Global Integration: MOOM, Matrix, AgentFold
- **Updating (업데이트)**: 충돌 해결 및 정보 수정.
  - External Memory Update: MemGPT, Zep, MOOM, Mem-α
  - Model Editing: ROME, MEMORYLLM, M+, ChemAgent
- **Forgetting (망각)**: 불필요한 정보 제거로 효율성 유지.
  - Time-based: MemGPT, MAICC
  - Frequency-based: XMem, KARMA, MemOS (LRU)
  - Importance-driven: TiM, MemTool, MemoryBank

#### 3.3 Memory Retrieval (메모리 검색)
4단계 파이프라인으로 구성.

- **Retrieval Timing & Intent**: 검색 타이밍과 의도 자동화. MemGPT, ComoRAG, MemGen, MemOS
- **Query Construction**: 쿼리를 효과적인 검색 신호로 변환.
  - Query Decomposition: Visconde, PRIME, Agent KB
  - Query Rewriting: HyDE, MemoRAG, MemGuide
- **Retrieval Strategies**: 실제 검색 실행.
  - Lexical: TF-IDF, BM25
  - Semantic: Sentence-BERT 기반 임베딩 유사도
  - Graph: AriGraph, HippoRAG, Mem0g, D-SMART, Zep
  - Hybrid: Agent KB, MIRIX, Generative Agents
- **Post-Retrieval Processing**: 검색 결과 정제.
  - Re-ranking & Filtering: Zep, Memory-R1, RMM
  - Aggregation & Compression: ComoRAG, G-Memory

---

## 미래 연구 방향 (Positions and Frontiers)

| 방향 | 핵심 내용 |
|------|----------|
| **Memory Retrieval → Memory Generation** | 정적 저장소 조회에서 컨텍스트 적응적 메모리 생성으로 패러다임 전환. Retrieve-then-generate 및 Direct generation 두 방향 존재. 미래 메모리는 문맥 적응적, 이질적 신호 통합, 학습 및 자기 최적화 특성을 가져야 함. |
| **Automated Memory Management** | 수작업 설계에서 자율 관리로 전환. 에이전트가 add/update/delete/retrieval 메모리 작업을 도구 호출 형태로 직접 결정. 자기 조직화 계층적 메모리 구조 개발 필요. |
| **RL Meets Agent Memory** | RL-free → RL-assisted → Fully RL-driven 메모리 시스템으로의 진화. 인간 사전 지식에 의존하지 않는 메모리 아키텍처 자체 설계 및 메모리 전체 생애주기(생성-진화-검색)의 end-to-end RL 학습이 목표. |
| **Multimodal Memory** | 시각·오디오·영상 등 다양한 모달리티 지원하는 통합 메모리. 현재는 시각 모달리티 집중, 진정한 omnimodal 지원 미흡. |
| **Shared Memory in Multi-Agent Systems** | 고립된 개별 메모리에서 공유 인지 기반(shared cognitive substrate)으로. 에이전트 역할/권한 인식 기반 읽기·쓰기, 학습 기반 공유 메모리 관리 필요. |
| **Memory for World Model** | 월드 모델의 장기 시간적 일관성을 위한 메모리. 단순 버퍼링에서 메모리 기반 계층적 상태 관리로. |
| **Trustworthy Memory** | 세 가지 핵심 축: ① Privacy(세분화된 권한 메모리, 암호화 저장, 적응형 망각) ② Explainability(추적 가능한 접근 경로, 메모리 영향 인과 그래프) ③ Hallucination Robustness(충돌 감지, 불확실성 인식 생성). OS-like 메모리(버전 관리, 감사 가능, 에이전트-사용자 공동 관리) 비전 제시. |
| **Human-Cognitive Connections** | Atkinson-Shiffrin 다중 저장 모델 및 Tulving의 에피소딕/의미적/절차적 메모리와의 유사성 분석. 미래: 생물학적 수면 유사 오프라인 통합 메커니즘, 재구성적 생성 메모리(Complementary Learning Systems 이론 적용). |

---

## 주요 자원 요약

### 벤치마크 (Memory/Lifelong-oriented)
- MemBench (53,000 샘플), LoCoMo (300 샘플), LongMemEval (500 샘플), PerLTQA (8,593 샘플)
- MemoryBench, LifelongAgentBench, StreamBench (연속 학습 평가)
- LongBench, LongBench v2, RULER, BABILong (장문 맥락 평가)
- HaluMem (메모리 환각 평가, 3,467 샘플)

### 오픈소스 프레임워크
- **에이전트 중심**: MemGPT, Mem0, Memobase, MemoryOS, MemOS, Zep
- **범용 검색/데이터베이스**: Pinecone, Chroma, Weaviate
- **신규 프레임워크**: MIRIX, MemU, MemEngine, Second Me, LangMem, Cognee

---

## 핵심 인사이트 요약

이 서베이의 가장 중요한 결론은 **에이전트 메모리가 단순한 보조적 저장 메커니즘이 아니라, 에이전트가 시간적 일관성, 지속적 적응, 장기 역량을 달성하기 위한 필수적인 인지 기반**이라는 것이다. Forms-Functions-Dynamics 프레임워크는 분산된 메모리 연구를 통합하고, 향후 완전히 학습 가능하고 자기 조직화된 메모리 시스템(특히 RL 기반, 멀티모달, 신뢰성 보장 메모리)으로의 발전 경로를 제시한다. 메모리 설계는 차세대 강건하고 범용적인 인공지능 개발에서 결정적인 역할을 할 것으로 전망된다.

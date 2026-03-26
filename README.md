# LLM Agentic AI 논문 정리

LLM 기반 에이전트의 핵심 기술(메모리, 도구, 계획, 자기교정, RAG)을 다루는 **71편의 논문**을 6개 카테고리로 분류하여 체계적으로 정리한 프로젝트입니다.

> 각 논문의 상세 요약은 [`summaries/`](summaries/) 디렉토리에, 전체 개요는 [`agent_memory_papers.md`](agent_memory_papers.md)에서 확인할 수 있습니다.

---

## 주요 논문 하이라이트

### 1. Memory Management (19편)

에이전트가 장기 상호작용 기록을 구조화하고 필요할 때 꺼내어 쓰는 아키텍처 연구

| 논문 | 학회 | 핵심 |
|------|------|------|
| **MemGPT** | UC Berkeley | OS 가상 메모리 페이징을 LLM에 적용, Main Context↔Disk 자율 스와핑 |
| **A-MEM** | NeurIPS 2025 | 제텔카스텐 방식으로 메모리 간 링크를 자율 생성하는 동적 메모리 |
| **G-Memory** | NeurIPS 2025 Spotlight | 3계층 그래프(Insight/Query/Interaction)로 다중 에이전트 협업 메모리 관리 |
| **HippoRAG** | NeurIPS 2024 | 해마 인덱싱 이론 + KG + PPR로 단일 단계 멀티홉 검색, IRCoT 대비 10-20x 저렴 |
| **MemoryOS** | EMNLP 2025 Oral | 3계층 메모리 OS(STM→MTM→LTM) + 4개 모듈, LoCoMo F1 +49% |
| **Evo-Memory** | Google DeepMind | 10+ 메모리 모듈을 통합 평가하는 자기 진화 벤치마크, ReMem 프레임워크 |

### 2. Tool Use & MCP (9편)

에이전트가 외부 API나 시스템과 안정적으로 상호작용하기 위한 호출 기법 연구

| 논문 | 학회 | 핵심 |
|------|------|------|
| **Toolformer** | NeurIPS 2023 / Meta | Self-supervised로 도구 호출을 자가 학습, 6.7B가 175B에 필적 |
| **Gorilla** | UC Berkeley | Retriever-Aware Fine-tuning으로 7B > GPT-4 API 정확도, 환각 0~7% |
| **ToolLLM** | ICLR 2024 Spotlight | 16,000+ REST API + DFSDT로 오픈소스가 ChatGPT급 도구 사용 달성 |
| **τ-bench** | ICLR 2025 / Sierra | 도구-에이전트-사용자 3자 상호작용 벤치마크, GPT-4o조차 50% 미만 |

### 3. Planning & Task Decomposition (9편)

모호한 목표를 논리적 순서로 하위 작업으로 쪼개고 검증하는 오케스트레이션 설계

| 논문 | 학회 | 핵심 |
|------|------|------|
| **HuggingGPT** | NeurIPS 2023 / Microsoft | LLM-as-Controller로 HuggingFace 모델들을 오케스트레이션 |
| **AFlow** | ICLR 2025 Oral (top 1.8%) | MCTS로 에이전틱 워크플로우 자동 생성, GPT-4o의 4.55% 비용으로 능가 |
| **OWL** | NeurIPS 2025 | Planner+Worker 분리, RL로 GAIA 69.70% 오픈소스 SOTA |
| **GPTSwarm** | ICML 2024 Oral (top 1.5%) | 에이전트를 계산 그래프로 모델링, 프롬프트+토폴로지 동시 자동 최적화 |
| **WebRL** | ICLR 2025 / Tsinghua | 자기 진화 RL로 Llama-8B가 GPT-4-Turbo 초과 (42.4% vs 17.6%) |

### 4. Self-Correction & Test-Time Compute (12편)

에이전트가 스스로 생각하고, 에러를 발견하면 스스로 수정하는 심층 추론 메커니즘

| 논문 | 학회 | 핵심 |
|------|------|------|
| **Cannot Self-Correct** | ICLR 2024 / DeepMind | 외부 피드백 없는 자기 교정이 오히려 성능 하락 (GPT-4: 95.5%→89.0%) |
| **SCoRe** | ICLR 2025 Oral / DeepMind | 멀티턴 RL로 최초의 유의미한 내재적 자기 교정 달성, MATH +15.6% |
| **Scaling TTC** | ICLR 2025 Oral / DeepMind | Compute-optimal 전략으로 작은 모델+TTC가 14x 큰 모델 능가 |
| **Thinking-Optimal** | NeurIPS 2025 | 과도한 CoT 확장의 역효과 실증, TOPS 전략으로 QwQ급 성능 |
| **Rethinking FT** | NeurIPS 2025 / Stanford | CE 학습의 과신이 pass@N을 저해, DCO 손실로 탐색-활용 균형 |

### 5. Agentic RAG & Graph RAG (10편)

지식 그래프를 구성하고 에이전트가 다중 홉 추론을 통해 문맥을 파악하는 기술

| 논문 | 학회 | 핵심 |
|------|------|------|
| **GraphRAG** | Microsoft Research | 엔티티 KG + 커뮤니티 탐지 + 계층적 요약으로 글로벌 센스메이킹 |
| **LightRAG** | EMNLP 2025 / BUPT-HKU | 이중 레벨 검색 + 증분 업데이트로 GraphRAG 비용 문제 해결 |
| **Think-on-Graph** | ICLR 2024 | LLM이 KG 위에서 빔 서치로 추론 경로 탐색, 9개 중 6개 SOTA |
| **Plan-on-Graph** | NeurIPS 2024 | 서브 목표 분해 + 적응적 반성으로 ToG 대비 LLM 호출 40.8% 절감 |

### 6. General — 벤치마크 & 프레임워크 (12편)

에이전트 아키텍처, 평가 벤치마크, 멀티에이전트 프레임워크

| 논문 | 학회 | 핵심 |
|------|------|------|
| **MetaGPT** | ICLR 2024 | SOP 기반 역할 할당으로 환각 전파 억제, HumanEval 85.9% |
| **AutoGen** | COLM 2024 / Microsoft | 가장 널리 배포된 멀티 에이전트 대화 프레임워크 |
| **SWE-bench** | ICLR 2024 Oral / Princeton | 2,294개 실제 GitHub 이슈로 코딩 에이전트 평가의 사실상 표준 |
| **GAIA** | ICLR 2024 / Meta AI | 범용 AI 어시스턴트 벤치마크, 인간 92% vs GPT-4 15% |
| **OSWorld** | NeurIPS 2024 | 실제 OS 환경에서 멀티모달 에이전트 평가, 인간 72% vs 모델 12% |
| **ADAS** | ICLR 2025 | Meta Agent Search로 에이전트 아키텍처를 스스로 프로그래밍 |

---

## 프로젝트 구조

```
├── agent_memory_papers.md          # 전체 논문 개요 (카테고리별 테이블, 71편)
├── summaries/                      # 개별 논문 상세 요약 마크다운
│   ├── 01_A-MEM.md ~ 71_SWE-bench.md
│   └── agent_memory_pdfs/          # 원본 PDF 저장소
├── summarize_instruction.md        # 요약 파이프라인 정의
├── notion_mcp_instruction.md       # Notion API 연동 가이드
└── CLAUDE.md                       # Claude Code 에이전트 지침서
```

## 사용법 (Claude Code)

| 커맨드 | 설명 |
|--------|------|
| `/paper {논문}` | PDF 확보 → 요약 → 개요 업데이트 → Notion 업로드 |
| `/paper-summary {논문}` | 위와 동일하되 Notion 업로드 제외 |
| `/notion-upload {대상}` | 로컬 요약을 Notion에 반영 |

논문 제목, 약칭, arXiv ID 모두 가능하며 쉼표로 여러 편 동시 처리 가능.

```
/paper MemoryBank
/paper MemoryBank, RAISE, CoALA
/paper 2401.12345
```

## 카테고리 체계

| # | 카테고리 | 범위 | 편수 |
|---|---------|------|------|
| 1 | **Memory Management** | 메모리 저장/검색/구조화/진화 | 19편 |
| 2 | **Tool Use & MCP** | 외부 도구 호출, function calling, MCP | 9편 |
| 3 | **Planning & Task Decomposition** | 작업 분할, 계획 수립, 오케스트레이션 | 9편 |
| 4 | **Self-Correction & Test-Time Compute** | 자가 교정, 추론 시간 연산, RL 기반 학습 | 12편 |
| 5 | **Agentic RAG & Graph RAG** | 지식 그래프, 그래프 RAG, 능동적 검색 | 10편 |
| 6 | **General** | 에이전트 아키텍처/서베이/벤치마크/기타 | 12편 |

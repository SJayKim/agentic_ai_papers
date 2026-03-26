# LLM Agentic AI 논문 정리

## 1. Memory Management (메모리 관리 및 구조화)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **A-MEM** | 2025.10 | NeurIPS 2025 | Wujiang Xu | 제텔카스텐 방식으로 메모리 간 링크를 자율 생성, 지식 네트워크를 동적으로 진화 |
| **MemEvolve** | 2025.12 | OPPO / NUS | Guibin Zhang | 경험 축적(내부 루프) + 메모리 코드 구조 최적화(외부 루프)로 메모리 시스템 자체를 메타 진화 |
| **ALMA** | 2026.02 | UBC | Yiming Xiong | 메타 에이전트가 DB 스키마와 검색/업데이트 메커니즘을 실행 가능한 코드로 자동 생성 |
| **SeCom** | 2025 | ICLR 2025 / Microsoft | Zhuoshi Pan | Turn/Session 단위 메모리 분할의 한계를 밝히고 최적 메모리 구성 단위를 연구 |
| **MIRIX** | 2025.07 | UCSD / NYU | Yu Wang | 다양한 메모리 타입과 에이전트를 모듈형으로 결합하는 다중 에이전트 메모리 시스템 |
| **Preference-Aware Memory** | 2025.10 | N/A | Haoran Sun | 장기 상호작용 중 사용자 선호도 변화를 감지하여 메모리를 동적 업데이트 |
| **MemoryAgentBench** | 2026.03 | ICLR 2026 | Yuanzhe Hu | 검색 정확도, 테스트 타임 학습, 장기 문맥 이해, 선택적 망각 등 4대 역량 평가 벤치마크 |
| **Memory Mgmt Impact** | 2025.05 | Harvard / UGA / MSU | Zidi Xiong | 메모리 추가/삭제 전략이 장기 성능에 미치는 영향 분석, 오류 전파 완화 전략 제시 |
| **Privacy Risks in Memory** | 2025.06 | ACL 2025 | Bo Wang | 악의적 프롬프트를 통한 메모리 유출 취약점 증명 및 방어 필요성 제기 |
| **Memory Survey** | 2025.12 | NUS / RUC / Fudan | Yuyang Hu | 메모리 형성/진화/검색 분류, RL 통합, 멀티 에이전트 메모리 등 종합 서베이 (100p) |
| **ACE** | 2026.01 | ICLR 2026 / Stanford | Qizheng Zhang | 컨텍스트를 진화하는 플레이북으로 관리, Generator-Reflector-Curator 3단계로 Context Collapse 방지 |
| **G-Memory** | 2025.06 | NeurIPS 2025 / NUS | Guibin Zhang | Insight/Query/Interaction 3계층 그래프로 MAS 협업 궤적을 관리, 양방향 탐색으로 역할별 메모리 제공 |
| **Evo-Memory** | 2025.11 | Google DeepMind / UIUC | Tianxin Wei | 10+ 메모리 모듈을 통합 평가하는 자기 진화 메모리 벤치마크, ReMem(Think-Act-Refine) 프레임워크 제안 |
| **MemGPT** | 2023.10 | UC Berkeley | Charles Packer | OS 가상 메모리 페이징을 LLM에 적용, Main Context↔External Storage 간 자율적 데이터 스와핑 |
| **DelTA** | 2024.10 | ICLR 2025 / HIT-Tencent | Yutong Wang | 문서 번역에서 고유명사 기록/이중 요약/장단기 메모리 4계층으로 일관성과 품질 동시 달성 |
| **MemoryOS** | 2025.05 | EMNLP 2025 Oral / BUPT-Tencent | Jiazheng Kang | 3계층 메모리 OS(STM/MTM/LTM) + 4모듈로 LoCoMo F1 +49% |
| **HippoRAG** | 2024.05 | NeurIPS 2024 / OSU | Bernal Jiménez | 해마 인덱싱 이론 + KG + PPR로 단일 단계 멀티홉 검색, IRCoT 대비 10-20x 저렴 |
| **HippoRAG 2** | 2025.02 | OSU | Bernal Jiménez | HippoRAG 확장, GraphRAG/LightRAG 대비 +7% 및 비용·지연 효율적 |
| **A-MAC** | 2026.03 | ICLR 2026 Workshop | Guilin Zhang | 메모리 입장을 5가지 요인으로 분해하는 구조적 의사결정 프레임워크 |

## 2. Tool Use & MCP (도구 사용 및 모델 컨텍스트 프로토콜)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **BUTTON** | 2025 | ICLR 2025 / Baichuan | Mingyang Chen | Bottom-Up 지시 구성 + Top-Down 궤적 생성으로 멀티턴 function calling 데이터 합성 |
| **ToolACE** | 2025 | ICLR 2025 / Huawei | Weiwen Liu | 자기 진화 API 합성(26,507개) + 모델 인식 복잡도 조절로 8B 모델이 GPT-4급 function calling 달성 |
| **Gorilla** | 2023.05 | UC Berkeley / Microsoft | Shishir G. Patil | Retriever-Aware Fine-tuning으로 7B 모델이 GPT-4 초과하는 API 호출 정확도, 환각 0~7% 달성 |
| **Toolformer** | 2023.02 | Meta AI / NeurIPS 2023 | Timo Schick | Self-supervised 손실 기반으로 모델이 도구 호출 시점·방법을 자가 학습, 6.7B가 175B에 필적 |
| **ToolLLM** | 2023.07 | ICLR 2024 Spotlight / Tsinghua | Yujia Qin | 16,000+ REST API + DFSDT 추론으로 오픈소스 LLM이 ChatGPT급 도구 사용 달성 |
| **AvaTaR** | 2024.06 | NeurIPS 2024 / Stanford | Shirley Wu | 대조적 추론으로 도구 사용 프롬프트 자동 최적화, 검색 +14%, QA +13% |
| **τ-bench** | 2024.06 | ICLR 2025 / Sierra-Princeton | Shunyu Yao | 도구-에이전트-사용자 3자 상호작용 벤치마크, GPT-4o 50% 미만 성공 |
| **MCP Security** | 2025.03 | arXiv | Xinyi Hou | MCP 4단계 라이프사이클별 16개 보안 위협 분류 및 방어 전략 |
| **Agent Protocols Survey** | 2025.04 | arXiv / SJTU | Yingxuan Yang | MCP, A2A, ACP, ANP 에이전트 통신 프로토콜 체계적 비교 서베이 |

## 3. Planning & Task Decomposition (계획 수립 및 작업 분할)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **Chain of Agents** | 2024.06 | Google Cloud AI | Yusen Zhang | 긴 컨텍스트를 청크로 분할 후 Worker-Manager 다중 에이전트 순차 협업으로 처리 |
| **AOP** | 2024.10 | ICLR 2025 / Alibaba | Ao Li | Solvability/Completeness/Non-Redundancy 3원칙 기반 에이전트 지향 계획, 보상 모델로 효율적 평가 |
| **OWL** | 2025.05 | NeurIPS 2025 / CAMEL-AI | Mengkang Hu | 도메인 무관 Planner + 특화 Worker 분리, RL로 Planner만 학습하여 GAIA 69.70% 오픈소스 SOTA |
| **HuggingGPT** | 2023.03 | NeurIPS 2023 / Microsoft | Yongliang Shen | ChatGPT를 컨트롤러로 Hugging Face 모델들을 오케스트레이션하는 LLM-as-Controller 패러다임 |
| **AFlow** | 2024.10 | ICLR 2025 Oral / DeepWisdom-PKU | Jiayi Zhang | MCTS로 에이전틱 워크플로우 자동 생성, 6개 벤치마크 +5.7%, GPT-4o의 4.55% 비용 |
| **WebRL** | 2024.11 | ICLR 2025 / Tsinghua | Zehan Qi | 자기 진화 RL 커리큘럼으로 Llama-8B가 GPT-4-Turbo 초과 (WebArena 42.4% vs 17.6%) |
| **SWE-agent** | 2024.05 | NeurIPS 2024 / Princeton | John Yang | ACI 설계 원칙으로 GitHub 이슈 자동 해결, SWE-bench 당시 SOTA 12.29% |
| **EvoAgent** | 2024.06 | NAACL 2025 / Fudan-Microsoft | Siyu Yuan | 진화 알고리즘(돌연변이/교차/선택)으로 단일→다중 에이전트 자동 확장 |
| **GPTSwarm** | 2024.02 | ICML 2024 Oral / KAUST | Mingchen Zhuge | 에이전트를 계산 그래프로 모델링, 프롬프트+토폴로지 동시 자동 최적화 |

## 4. Self-Correction & Test-Time Compute (자가 교정 및 추론 시간 연산)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **AgentRefine** | 2025.01 | ICLR 2025 / BUPT | Dayuan Fu | 합성 환경에서 오류-수정 trajectory로 학습하여 에이전트 일반화 능력 강화 |
| **Test-Time Compute Survey** | 2025.06 | Soochow / NUS / Ant | Yixin Ji | System-1→System-2 전환에서 test-time compute의 역할을 TTA와 TTR로 체계적 분류 |
| **Eval Long-Context Reasoning** | 2024.12 | NeurIPS 2025 Workshop / UMich | Andy Chung | WebAgent의 긴 컨텍스트에서 추론 성능 급락(40%→10% 미만) 실증 및 iRAG 제안 |
| **Turn-Level Credit** | 2025.05 | UMN / Texas A&M | Quan Wei | 멀티턴 에이전트 RL 학습에서 턴 단위 보상 할당(MT-PPO/MT-GRPO)으로 fine-grained 최적화 |
| **Scaling TTC** | 2024.08 | ICLR 2025 (Oral) / DeepMind | Charlie Snell | Compute-optimal 전략으로 best-of-N 대비 4x 효율 개선, 작은 모델+TTC가 14x 큰 모델 능가 |
| **Thinking-Optimal** | 2025.02 | NeurIPS 2025 / RUC-Microsoft | Wenkai Yang | 과도한 CoT 확장의 역효과 실증, 최적 추론 길이를 자율 결정하는 TOPS 전략으로 QwQ급 성능 |
| **Cannot Self-Correct** | 2023.10 | ICLR 2024 / Google DeepMind | Jie Huang | 외부 피드백 없는 내재적 자기 교정이 오히려 성능 하락시킴을 실증 (GPT-4: 95.5%→89.0%) |
| **CorrectBench** | 2025.10 | NeurIPS 2025 / HUST | Guiyao Tie | 11개 교정 방법×11개 LLM 포괄 벤치마크, 외부 교정은 효과적이나 추론 LLM에는 제한적 |
| **Rethinking Fine-Tuning** | 2025.02 | NeurIPS 2025 / Stanford | Feng Chen | CE 학습의 과신이 pass@N을 저해, DCO 손실로 탐색-활용 균형 최적화 |
| **SCoRe** | 2024.09 | ICLR 2025 Oral / DeepMind | Aviral Kumar | 2단계 멀티턴 RL로 최초의 유의미한 내재적 자기 교정 달성, MATH +15.6% |
| **SuperCorrect** | 2024.10 | ICLR 2025 / PKU | Ling Yang | 사고 템플릿 증류 + 교차 모델 DPO로 7B가 DeepSeekMath 대비 +7.8% |
| **S²R** | 2025 | ACL 2025 | Ruotian Ma | 3.1K 샘플만으로 자기 검증+교정 학습, Qwen2.5-Math 51%→81.6% |

## 5. Agentic RAG & Graph RAG (에이전틱/그래프 RAG)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **MAGMA** | 2026.01 | UT Dallas | Dongming Jiang | Semantic/Temporal/Causal/Entity 등 다중 그래프 뷰로 메모리 분리 저장 및 의도 기반 탐색 |
| **AriGraph** | 2025.05 | IJCAI 2025 | Anokhin | Episodic + Semantic 메모리를 결합해 지식 그래프 형태의 World Model을 자율 구축 |
| **Self-Reflective KG** | 2025.05 | USTC | Jiajun Zhu | KG 기반 QA에서 자기 성찰적 계획을 통해 reasoning path 신뢰성 향상 |
| **GraphRAG** | 2024.04 | Microsoft Research | Darren Edge | 엔티티 KG + Leiden 커뮤니티 탐지 + 계층적 요약으로 전체 코퍼스의 글로벌 센스메이킹 |
| **Agentic RAG + KG** | 2025.07 | Ekimetrics | Jean Lelong | 에이전트가 KG를 Cypher로 동적 탐색하며 반복적 다중 홉 추론 수행 (INRAExplorer) |
| **SUBQRAG** | 2025.10 | Northeastern University | Jiaoyang Li | 서브 질문 분해 + 동적 KG 업데이트 + Graph Memory로 멀티홉 QA의 정확도와 추적성 향상 |
| **LightRAG** | 2024.10 | BUPT / HKU | Zirui Guo | 이중 레벨(low/high) 검색 + 증분 업데이트로 GraphRAG의 비용 문제를 해결하는 경량 Graph RAG |
| **Think-on-Graph** | 2023.07 | ICLR 2024 / IDEA Research | Jiashuo Sun | LLM⊗KG 패러다임: LLM이 KG 위에서 빔 서치로 추론 경로 탐색, 9개 중 6개 SOTA |
| **Think-on-Graph 2.0** | 2024.07 | ICLR 2025 / IDEA Research | Shengjie Ma | KG 탐색과 문서 검색을 교대 수행하는 하이브리드 프레임워크, 7개 중 6개 SOTA |
| **Plan-on-Graph** | 2024.10 | NeurIPS 2024 | Liyi Chen | 서브 목표 분해 + 적응적 가이드/메모리/반성으로 ToG 대비 40.8% 적은 LLM 호출 |

## 6. General (에이전트 아키텍처 및 기타)

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **ADAS** | 2025.03 | ICLR 2025 | Shengran Hu | Meta Agent Search 알고리즘으로 에이전트 아키텍처를 스스로 프로그래밍 |
| **MASS** | 2026.01 | ICLR 2026 / Google | Han Zhou | 프롬프트 최적화와 토폴로지 탐색을 인터리빙하여 멀티 에이전트 시스템을 자동 설계 |
| **AgentSquare** | 2024.10 | ICLR 2025 / Tsinghua | Yu Shang | Planning/Reasoning/Tool Use/Memory 4개 모듈의 진화·재조합으로 최적 에이전트 자동 탐색 |
| **Multi-Agent Collab Survey** | 2025 | UCC / TCD / PNU | Khanh-Tung Tran | MAS 협업 메커니즘을 Actors/Types/Structures/Strategies/Coordination 5차원으로 분류 |
| **Creativity in MAS** | 2025.05 | NTU | Yi-Cheng Lin | MAS에서의 창의성을 주체성 스펙트럼·생성 기법·평가 방법으로 체계화한 최초 서베이 |
| **AgentBench** | 2023.08 | ICLR 2024 / Tsinghua | Xiao Liu | 8개 환경에서 29개 LLM을 에이전트로 평가하는 최초의 다중 환경 벤치마크 |
| **GAIA** | 2023.11 | ICLR 2024 / Meta AI | Grégoire Mialon | 범용 AI 어시스턴트 벤치마크, 인간 92% vs GPT-4 15%로 AGI 격차 정량화 |
| **OSWorld** | 2024.04 | NeurIPS 2024 / HKU-Salesforce | Tianbao Xie | 실제 OS 환경(Ubuntu/Win/Mac)에서 멀티모달 에이전트 평가, 인간 72% vs 모델 12% |
| **AgentHarm** | 2024.10 | ICLR 2025 / EPFL-CMU | Maksym Andriushchenko | 110개 악의적 에이전트 태스크로 안전성 평가, LLM이 놀라울 정도로 순응적 |
| **AutoGen** | 2023.08 | COLM 2024 / Microsoft | Qingyun Wu | 커스터마이즈 가능한 다중 에이전트 대화 프레임워크, 사실상 표준 |
| **MetaGPT** | 2023.08 | ICLR 2024 / FoundationAgents | Sirui Hong | SOP 기반 역할 할당으로 환각 전파 억제, HumanEval 85.9% Pass@1 |
| **SWE-bench** | 2023.10 | ICLR 2024 Oral / Princeton | Carlos E. Jimenez | 2,294개 실제 GitHub 이슈로 코딩 에이전트 평가하는 사실상 표준 벤치마크 |

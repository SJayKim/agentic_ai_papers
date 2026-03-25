# LLM Agent Memory 관련 논문 정리

## 1. Knowledge Graph & Graph RAG

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **A-MEM** | 2025.10 | NeurIPS 2025 | Wujiang Xu | 제텔카스텐 방식으로 메모리 간 링크를 자율 생성, 지식 네트워크를 동적으로 진화 |
| **MAGMA** | 2026.01 | UT Dallas | Dongming Jiang | Semantic/Temporal/Causal/Entity 등 다중 그래프 뷰로 메모리 분리 저장 및 의도 기반 탐색 |
| **AriGraph** | 2025.05 | IJCAI 2025 | Anokhin | Episodic + Semantic 메모리를 결합해 지식 그래프 형태의 World Model을 자율 구축 |

## 2. Meta-Learning & Evolution

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **MemEvolve** | 2025.12 | OPPO / NUS | Guibin Zhang | 경험 축적(내부 루프) + 메모리 코드 구조 최적화(외부 루프)로 메모리 시스템 자체를 메타 진화 |
| **ALMA** | 2026.02 | UBC | Yiming Xiong | 메타 에이전트가 DB 스키마와 검색/업데이트 메커니즘을 실행 가능한 코드로 자동 생성 |
| **ADAS** | 2025.03 | ICLR 2025 | Shengran Hu | Meta Agent Search 알고리즘으로 에이전트 아키텍처를 스스로 프로그래밍 |

## 3. Long-term & Multi-Agent

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **SeCom** | 2025 | ICLR 2025 / Microsoft | Zhuoshi Pan | Turn/Session 단위 메모리 분할의 한계를 밝히고 최적 메모리 구성 단위를 연구 |
| **MIRIX** | 2025.07 | UCSD / NYU | Yu Wang | 다양한 메모리 타입과 에이전트를 모듈형으로 결합하는 다중 에이전트 메모리 시스템 |
| **Preference-Aware Memory** | 2025.10 | N/A | Haoran Sun | 장기 상호작용 중 사용자 선호도 변화를 감지하여 메모리를 동적 업데이트 |

## 4. Management, Benchmark & Privacy

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **MemoryAgentBench** | 2026.03 | ICLR 2026 | Yuanzhe Hu | 검색 정확도, 테스트 타임 학습, 장기 문맥 이해, 선택적 망각 등 4대 역량 평가 벤치마크 |
| **Memory Mgmt Impact** | 2025.05 | Harvard / UGA / MSU | Zidi Xiong | 메모리 추가/삭제 전략이 장기 성능에 미치는 영향 분석, 오류 전파 완화 전략 제시 |
| **Privacy Risks in Memory** | 2025.06 | ACL 2025 | Bo Wang | 악의적 프롬프트를 통한 메모리 유출 취약점 증명 및 방어 필요성 제기 |
| **Memory Survey** | 2025.12 | NUS / RUC / Fudan | Yuyang Hu | 메모리 형성/진화/검색 분류, RL 통합, 멀티 에이전트 메모리 등 종합 서베이 (100p) |

## 5. Prompt & Architecture Auto-Optimization

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **MASS** | 2026.01 | ICLR 2026 / Google | Han Zhou | 프롬프트 최적화와 토폴로지 탐색을 인터리빙하여 멀티 에이전트 시스템을 자동 설계 |
| **AgentSquare** | 2024.10 | ICLR 2025 / Tsinghua | Yu Shang | Planning/Reasoning/Tool Use/Memory 4개 모듈의 진화·재조합으로 최적 에이전트 자동 탐색 |

## 6. RL-based Reasoning & Tool Use

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **Turn-Level Credit** | 2025.05 | UMN / Texas A&M | Quan Wei | 멀티턴 에이전트 RL 학습에서 턴 단위 보상 할당(MT-PPO/MT-GRPO)으로 fine-grained 최적화 |

## 7. Self-Reflection & Knowledge Graph Fusion

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **Self-Reflective KG** | 2025.05 | USTC | Jiajun Zhu | KG 기반 QA에서 자기 성찰적 계획을 통해 reasoning path 신뢰성 향상 |
| **AgentRefine** | 2025.01 | ICLR 2025 / BUPT | Dayuan Fu | 합성 환경에서 오류-수정 trajectory로 학습하여 에이전트 일반화 능력 강화 |

## 8. Context Engineering & Long-Context

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **ACE** | 2026.01 | ICLR 2026 / Stanford | Qizheng Zhang | 컨텍스트를 진화하는 플레이북으로 관리, Generator-Reflector-Curator 3단계로 Context Collapse 방지 |
| **Chain of Agents** | 2024.06 | Google Cloud AI | Yusen Zhang | 긴 컨텍스트를 청크로 분할 후 Worker-Manager 다중 에이전트 순차 협업으로 처리 |
| **Eval Long-Context Reasoning** | 2024.12 | NeurIPS 2025 Workshop / UMich | Andy Chung | WebAgent의 긴 컨텍스트에서 추론 성능 급락(40%→10% 미만) 실증 및 iRAG 제안 |

## 9. Multi-Agent Collaboration & Creativity

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **Multi-Agent Collab Survey** | 2025 | UCC / TCD / PNU | Khanh-Tung Tran | MAS 협업 메커니즘을 Actors/Types/Structures/Strategies/Coordination 5차원으로 분류 |
| **Creativity in MAS** | 2025.05 | NTU | Yi-Cheng Lin | MAS에서의 창의성을 주체성 스펙트럼·생성 기법·평가 방법으로 체계화한 최초 서베이 |

## 10. Test-Time Compute & Tool Use

| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
|------|-----------|---------------|-------|---------------|
| **Test-Time Compute Survey** | 2025.06 | Soochow / NUS / Ant | Yixin Ji | System-1→System-2 전환에서 test-time compute의 역할을 TTA와 TTR로 체계적 분류 |
| **BUTTON** | 2025 | ICLR 2025 / Baichuan | Mingyang Chen | Bottom-Up 지시 구성 + Top-Down 궤적 생성으로 멀티턴 function calling 데이터 합성 |
| **ToolACE** | 2025 | ICLR 2025 / Huawei | Weiwen Liu | 자기 진화 API 합성(26,507개) + 모델 인식 복잡도 조절로 8B 모델이 GPT-4급 function calling 달성 |

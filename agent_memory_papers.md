# LLM Agent Memory 관련 논문 정리

## 1. Knowledge Graph & Graph RAG

| 논문 | 발표 | 핵심 아이디어 |
|------|------|---------------|
| **A-MEM** | NeurIPS 2025 | 제텔카스텐 방식으로 메모리 간 링크를 자율 생성, 지식 네트워크를 동적으로 진화 |
| **MAGMA** | 2026.01 | Semantic/Temporal/Causal/Entity 등 다중 그래프 뷰로 메모리 분리 저장 및 의도 기반 탐색 |
| **AriGraph** | IJCAI 2025 | Episodic + Semantic 메모리를 결합해 지식 그래프 형태의 World Model을 자율 구축 |

## 2. Meta-Learning & Evolution

| 논문 | 발표 | 핵심 아이디어 |
|------|------|---------------|
| **MemEvolve** | 2025.12 | 경험 축적(내부 루프) + 메모리 코드 구조 최적화(외부 루프)로 메모리 시스템 자체를 메타 진화 |
| **ALMA** | 2026.02 | 메타 에이전트가 DB 스키마와 검색/업데이트 메커니즘을 실행 가능한 코드로 자동 생성 |
| **Automated Design of Agentic Systems** | ICLR 2025 | Meta Agent Search 알고리즘으로 에이전트 아키텍처를 스스로 프로그래밍 |

## 3. Long-term & Multi-Agent

| 논문 | 발표 | 핵심 아이디어 |
|------|------|---------------|
| **SeCom** | ICLR 2025 (Microsoft) | Turn/Session 단위 메모리 분할의 한계를 밝히고 최적 메모리 구성 단위를 연구 |
| **MIRIX** | 2025.07 | 다양한 메모리 타입과 에이전트를 모듈형으로 결합하는 다중 에이전트 메모리 시스템 |
| **Preference-Aware Memory Update** | 2025.10 | 장기 상호작용 중 사용자 선호도 변화(Preference Drift)를 감지하여 메모리를 동적 업데이트 |

## 4. Management, Benchmark & Privacy

| 논문 | 발표 | 핵심 아이디어 |
|------|------|---------------|
| **MemoryAgentBench** | ICLR 2026 | 검색 정확도, 테스트 타임 학습, 장기 문맥 이해, 선택적 망각 등 4대 역량 평가 벤치마크 |
| **How Memory Management Impacts LLM Agents** | 2025.05 | 메모리 추가/삭제 전략이 장기 성능에 미치는 영향 분석, 오류 전파 완화 전략 제시 |
| **Unveiling Privacy Risks in LLM Agent Memory** | ACL 2025 | 악의적 프롬프트를 통한 메모리 유출(Memory Leakage) 취약점 증명 및 방어 필요성 제기 |
| **Memory in the Age of AI Agents: A Survey** | 2025.12 | 메모리 형성/진화/검색 분류, RL 통합, 멀티 에이전트 메모리 등 종합 서베이 (100p) |

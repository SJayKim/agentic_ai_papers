# G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems

> **논문 정보**: Guibin Zhang, Muxin Fu, Guancheng Wan, Miao Yu, Kun Wang, Shuicheng Yan (NUS, Tongji University, UCLA, A*STAR, NTU)
> **arXiv**: 2506.07398 (2025.06)
> **코드**: https://github.com/bingreeky/GMemory

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 다중 에이전트 시스템(MAS)은 단일 에이전트 대비 10배 이상 긴 상호작용 궤적을 생성하지만, 기존 MAS 메모리 메커니즘은 (1) 최종 결과물만 저장하는 수준으로 에이전트 간 협업 과정을 무시하고, (2) 에이전트별 역할 맞춤형 메모리가 부재하여 자기 진화(self-evolving) 능력이 제한된다. |
| **Motivation** | 단일 에이전트용 메모리(RAG 기반 유사도 검색)를 MAS에 직접 이식하면 과도한 컨텍스트 길이와 역할 무관한 정보로 인해 오히려 성능이 하락(MemoryBank: -2.65%, ChatDev-M: -10.45%)하는 경우가 빈번하다. 조직 기억 이론(Organizational Memory Theory)에 기반한 계층적 메모리 설계가 필요하다. |
| **Limitation** | 저자 언급: 현재 G-Memory는 태스크 시작 시 1회만 호출되며, 매 대화 라운드마다의 동적 호출은 미구현. 독자 관점: 임베딩 기반 초기 검색(MiniLM)의 품질에 의존하며, Insight 생성이 LLM 호출에 전적으로 의존하여 노이즈 축적 가능성 존재. 또한 에이전트 수 증가 시 역할별 메모리 필터링의 확장성 검증 부족. |

---

## Method

1. **3계층 그래프 메모리 아키텍처** (조직 기억 이론 기반)
   - **Interaction Graph (최하위)**: 각 에이전트의 발화(utterance)를 노드로, 시간적·인과적 관계를 엣지로 기록. 에이전트 ID와 텍스트 내용을 포함하는 세밀한 협업 궤적
   - **Query Graph (중간층)**: 과거 처리한 쿼리를 노드로, 쿼리 간 의미적 관계를 엣지로 연결. 각 노드는 (원본 쿼리, 성공/실패 상태, 연결된 Interaction Graph)의 삼중 구조
   - **Insight Graph (최상위)**: 여러 쿼리에서 추출한 일반화된 교훈/전략을 노드로 저장. 하이퍼엣지로 Insight 간 관계를 쿼리 컨텍스트와 함께 인코딩

2. **양방향 메모리 탐색 (Bi-directional Traversal)**
   - **Coarse-grained Retrieval**: MiniLM 임베딩으로 유사 쿼리 top-k 검색 후, Query Graph에서 1-hop 이웃 확장
   - **Upward Traversal** (Query → Insight): 검색된 쿼리와 연결된 Insight 노드를 수집하여 고수준 전략적 가이던스 제공
   - **Downward Traversal** (Query → Interaction): LLM 기반 관련도 평가(RLLM)로 상위 M개 쿼리 선정, 각 Interaction Graph를 LLM 스파시파이어로 핵심 대화만 추출
   - **역할별 메모리 배정**: 연산자 Φ가 각 에이전트의 Role에 맞게 Insight와 Interaction snippet을 필터링하여 개인화된 메모리 제공

3. **계층적 메모리 업데이트**
   - 태스크 완료 후 환경 피드백(성공/실패)을 받아 3개 층 모두 업데이트
   - Interaction 층: 새 궤적 그래프 저장
   - Query 층: 새 쿼리 노드 추가 및 관련 쿼리/Insight 지원 쿼리와 엣지 연결
   - Insight 층: 새 Insight 생성(요약 함수 J) 및 기존 Insight의 지원 쿼리 집합 확장

---

## Key Contribution

1. **MAS 전용 메모리 아키텍처의 필요성 실증**: 단일 에이전트 메모리를 MAS에 이식하면 오히려 성능이 하락할 수 있음을 5개 벤치마크에서 체계적으로 입증
2. **3계층 그래프 기반 플러그앤플레이 메모리 모듈**: Insight/Query/Interaction의 계층적 그래프 구조로 MAS 협업 궤적을 효율적으로 압축·관리하며, 기존 MAS 프레임워크에 수정 없이 통합 가능
3. **역할 인식 양방향 탐색**: 에이전트별 역할에 맞춘 메모리 필터링과, 추상적 Insight↔구체적 Interaction을 동시에 제공하는 양방향 탐색 설계

---

## Experiment & Results

- **벤치마크**: ALFWorld, SciWorld (embodied action), PDDL (game), HotpotQA, FEVER (knowledge QA)
- **MAS 프레임워크**: AutoGen, DyLAN, MacNet
- **LLM 백본**: GPT-4o-mini, Qwen-2.5-7b, Qwen-2.5-14b
- **Baseline**: No-memory, Voyager, MemoryBank, Generative Agents, MetaGPT-M, ChatDev-M, MacNet-M

**핵심 결과 (GPT-4o-mini)**:
- AutoGen + G-Memory: 평균 57.18% (no-memory 48.27% 대비 +8.91%)
- MacNet + G-Memory: 평균 51.95% (no-memory 42.01% 대비 +9.94%)
- ALFWorld에서 최대 20.89% 향상 (MacNet + Qwen-2.5-14b: 58.21% → 79.10%)
- Knowledge QA에서 최대 10.12% 향상

**토큰 효율성**: PDDL+AutoGen에서 +10.32% 성능 향상에 1.4×10⁶ 토큰 추가 소모 (MetaGPT-M은 2.2×10⁶ 토큰으로 +4.07%만 달성)

**Ablation**: Insight만 제공 시 평균 -3.82%~-4.47%, Interaction만 제공 시에도 성능 하락 → 두 계층 모두 필수. 1-hop 확장과 k∈{1,2}가 최적이며, 과도한 확장(2-3 hop)은 노이즈 유입으로 성능 저하.

# MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents

> **논문 정보**: Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li (University of Texas at Dallas, University of Florida)
> **arXiv**: 2601.03236 (2026.01)
> **코드**: https://github.com/FredJiang0324/MAMGA

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 Memory-Augmented Generation(MAG) 시스템은 시맨틱 유사도 기반의 단일 메모리 저장소에 의존하여, 시간적·인과적·엔티티 정보가 뒤섞인다. 이로 인해 쿼리 의도와 검색 증거 간 정렬이 어렵고, 복잡한 추론(Why, When 질문)에서 정확도가 떨어진다. |
| **Motivation** | LLM 에이전트가 장기 상호작용에서 일관성을 유지하려면, 단순 유사도 검색을 넘어 "왜 발생했는가(인과)", "언제 발생했는가(시간)", "누가 관련되었는가(엔티티)"를 구조적으로 모델링해야 한다. 기존 그래프 기반 접근(GraphRAG, Zep 등)도 associative proximity에 의존하여 mechanistic dependency를 포착하지 못한다. |
| **Limitation** | (1) 4개 그래프 유지에 따른 저장·계산 오버헤드가 대규모 배포에서 제약이 될 수 있다. (2) 인과 그래프 구축이 LLM 추론에 의존하므로 비용과 정확도 트레이드오프 존재. (3) 텍스트 기반 대화/QA에 검증이 집중되어, 멀티모달·실시간 에이전트 환경에서의 검증이 부족하다. (4) Intent Classification이 {WHY, WHEN, ENTITY} 3가지로 고정되어 복합 의도 쿼리에서 한계가 있을 수 있다. |

---

## Method

MAGMA는 메모리를 **4개 직교 관계 그래프**(Semantic, Temporal, Causal, Entity)로 분리 표현하고, **의도 기반 검색 정책**으로 쿼리에 맞는 그래프를 선택적으로 탐색하는 아키텍처다.

1. **Data Structure Layer (메모리 기판)**
   - 각 메모리 노드를 `n = ⟨c, τ, v, A⟩`로 표현 (내용, 타임스탬프, 임베딩, 속성)
   - **Temporal Graph**: 시간 순서 쌍 `(n_i, n_j)` where `τ_i < τ_j` — 불변의 시간 체인
   - **Causal Graph**: LLM 추론으로 인과 관계 추출 — "Why" 쿼리 지원
   - **Semantic Graph**: 코사인 유사도 > θ인 노드 연결
   - **Entity Graph**: 이벤트-엔티티 간 연결 — 시간적으로 떨어진 동일 엔티티 추적

2. **Query Process (의도 기반 계층적 검색)**
   - **Stage 1 - Query Analysis**: 의도 분류(`WHY/WHEN/ENTITY`), 시간 파싱, 임베딩+키워드 추출
   - **Stage 2 - Anchor Identification**: RRF(Reciprocal Rank Fusion)로 벡터 검색과 키워드 검색 결합, 앵커 노드 선정
   - **Stage 3 - Adaptive Traversal**: 의도에 따라 가중치 벡터 `w_Tq`를 적용한 빔 서치로 그래프 탐색. `score = exp(λ1·ϕ(r,Tq) + λ2·sim(v,q))`로 구조적 정렬과 의미적 유사도 동시 활용
   - **Stage 4 - Narrative Synthesis**: 검색된 서브그래프를 위상 정렬(시간순/인과순)로 선형화하여 프롬프트 구성

3. **Memory Evolution (이중 스트림)**
   - **Fast Path (Synaptic Ingestion)**: 이벤트 분할, 벡터 인덱싱, 시간 체인 업데이트 — LLM 호출 없이 즉시 처리
   - **Slow Path (Structural Consolidation)**: 비동기 워커가 큐에서 이벤트를 꺼내 인접 노드 분석 후 인과·엔티티 링크를 추론·추가

기존 단일 그래프 기반 방법과 달리, 관계 유형별로 그래프를 분리함으로써 해석 가능한 추론 경로를 제공한다.

---

## Key Contribution

1. **다중 관계 그래프 아키텍처**: 시맨틱·시간·인과·엔티티 4개 직교 그래프로 메모리를 분리 표현하여, 각 관계 유형에 특화된 추론을 가능하게 함.
2. **Adaptive Traversal Policy**: 쿼리 의도에 따라 그래프 탐색 가중치를 동적으로 조정하는 정책 기반 검색. 불필요한 그래프 영역을 pruning하여 검색 지연과 토큰 소비 감소.
3. **이중 스트림 메모리 진화**: 지연 민감 이벤트 수집(Fast Path)과 비동기 구조 보강(Slow Path)을 분리하여, 응답성을 유지하면서 관계 구조를 점진적으로 심화.
4. **장기 추론 SOTA**: LoCoMo와 LongMemEval에서 기존 SOTA 대비 일관된 성능 향상 달성.

---

## Experiment & Results

**데이터셋**: (1) LoCoMo — 장기 대화 QA, 5개 카테고리 (Multi-Hop, Temporal, Open-Domain, Single-Hop, Adversarial). (2) LongMemEval — 극단적 컨텍스트 길이(101K 토큰) 하에서 6가지 질문 유형 평가.

**비교 대상**: Full Context, A-MEM, MemoryOS, Nemori (모두 GPT-4o-mini 백본)

**LoCoMo 결과 (LLM-as-a-Judge)**:
- MAGMA Overall: **0.700** vs Nemori 0.590, A-MEM 0.580, MemoryOS 0.553, Full Context 0.481
- Adversarial: MAGMA **0.742** vs A-MEM 0.616, Nemori 0.325 — 인과·엔티티 일관 경로가 의미적 유사 함정을 회피
- Temporal: MAGMA **0.650** vs Nemori 0.649, A-MEM 0.474
- Single-Hop: MAGMA **0.776** vs Nemori 0.764, A-MEM 0.653

**LongMemEval 결과** (101K 토큰 컨텍스트):
- MAGMA 평균 **61.2%** vs Nemori 56.2%, Full Context 55.0%
- single-session-preference: MAGMA **73.3%** vs Nemori 62.7%
- MAGMA 토큰 사용량 0.7~4.2K vs Nemori 3.7~4.8K vs Full Context 101K

**효율성**: 그래프 분리와 의도 기반 pruning으로 검색 지연 및 토큰 소비를 줄이면서도 추론 정확도 향상. Fast Path에서 LLM 호출 없이 이벤트를 즉시 수집하여 응답 지연 최소화.

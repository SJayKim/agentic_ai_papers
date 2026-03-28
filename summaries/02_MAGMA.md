# MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents

> **논문 정보**: Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li (University of Texas at Dallas, University of Florida)
> **arXiv**: 2601.03236 (2026.01) | **학회**: 미확인
> **코드**: https://github.com/FredJiang0324/MAMGA

---

## Problem

기존 Memory-Augmented Generation(MAG) 시스템은 과거 상호작용을 모놀리식(monolithic) 저장소에 보관하고, 의미적 유사도(semantic similarity), 최신성(recency), 휴리스틱 점수에 주로 의존하여 검색을 수행한다. 이러한 단일 차원 검색은 "무엇이 일어났는가(what)"는 찾을 수 있지만, "왜 일어났는가(why)"에 대한 인과적 추론이 불가능하다. A-MEM은 Zettelkasten 스타일 메모리를 제공하지만 검색이 임베딩 유사도에 의존하고, MemoryOS는 의미 중심 계층 저장을 사용하지만 관계적 차원을 명시적으로 분리하지 않는다. 시간적(temporal), 인과적(causal), 엔티티(entity) 관계가 하나의 저장소에 뒤엉켜 있어 해석 가능성과 쿼리 의도-검색 증거 간 정렬이 저하되며, 이는 복잡한 장기(long-horizon) 추론 태스크에서 정확도 하락으로 직결된다. 또한 LLM의 고정 길이 컨텍스트 윈도우는 attention dilution과 "lost-in-the-middle" 현상을 야기하여 장거리 의존성 처리를 근본적으로 제한한다.

---

## Motivation

핵심 관찰은 에이전트의 기억이 단일 유사도 공간이 아니라, 의미·시간·인과·엔티티라는 서로 직교(orthogonal)하는 네 가지 관계적 차원으로 구성된다는 점이다. "왜?"라는 질문에는 인과 그래프를, "언제?"에는 시간 그래프를, "누가?"에는 엔티티 그래프를 우선 탐색해야 정확한 답을 얻을 수 있다. 이를 위해 메모리 표현(representation)과 검색 로직(retrieval logic)을 분리(decouple)하면, 쿼리 의도에 따라 적응적으로 관련 관계 뷰를 선택하고 탐색할 수 있다. 또한 인간의 기억 시스템에서 영감을 받아, 지연에 민감한 즉각 기록(synaptic ingestion)과 계산 집약적인 구조 정제(structural consolidation)를 이중 스트림으로 분리함으로써, 반응성과 관계적 깊이를 동시에 확보할 수 있다는 직관에 기반한다.

---

## Method

MAGMA는 세 개의 논리적 레이어로 구성된다.

1. **Data Structure Layer (다중 그래프 메모리 기판)**: 시간 변이 방향 다중 그래프 G_t = (N_t, E_t)로 형식화된다. 각 이벤트 노드 n_i = <c_i, τ_i, v_i, A_i>는 내용, 타임스탬프, 밀집 임베딩, 메타데이터 속성을 포함한다. 엣지 공간은 네 가지 관계 그래프로 분할된다: (a) **Temporal Graph** — τ_i < τ_j인 엄격 순서 쌍, (b) **Causal Graph** — LLM 기반 추론으로 논리적 수반 관계를 나타내는 방향 엣지, (c) **Semantic Graph** — 코사인 유사도 임계값 θ_sim 초과 시 연결되는 무방향 엣지, (d) **Entity Graph** — 이벤트를 추상 엔티티 노드에 연결하여 시간선 간 객체 영속성을 보장한다.

2. **Query Process (적응적 계층적 검색)**: 4단계 파이프라인으로 동작한다.
   - **Stage 1 — Query Analysis & Decomposition**: 쿼리를 의도 분류(T_q ∈ {WHY, WHEN, ENTITY}), 시간 구간 파싱, 밀집 임베딩 + 희소 키워드 추출로 분해한다.
   - **Stage 2 — Multi-Signal Anchor Identification**: 벡터 검색, 키워드 매칭, 시간 필터링 결과를 Reciprocal Rank Fusion(RRF)으로 융합하여 앵커 노드 집합을 선정한다.
   - **Stage 3 — Adaptive Traversal Policy**: 앵커에서 출발하는 휴리스틱 빔 서치를 수행한다. 전이 점수 S(n_j|n_i, q) = exp(λ_1·ϕ(type(e_ij), T_q) + λ_2·sim(v_j, q))를 계산하며, ϕ는 쿼리 의도에 따라 엣지 유형별 가중치를 동적으로 부여한다. 상위-k 노드를 유지하며 예산 한도 도달 시 조기 종료한다.
   - **Stage 4 — Narrative Synthesis**: 검색된 서브그래프를 위상 정렬(시간순 또는 인과순)하고, 타임스탬프·내용·참조 ID를 포함하는 구조화 블록으로 직렬화하며, relevance 점수 기반 토큰 예산 배분으로 저관련 노드를 요약 코드로 압축한다.

3. **Write/Update Process (이중 스트림 메모리 진화)**:
   - **Fast Path (Synaptic Ingestion)**: 이벤트 분할, 벡터 인덱싱, temporal backbone 업데이트를 비차단(non-blocking)으로 수행하여 즉각 반응성을 유지한다.
   - **Slow Path (Structural Consolidation)**: 비동기 워커가 큐에서 이벤트를 디큐잉하고, 2-hop 이웃 컨텍스트를 LLM에 입력하여 잠재적 인과(causal) 및 엔티티(entity) 링크를 추론·추가한다.

---

## Key Contribution

1. **다중 그래프 메모리 아키텍처**: 의미·시간·인과·엔티티 네 가지 직교 관계 그래프를 통합 기판에서 명시적으로 모델링하여, 기존 모놀리식/단일유사도 메모리의 구조적 한계를 해결한다.
2. **Adaptive Traversal Policy**: 쿼리 의도에 따라 검색 경로를 동적으로 라우팅하는 정책 기반 그래프 탐색으로, 구조적으로 무관한 정보의 유입을 조기 차단하여 지연 시간과 토큰 소비를 동시에 절감한다.
3. **Dual-Stream Memory Evolution**: 지연 민감 경로와 비동기 구조 정제 경로를 분리하여, 실시간 반응성을 유지하면서도 점진적으로 관계적 깊이를 확보하는 메커니즘을 제안한다.
4. **장기 추론 벤치마크에서의 일관된 SOTA 달성**: LoCoMo와 LongMemEval 모두에서 기존 최첨단 에이전트 메모리 시스템을 능가하며, 동시에 추론 효율성도 개선한다.

---

## Experiment & Results

**데이터셋**: (1) LoCoMo — 평균 9K 토큰의 초장문 대화, 시간적·인과적 검색 평가, (2) LongMemEval — 평균 100K+ 토큰의 대규모 스트레스 테스트 벤치마크. **백본 LLM**: gpt-4o-mini. **Baseline**: Full Context, A-MEM, MemoryOS, Nemori.

**LoCoMo 결과 (LLM-as-a-Judge)**: MAGMA는 Overall 0.700으로 Full Context(0.481), A-MEM(0.580), MemoryOS(0.553), Nemori(0.590) 대비 18.6%~45.5% 상대적 우위를 달성했다. Adversarial 카테고리에서 0.742로 가장 큰 격차를 보였고(Nemori 0.325, MemoryOS 0.428), Temporal에서 0.650, Single-Hop에서 0.776을 기록했다.

**LongMemEval 결과**: MAGMA는 평균 정확도 61.2%로 Full Context(55.0%)와 Nemori(56.2%)를 상회했다. single-session-preference에서 73.3%(Full Context 6.7%), single-session-assistant에서 83.9%(Full Context 89.3%)를 달성하면서도, 쿼리당 토큰을 0.7k~4.2k로 유지하여 Full Context의 101K 대비 95% 이상 감소시켰다.

**시스템 효율성**: MAGMA는 쿼리 지연 1.47초로 가장 빠르며(A-MEM 2.26s 대비 약 35% 감소), 쿼리당 토큰 3.37k로 경쟁력 있는 수준을 유지한다. 메모리 빌드 타임은 0.39시간으로 Nemori(0.29h) 다음이다.

**Ablation Study**: Adaptive Policy 제거 시 가장 큰 성능 하락(0.700→0.637, -9%), Causal Links 제거 시 0.644, Temporal Backbone 제거 시 0.647, Entity Links 제거 시 0.666으로, 네 구성 요소 모두 유의미한 기여를 보이며, 특히 정책 기반 탐색과 인과·시간 구조가 핵심임을 확인했다.

---

## Limitation

첫째, 비동기 구조 정제(slow path)에서 생성되는 인과·엔티티 링크의 품질이 기반 LLM의 추론 충실도에 의존하며, 추출 오류와 환각(hallucination)이 잠재적 인과 관계에 전파될 수 있다. 구조화 프롬프트와 보수적 추론 임계값으로 완화하지만 근본적 해결은 아니다. 둘째, 네 가지 관계 그래프와 이중 스트림 처리를 유지하는 데 따른 저장 및 엔지니어링 복잡성이 단순 벡터 메모리 시스템 대비 높아, 극도로 자원이 제한된 환경에서는 적용이 어려울 수 있다. 셋째, 평가가 LoCoMo와 LongMemEval이라는 대화형 벤치마크에 한정되어 있어, 멀티모달 에이전트나 이질적 관찰 스트림 환경에서의 일반화는 검증되지 않았다. 넷째, 독자 관점에서 인과 그래프 구축의 LLM 호출 비용이 메모리 규모에 비례하여 증가하므로, 매우 대규모 장기 상호작용에서의 비용 확장성(cost scalability) 문제가 실용적 배포의 병목이 될 수 있다.

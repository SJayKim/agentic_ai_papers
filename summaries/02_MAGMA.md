# MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents

> **논문 정보**: Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li (University of Texas at Dallas, University of Florida)
> **arXiv**: 2601.03236 (2026.01) | **학회**: 미확인
> **코드**: https://github.com/FredJiang0324/MAMGA

---

## Problem

기존 Memory-Augmented Generation(MAG) 시스템은 과거 상호작용을 모놀리식(monolithic) 저장소나 최소한으로 구조화된 메모리 버퍼에 보관하고, 의미적 유사도(semantic similarity), 최신성(recency), 휴리스틱 점수에 의존해 검색을 수행한다.
이러한 단일 차원 검색은 "무엇이 일어났는가(what)"는 찾을 수 있으나, "왜 일어났는가(why)"에 대한 인과적 추론이 근본적으로 불가능하며 복잡한 장기 추론 태스크에서 정확도 저하를 야기한다.
A-MEM은 Zettelkasten 스타일로 메모리를 점진적 링크로 조직하지만 검색이 임베딩 유사도에만 의존하여 인과 관계를 누락하고, MemoryOS는 계층 저장을 제공하지만 관계적 차원을 명시적으로 분리하지 않는다.
Nemori와 같은 그래프 기반 접근도 서사(narrative) 중심이라 시간·인과·엔티티 관계가 하나의 저장소에 엉켜 있어 해석 가능성과 쿼리 의도-검색 증거 간 정렬이 심각하게 저하된다.
또한 LLM의 고정 길이 컨텍스트 윈도우는 attention dilution, 위치 임베딩 한계, "lost-in-the-middle" 현상을 일으켜 장거리 의존성 처리를 구조적으로 제약한다.
결과적으로 기존 시스템은 표면적 의미 매칭에 강한 반면, 반드시 서로 다른 세션에 흩어진 증거를 조합해야 하는 멀티홉·시간 추론·적대적(adversarial) 쿼리에서 취약함을 드러낸다.
이 문제는 "무엇"을 찾는 연상 근접성(associative proximity)과 "왜"를 설명해야 하는 기계적 의존성(mechanistic dependency) 사이의 구조적 괴리에서 비롯된다.

---

## Motivation

핵심 관찰은 에이전트의 기억이 단일 유사도 공간이 아니라, 의미(semantic)·시간(temporal)·인과(causal)·엔티티(entity)라는 서로 직교(orthogonal)하는 네 가지 관계적 차원으로 자연스럽게 분해된다는 점이다.
"왜?" 질문에는 인과 그래프를, "언제?"에는 시간 그래프를, "누가?"에는 엔티티 그래프를 우선 탐색해야 쿼리 의도와 검색 증거가 일치하며 정확한 답을 얻을 수 있다.
이를 위해 메모리 표현(representation)과 검색 로직(retrieval logic)을 분리(decouple)하면, 쿼리 의도에 따라 적응적으로 관련 관계 뷰를 선택하고 그 뷰만 정밀하게 탐색할 수 있어 불필요한 정보의 유입을 조기에 차단할 수 있다.
또한 인간 기억의 상보적 학습 시스템(Complementary Learning Systems) 이론에서 영감을 받아, 지연에 민감한 즉각 기록(synaptic ingestion)과 계산 집약적 구조 정제(structural consolidation)를 이중 스트림으로 분리하면, 반응성과 관계적 깊이를 동시에 확보할 수 있다.
즉 쓰기 경로에서 LLM 추론을 비차단(non-blocking)으로 분리하면 에이전트의 대화 지연을 유지하면서도 백그라운드에서 점진적으로 인과·엔티티 링크를 밀도 있게 구축할 수 있다는 것이 설계 직관이다.
마지막으로 정책 기반 그래프 탐색(policy-guided traversal)은 시간순 정렬·위상 정렬을 통해 "원인이 결과보다 먼저 제시되는" 명시적 증거 체인을 LLM에게 전달하여, 자유 생성이 아니라 증거 해석자(interpreter)로 동작하도록 유도한다.

---

## Method

MAGMA는 세 개의 논리적 레이어로 구성되며, 데이터 구조·쿼리 처리·쓰기/갱신 프로세스가 상호작용한다.

1. **시간 변이 방향 다중 그래프 형식화**: 메모리를 G_t = (N_t, E_t)로 정의하며, 각 이벤트 노드 n_i = ⟨c_i, τ_i, v_i, A_i⟩는 내용, 타임스탬프, d차원 밀집 임베딩, 메타데이터 속성(엔티티 참조·시간 단서 등)을 담는다.
2. **네 가지 직교 관계 그래프로 엣지 공간 분할**: (a) Temporal Graph E_temp — τ_i < τ_j인 엄격 순서 쌍의 불변 체인, (b) Causal Graph E_causal — S(n_j|n_i, q) > δ일 때 생성되는 방향 엣지로 "왜" 쿼리 지원, (c) Semantic Graph E_sem — cos(v_i, v_j) > θ_sim 무방향 엣지, (d) Entity Graph E_ent — 이벤트를 추상 엔티티 노드에 연결해 세션 간 객체 영속성을 유지한다.
3. **Stage 1 — Query Analysis & Decomposition**: 경량 분류기가 쿼리를 T_q ∈ {WHY, WHEN, ENTITY}로 매핑하고, 시간 태거가 "last Friday" 같은 상대 표현을 절대 타임스탬프 [τ_s, τ_e]로 해석하며, 동시에 밀집 임베딩 q⃗과 희소 키워드 q_key를 추출한다.
4. **Stage 2 — Multi-Signal Anchor Identification**: 벡터 검색·키워드 매칭·시간 필터링 결과를 Reciprocal Rank Fusion으로 융합해 S_anchor = TopK(∑_m 1/(k + r_m(n))) (k=60)을 계산하고 앵커 노드 집합을 선정한다.
5. **Stage 3 — Adaptive Traversal Policy**: 앵커에서 출발하는 휴리스틱 빔 서치가 전이 점수 S(n_j|n_i, q) = exp(λ_1·ϕ(type(e_ij), T_q) + λ_2·sim(v⃗_j, q⃗))을 계산한다. 구조 정렬 함수 ϕ(r, T_q) = w_{T_q}^⊤·1_r는 쿼리 의도에 따라 엣지 유형별 가중치를 부여하여, "왜" 쿼리에는 CAUSAL 엣지(w=3.0~5.0)를, ENTITY 쿼리에는 엔티티 엣지(w=2.5~6.0)를 우선한다.
6. **빔 유지와 예산 기반 조기 종료**: 각 단계에서 누적 점수 상위 k 노드만 유지하고 감쇠(decay) γ을 적용하며, 방문 노드가 Budget(Max Nodes=200, Max Depth=5 hops)에 도달하면 탐색을 중단해 토큰 소비를 억제한다.
7. **Stage 4a — Topological Ordering**: T_q=WHEN이면 타임스탬프 τ_i 기준 정렬, T_q=WHY이면 E_causal에 대해 위상 정렬을 수행해 원인이 결과에 선행하도록 컨텍스트를 배치한다.
8. **Stage 4b — Context Scaffolding with Provenance**: 각 노드를 `[<t:τ_i> n_i.content <ref:n_i.id>]` 구조 블록으로 직렬화해 환각을 줄이고 LLM이 증거 해석자로 동작하도록 강제한다.
9. **Stage 4c — Salience-Based Token Budgeting**: S(n_j|n_i, q) 점수 기반으로 저관련 노드를 "...3 intermediate events..." 같은 압축 코드로 요약하고, 고관련 노드는 원문을 유지하여 고정 컨텍스트 예산 내에서 정보 밀도를 극대화한다.
10. **Fast Path (Synaptic Ingestion)**: 사용자 상호작용 I에 대해 이벤트 분할·임베딩 인코딩·벡터 DB 인덱싱·temporal backbone(n_{t-1} → n_t) 갱신을 비차단으로 실행하고, 노드 ID를 비동기 큐에 enqueue한 뒤 즉시 반환해 LLM 추론 없이 쓰기 경로의 지연을 일정하게 유지한다.
11. **Slow Path (Structural Consolidation)**: 백그라운드 워커가 큐에서 이벤트를 dequeue한 뒤 2-hop 이웃 N(n_t)를 수집하고, 구조화 프롬프트를 LLM Φ에 입력해 E_new = Φ_reason(N(n_t), H_history)로 잠재적 인과·엔티티 링크를 추론해 그래프에 추가한다.
12. **적응적 가중치 하이퍼파라미터**: λ_1 = 1.0(구조 계수 고정), λ_2 ∈ [0.3, 0.7](의미 계수), w_entity ∈ [2.5, 6.0], w_temporal ∈ [0.5, 4.0], w_causal ∈ [3.0, 5.0], Drop Threshold 0.15, Vector Top-K 20으로 설정되어 쿼리 의도별로 동적으로 이동한다.

---

## Key Contribution

1. **다중 그래프 메모리 아키텍처**: 의미·시간·인과·엔티티 네 가지 직교 관계 그래프를 통합 기판에서 명시적으로 모델링함으로써, 단일 유사도 공간에 관계가 뒤섞여 "왜"를 추론하지 못하던 기존 모놀리식 메모리의 구조적 한계를 해결한다.
2. **Adaptive Traversal Policy**: 쿼리 의도를 기반으로 엣지 유형별 가중치를 동적으로 부여하는 정책 기반 빔 서치를 도입하여, 구조적으로 무관하지만 의미적으로 유사한 분산(distractor) 정보의 유입을 조기에 가지치기(prune)하고 지연과 토큰 소비를 동시에 절감한다.
3. **Dual-Stream Memory Evolution**: 지연 민감 Fast Path와 비동기 Slow Path를 분리하여, 에이전트의 대화 반응성을 유지하면서도 LLM 추론 비용이 큰 인과·엔티티 링크 구축을 백그라운드에서 점진적으로 수행해 관계적 깊이를 확보한다.
4. **증거 기반 컨텍스트 합성**: 위상 정렬 + provenance 참조 ID + salience 기반 토큰 예산 배분으로 구조화된 컨텍스트를 구성해, LLM을 자유 생성자가 아닌 증거 해석자로 유도함으로써 grounding 오류를 줄인다.
5. **장기 추론 벤치마크에서 일관된 SOTA**: LoCoMo와 LongMemEval 모두에서 기존 최첨단 에이전트 메모리 시스템을 정확도와 효율성 양면에서 동시에 능가하여, 관계적 구조화가 flat 메모리보다 본질적으로 우월함을 실증한다.

---

## Experiment

**데이터셋**: (1) LoCoMo — 평균 9K 토큰 초장문 대화, 시간·인과 검색 평가, 총 1,986개 질의(Single-Hop 841, Adversarial 446, Temporal 321, Multi-Hop 282, Open Domain 96), (2) LongMemEval — 평균 100K+ 토큰 스트레스 테스트 벤치마크.
**백본 LLM**: gpt-4o-mini(temperature=0.0), 임베딩은 all-MiniLM-L6-v2(384d) 또는 text-embedding-3-small(1536d). **Baseline**: Full Context, A-MEM, MemoryOS, Nemori(모두 동일 백본).

**LoCoMo 결과 (LLM-as-a-Judge)**: MAGMA는 Overall 0.700으로 Full Context(0.481), A-MEM(0.580), MemoryOS(0.553), Nemori(0.590) 대비 **18.6%~45.5% 상대 우위**를 달성했다.
Adversarial 카테고리에서 0.742로 가장 큰 격차를 보였고(Nemori 0.325, MemoryOS 0.428), Temporal 0.650, Single-Hop 0.776, Open-Domain 0.517, Multi-Hop 0.528을 기록했다.
Adversarial 강점은 Adaptive Traversal Policy가 의미적으로 유사하지만 구조적으로 무관한 distractor를 회피한 결과다.

**LongMemEval 결과**: MAGMA는 평균 정확도 **61.2%**로 Full Context(55.0%)와 Nemori(56.2%)를 상회했다.
single-session-preference 73.3%(Full Context 6.7%, Nemori 62.7%)에서 가장 큰 격차를 보였고, temporal-reasoning 45.1%, knowledge-update 66.7%, single-session-assistant 83.9%를 달성했다.
토큰 사용량은 쿼리당 **0.7k~4.2k**로 Full Context의 **101K 대비 95% 이상 감소**시켰으며, 정확도를 유지하면서 추론 비용을 대폭 절감했다.

**시스템 효율성**: 쿼리 지연 **1.47초**로 A-MEM(2.26s), Nemori(2.59s), MemoryOS(32.68s), Full Context(1.74s) 중 가장 빠르며, A-MEM 대비 약 35% 감소했다.
쿼리당 토큰은 3.37k(A-MEM 2.62k, Nemori 3.46k, MemoryOS 4.76k), 메모리 빌드 타임 0.39h(Nemori 0.29h, A-MEM 1.01h, MemoryOS 0.91h)로 모든 지표가 경쟁력 있다.

**Ablation Study (LoCoMo Judge/F1/BLEU-1)**: Full 0.700 / 0.467 / 0.378 기준으로 Adaptive Policy 제거 시 0.637 / 0.413 / 0.357 (-9%)로 가장 큰 하락, Causal Links 제거 0.644, Temporal Backbone 제거 0.647, Entity Links 제거 0.666 순으로, 네 구성요소 모두 유의하며 정책 기반 탐색과 인과·시간 구조가 가장 핵심임을 확인했다.

**Case Study**: 엔티티 중심 회상(violin/clarinet 통합), 멀티홉 산술("적어도 3명" 추론), 시간 접지("yesterday" → 2023-10-19 정규화)에서 baseline이 요약으로 세부 사항을 잃거나 표면 매칭에 그친 반면 MAGMA는 그래프 탐색으로 정답을 합성했다.

---

## Limitation

첫째, 저자들은 비동기 구조 정제(slow path)에서 생성되는 인과·엔티티 링크 품질이 기반 LLM의 추론 충실도에 종속됨을 인정한다.
추출 오류와 환각(hallucination)이 잠재적 인과 관계에 전파될 수 있으며, 구조화 프롬프트와 보수적 추론 임계값(δ, Drop Threshold 0.15)으로 완화하지만 근본적 해결은 아니다.
둘째, 네 가지 관계 그래프와 이중 스트림 처리를 유지하는 저장 및 엔지니어링 복잡성이 단순 벡터 메모리 시스템 대비 높아, 극도로 자원이 제한된 엣지 환경에서는 적용이 어렵다.
셋째, 평가가 LoCoMo와 LongMemEval이라는 장문 대화 벤치마크에 한정되어 있어, 멀티모달 에이전트나 이질적 관찰 스트림(예: 비전·로보틱스 환경)에서의 일반화는 검증되지 않았으며 추가 보정이 필요할 수 있다.
넷째, 독자 관점에서 인과 그래프 구축의 LLM 호출 비용이 메모리 규모와 2-hop 이웃 크기에 비례하므로, 수십만 건 이상 초대규모 장기 상호작용에서는 비용 확장성(cost scalability)이 실용적 배포의 병목이 될 수 있다.
다섯째, 적응적 가중치 w_{T_q}(λ_2 0.3~0.7, w_causal 3.0~5.0 등 넓은 범위)가 LoCoMo에서 경험적으로 튜닝되어 있어, 도메인이 바뀔 때마다 재조정이 필요하다는 운영상 부담이 존재한다.
여섯째, 쿼리 의도 분류기 T_q ∈ {WHY, WHEN, ENTITY}가 세 클래스에 국한되어, "비교"·"가설적 추론"·"반사실(counterfactual)" 같은 복합 의도를 단일 유형으로 강제 매핑할 때 정책 가중치가 부적합해질 수 있다.

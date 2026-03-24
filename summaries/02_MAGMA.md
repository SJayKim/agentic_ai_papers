# MAGMA: Multi-Graph based Agentic Memory Architecture

> **논문 정보**: "MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents"
> Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li (UT Dallas, University of Florida)
> arXiv:2601.03236v1 [cs.AI], 2026년 1월 6일

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 에이전트는 고정된 컨텍스트 윈도우로 인해 장기 기억을 유지하지 못함. 기존 MAG(Memory-Augmented Generation) 시스템들은 단일 모놀리식 저장소에 의존하며, 주로 의미적 유사도(semantic similarity)만으로 검색을 수행함. 이로 인해 시간적(temporal), 인과적(causal), 엔티티(entity) 관계 정보가 뒤섞여 복잡한 장기 추론 시 검색 정확도가 저하됨. |
| **Motivation** | LLM은 "lost-in-the-middle" 현상, attention dilution, 위치 인코딩 한계로 인해 장거리 의존성 처리가 어렵고, 멀티 세션 일관성 유지가 불가능함. A-Mem은 Zettelkasten 방식으로 메모리를 구성하지만 의미 임베딩 유사도에만 의존해 인과·시간 관계를 놓침. Nemori는 에피소드 분할을 도입했지만 관계 차원이 분리되지 않아 구조적으로 미분화됨. 기존 방법들은 "무엇이 일어났는가(what)"는 검색하지만 "왜(why)" 일어났는가는 추론하지 못함. |
| **Method** | **MAGMA**: 4개의 직교(orthogonal) 관계 그래프(의미·시간·인과·엔티티)로 구성된 멀티 그래프 기반 에이전트 메모리 아키텍처. 3개의 논리적 레이어로 구성됨:<br>1. **데이터 구조 레이어**: 시간 변동 유향 멀티그래프 Gₜ = (Nₜ, Eₜ). 각 이벤트 노드 nᵢ = ⟨cᵢ, τᵢ, vᵢ, Aᵢ⟩(내용, 타임스탬프, 벡터, 속성). 4가지 엣지 타입: Temporal(시간순 chain), Causal(인과 추론으로 생성), Semantic(코사인 유사도 기반 비방향), Entity(엔티티 영속성 연결).<br>2. **쿼리 프로세스**: (a) Query 분석 및 의도 분류(WHY/WHEN/ENTITY), (b) 멀티 시그널 앵커 식별(RRF 융합: 벡터 검색 + 키워드 검색 + 시간 필터), (c) **Adaptive Traversal Policy**: 전이 스코어 S(nⱼ|nᵢ,q) = exp(λ₁·ϕ(edge_type,Tq) + λ₂·sim(n̄ⱼ,q̄))로 의도 적응형 빔 서치 탐색, (d) 그래프 선형화를 통한 컨텍스트 합성 및 Salience 기반 토큰 예산 관리.<br>3. **쓰기/업데이트 프로세스**: 이중 스트림(dual-stream) 메모리 진화 - **Fast Path(Synaptic Ingestion)**: LLM 블로킹 없이 이벤트 분할·벡터 인덱싱·시간 backbone 업데이트만 수행. **Slow Path(Structural Consolidation)**: 비동기 백그라운드에서 LLM으로 인과·엔티티 엣지 추론 후 그래프에 추가. |
| **Key Contribution** | ① 메모리를 의미·시간·인과·엔티티 4개 직교 그래프로 분리 표현하는 멀티그래프 구조 (기존: 단일 벡터 DB 또는 단순 KG). ② 쿼리 의도(WHY/WHEN/ENTITY)에 따라 동적으로 그래프 탐색 경로를 조절하는 Adaptive Traversal Policy. ③ 지연 민감 처리(Fast Path)와 고비용 구조적 추론(Slow Path)을 분리하는 이중 스트림 메모리 진화 메커니즘. ④ 기존 대비 검색 해석 가능성(provenance 포함 직렬화)과 환각(hallucination) 억제 강화. |
| **Experiment/Results** | **LoCoMo 벤치마크** (평균 9K 토큰 대화, LLM-as-a-Judge 평가, gpt-4o-mini 기반):<br>- MAGMA **Overall: 0.700** vs. Nemori 0.590, MemoryOS 0.553, A-MEM 0.580, Full Context 0.481<br>- 상대적 향상폭: 기존 최고 대비 **18.6~45.5%**<br>- Adversarial: MAGMA **0.742** (최고), Temporal: 0.650 (공동 최고), Single-Hop: 0.776 (최고)<br>**LongMemEval 벤치마크** (평균 100K+ 토큰, 극한 컨텍스트 스트레스 테스트):<br>- MAGMA 평균 정확도 **61.2%** vs. Full Context 55.0%, Nemori 56.2%<br>- 토큰 사용량: MAGMA **0.7~4.2K tokens/query** (Full Context 101K 대비 **95% 이상 절감**)<br>**시스템 효율성** (Table 3):<br>- 쿼리 레이턴시: MAGMA **1.47초** (A-MEM 2.26초, MemoryOS 32.68초, Nemori 2.59초 대비 최저)<br>- 토큰/쿼리: MAGMA **3.37K** (A-MEM 2.62K 다음으로 효율적)<br>- 메모리 빌드 시간: MAGMA **0.39시간** (Nemori 0.29시간보다 약간 높음) |
| **Limitation** | ① **LLM 의존성**: 비동기 통합(Slow Path)에서 인과·엔티티 엣지를 LLM으로 추론하므로, LLM의 추출 오류나 환각이 그래프 품질에 전파될 수 있음. ② **저장 및 엔지니어링 복잡도**: 4개 관계 그래프와 이중 스트림 처리는 단순 벡터 전용 시스템 대비 구현·메모리 오버헤드가 높아 자원 제한 환경에서 적용이 어려울 수 있음. ③ **평가 범위 한계**: LoCoMo, LongMemEval은 대화 기반 시간·인과 추론 위주이므로, 멀티모달 에이전트나 이기종 관측 스트림 환경으로의 일반화는 별도 검증 필요. |

---

## 선택 요소

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | 4개 baseline과 비교: (1) **Full Context** (전체 대화 히스토리를 LLM에 직접 입력), (2) **A-MEM** (Zettelkasten 방식 자기진화 메모리), (3) **Nemori** (예측-보정 에피소드 분할 기반 그래프 메모리), (4) **MemoryOS** (계층적 저장 전략의 메모리 OS). LoCoMo Overall Judge 기준: MAGMA 0.700 > Nemori 0.590 (+18.6%) > A-MEM 0.580 > MemoryOS 0.553 > Full Context 0.481. 특히 Adversarial 태스크에서 MAGMA 0.742 vs. A-MEM 0.616으로 압도적 우위. |
| **Ablation Study** | Table 4, LoCoMo Judge 기준 전체 성능 0.700 대비: (1) **w/o Adaptive Policy**: 0.637 (▼0.063, 가장 큰 하락) → 의도 기반 라우팅이 핵심임을 확인. (2) **w/o Causal Links**: 0.644 (▼0.056) → 인과 구조 제거 시 복잡 추론 급격히 저하. (3) **w/o Temporal Backbone**: 0.647 (▼0.053) → 시간 순서 제거 시 인과 제거와 유사한 수준으로 하락, 두 축은 상호 보완적. (4) **w/o Entity Links**: 0.666 (▼0.034, 가장 작은 하락) → 엔티티 영속성 유지에 기여하지만 가장 독립적인 컴포넌트. |

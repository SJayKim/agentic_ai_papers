# 92. Graph-R1: Towards Agentic GraphRAG Framework via End-to-end Reinforcement Learning

> 📄 **저자**: Haoran Luo, Haihong E, Guanting Chen, Qika Lin, Yikai Guo, Fangzhi Xu, Zemin Kuang, Meina Song, Xiaobao Wu, Yifan Zhu, Luu Anh Tuan (Beijing University of Posts and Telecommunications; Nanyang Technological University; National University of Singapore; Beijing Institute of Computer Technology and Application; Xi'an Jiaotong University; Capital Medical University; Shanghai Jiao Tong University; VinUniversity)
> 📚 **학회/발표 기관**: ICML 2026
> 📅 **발표 날짜**: 2025.07
> 🔗 **arXiv**: https://arxiv.org/abs/2507.21892
> 💻 **코드**: https://github.com/LHRLAB/Graph-R1

---

## Problem

RAG(Retrieval-Augmented Generation)는 외부 지식을 끌어와 LLM의 환각을 완화하지만, 대부분 chunk(텍스트 블록) 기반 검색에 의존한다.
chunk 기반 검색은 엔티티 간의 복잡한 지식 구조나 구조적 의미(structural semantics)를 포착하지 못해, 다중 홉(multi-hop) 추론처럼 여러 사실을 연결해야 하는 질의에서 한계를 보인다.
이를 보완하려는 GraphRAG는 지식을 엔티티-관계 그래프로 표현하지만, 다음 세 가지 병목이 남는다.
첫째, 지식 그래프 구축 과정에서 LLM으로 자연어를 그래프 구조로 변환하는 비용이 크고, 원본 대비 의미 손실(semantic loss)이 발생한다.
둘째, 그래프 검색이 단 한 번의 고정된(one-time) 상호작용으로 충분한 지식을 모으려 해, 복잡한 질의에서 성능이 제한된다(검색과 추론이 분리되어 있음).
셋째, 검색된 그래프 지식을 바탕으로 한 답변 생성이 강한 long-context 추론 능력에 의존해, 출력 품질이 LLM의 파라미터 크기와 프롬프트 설계에 크게 좌우된다.

---

## Motivation

핵심 직관은 그래프(특히 하이퍼그래프)를 "지식 환경"으로 두고, 검색을 한 번의 질의가 아니라 에이전트-환경 간 다중 턴 상호작용으로 모델링하면 검색과 추론을 분리하지 않고 통합할 수 있다는 것이다.
저자들은 DeepSeek-R1에서 영감을 받아, 이 다중 턴 그래프 추론 정책을 사람이 설계한 프롬프트가 아니라 end-to-end 강화학습(RL)으로 직접 학습시키고자 한다.
지식을 binary(이항) 관계가 아닌 n-ary(다항) 관계를 담는 지식 하이퍼그래프로 표현하면 더 풍부한 의미 그라운딩이 가능해, RL이 도달할 수 있는 성능 천장이 높아진다(Figure 2).
즉 "강한 지식 표현(하이퍼그래프) + 다중 턴 검색 + outcome 기반 RL"을 하나의 최적화 목표로 묶으면, 작은 LLM도 구조적 지식과 언어 생성 사이의 간극을 메우며 일반화 가능한 그래프 추론 전략을 학습할 수 있다는 것이 동기다.
또한 RL로 학습된 에이전트는 추론 시 외부 LLM(GPT-4o-mini 등)에 의존하지 않으므로 생성 비용과 long-context 의존성을 줄일 수 있다.

---

## Method

Graph-R1은 (1) 에이전트 초기화(지식 하이퍼그래프 구축), (2) 다중 턴 그래프 상호작용, (3) outcome 기반 end-to-end RL 최적화의 세 부분으로 구성된다.

**(1) 경량 지식 하이퍼그래프 구축 (Graph Environment).**
도메인 지식 K = {d_1, ..., d_N}의 각 chunk d에 대해 LLM 기반 추출기 π_ext가 n-ary 관계 사실(n-ary relational facts)을 식별한다.
각 사실은 의미 세그먼트(하이퍼엣지) h_i와 거기에 참여하는 엔티티 집합 V_hi = {v_1, ..., v_n}로 이루어진다.
공유 인코더 ϕ(·)가 엔티티와 하이퍼엣지 양쪽의 의미 임베딩을 생성하여, 결과 하이퍼그래프 G_H = (V, E_H, ϕ)는 n-ary 관계를 풍부한 의미와 함께 인코딩한다.
이 방식은 기존 GraphRAG보다 구축 비용이 낮으면서도 의미가 풍부한 구조를 만든다.

**(2) 멀티턴 think-retrieve-rethink-generate 루프 (Multi-turn Graph Interaction).**
에이전트의 각 행동 a_t는 네 가지 서브 행동으로 구성된다: Thinking(추론 지속/종료 결정), Query Generation(검색 질의 작성), Graph Retrieval(하이퍼그래프에서 지식 추출), Answering(최종 답변 생성).
정책은 계층적으로 분해되어, 매 스텝 에이전트는 먼저 Thinking으로 현재 상태와 지식 공백을 요약한 뒤, 구성 지시자 α_t로 "(query, retrieve)를 더 할지" 또는 "(answer)로 종료할지"를 선택한다.
프롬프트 템플릿(Table 1)은 추론을 `<think>...</think>`, 질의를 `<query>...</query>`, 검색 결과를 `<knowledge>...</knowledge>`, 최종 답을 `<answer>...</answer>` 블록으로 구조화하도록 강제한다.
검색은 dual-path(이중 경로)로 수행된다.
(i) Entity-based Hyperedge Retrieval: 질의에서 추출한 엔티티와 유사한 상위 k_V개 엔티티를 찾고, 이들과 연결된 하이퍼엣지를 수집한다.
(ii) Direct Hyperedge Retrieval: 질의-하이퍼엣지 유사도로 상위 k_H개 하이퍼엣지를 직접 검색해 관련 사실을 모은다.
(iii) Fusion: 두 경로의 결과를 reciprocal rank aggregation(Score(f) = 1/r_V + 1/r_H)으로 융합해 상위 k개 n-ary 사실을 에이전트에 반환한다.
상태 s_t = (s_1, a_1, ..., a_{t-1})로 누적되며, 종료 행동 a_T가 나오면 최종 상태 s_T에서 답 y_q를 생성한다.

**(3) Outcome 기반 end-to-end RL (GRPO).**
최적화는 Group Relative Policy Optimization(GRPO) 목표 J_GRPO(θ)를 사용한다.
하나의 질의 q에 대해 N개의 다중 턴 궤적(trajectory) {τ_i}를 샘플링하고, 각 궤적의 보상 R(τ_i)를 그룹 평균으로 정규화해 advantage Â(τ_i) = (R(τ_i) − mean)/F_norm로 계산한다(중요도 비율 ρ_θ에 clip, KL 정규화 β로 안정화).
보상 함수 R(τ)는 두 부분으로 설계된다.
Format Reward: 매 스텝이 올바른 (think, α, output) 블록 형식을 따르면 0.5씩, 최대 1.0까지 부여한다.
Answer Reward: 생성된 답을 정답과 비교한 token-level F1로 측정한다.
최종 보상은 R(τ) = −1.0 + R_format(τ) + I{R_format(τ)=1.0}·R_answer로, 형식이 완전히 유효할 때만 답변 정확도가 보상되어 사고력 있는 검색과 정확한 답변을 동시에 유도한다.

---

## Key Contribution

1. 지식 하이퍼그래프 구축 + 다중 턴 에이전트 검색 + end-to-end RL을 하나로 통합한 **최초의 agentic GraphRAG 프레임워크** Graph-R1을 제안했다.
2. n-ary 관계를 담는 경량 지식 하이퍼그래프를 에이전트의 표준 행동 환경으로 설계하여, binary 그래프 대비 더 풍부한 의미 표현과 더 높은 성능 천장을 확보했다.
3. 검색을 "think-retrieve-rethink-generate"의 다중 턴 에이전트-환경 상호작용으로 정식화하고, dual-path 하이퍼그래프 검색 + reciprocal rank fusion을 도입했다.
4. 생성 품질(F1)과 형식 준수를 결합한 outcome 기반 보상과 GRPO를 사용해, 형식이 유효할 때만 정답 보상을 주는 end-to-end 보상 메커니즘을 설계했다.
5. 6개 표준 RAG 벤치마크에서 정확도, 검색 효율, 생성 품질 모두에서 기존 GraphRAG 및 RL 강화 RAG를 능가함을 입증하고, 소프트웨어와 데이터를 공개했다.

---

## Experiment & Results

6개 표준 RAG 데이터셋(2WikiMultiHopQA, HotpotQA, Musique, Natural Questions(NQ), PopQA, TriviaQA)에서 평가했다.
베이스라인은 NaiveGeneration, StandardRAG, SFT, R1, Search-R1, R1-Searcher(Qwen2.5의 1.5B/3B/7B 세 규모)와, GPT-4o-mini 기반의 GraphRAG, LightRAG, PathRAG, HippoRAG2, HyperGraphRAG를 포함한다.
평가 지표는 EM, F1, Retrieval Similarity(R-S), Generation Evaluation(G-E)이다.
검색 임베딩은 bge-large-en-v1.5, 지식 구축은 GPT-4o-mini를 사용했고, 모든 실험은 A100 80GB 4장에서 수행됐다.

**주요 결과(RQ1).**
Qwen2.5-7B 기준 Graph-R1의 평균 F1은 57.82로, StandardRAG(32.05), HyperGraphRAG(29.40), Search-R1(46.19)을 크게 앞섰다.
모델 크기가 1.5B→3B→7B로 커질수록 평균 F1이 40.09→51.26→57.82로 꾸준히 상승했다.
개별 데이터셋에서도 7B Graph-R1은 2WikiMultiHopQA F1 65.04, HotpotQA 62.69, Musique 46.17, TriviaQA 71.93을 기록했다(Musique에서 Search-R1 22.35 대비 두 배 이상).
프롬프트 기반 GraphRAG가 StandardRAG보다 못한 경우가 많아, "그래프 구조만으로는 부족하고 RL과 결합해야 잠재력이 발현된다"는 점을 보였다.

**Ablation(RQ2).**
지식 구축(K.C.), 다중 턴 상호작용(M.I.), 강화학습(R.L.)을 각각 제거하면 모두 성능이 하락했고, 특히 R.L. 제거 시 7B에서 F1이 63.87→17.79로 급락해 RL이 핵심임을 보였다.
RL 알고리즘 비교에서 GRPO가 REINFORCE++ 및 PPO보다 높은 F1을 달성했다.

**효율/비용(RQ3-5).**
지식 구축은 1K 토큰당 5.69초·$2.81로 GraphRAG(8.04s·$3.35), HyperGraphRAG(6.76s·$4.14)보다 저렴하며 약 12만 노드·9.8만 엣지를 생성했다.
추론 시 외부 LLM에 의존하지 않아 질의당 7.0초·생성 비용 $0(HyperGraphRAG 9.6s·$8.76 대비)로, 응답 길이는 약 1200-1500 토큰·상호작용은 평균 2.3-2.5턴으로 더 짧은 응답에 더 많은 검색 턴을 보였다.
생성 품질 7개 차원 평가에서 Correctness 86.9, Relevance 95.2, Logical Coherence 88.5를 기록하며 Overall 82.4로 Search-R1(70.3)을 크게 앞섰다.

---

## Limitation

저자들이 직접 관찰한 한계로, Qwen3(4B)처럼 이미 RL로 잘 학습된 모델에 Graph-R1을 적용하면 모델이 자체 내부 추론에 과도하게 의존(over-rely)하여, 출발점이 더 강함에도 전체 성능 천장이 오히려 약간 낮아지는 현상이 나타났다.
이는 외부 그래프 검색과 모델 내부 지식 사이의 균형이 깨질 수 있음을 시사하며, 강한 베이스 모델에 대한 적용 전략이 추가로 필요함을 의미한다.
지식 하이퍼그래프 구축이 여전히 GPT-4o-mini 같은 LLM 추출기에 의존하므로, 추출기의 품질·비용·도메인 적합성이 전체 성능의 상한을 좌우한다(독자 관점).
또한 답변 보상이 token-level F1에 기반하므로, 표면적 토큰 겹침은 낮지만 의미상 옳은 답이나 장문 서술형 답변에서는 보상 신호가 왜곡될 수 있고, 형식 위반 시 정답 보상이 완전히 차단되는 구조라 학습 초기 탐색이 불안정할 수 있다.
실험이 6개 일반 도메인 QA 벤치마크와 Qwen 계열에 한정되어, 전문 도메인(의료·법률 등)이나 다른 아키텍처로의 일반화는 검증되지 않았다(실제 영향: 도메인 이식 시 재구축·재학습 비용 발생).
마지막으로 다중 턴 RL 학습 자체가 A100 4장을 요구해, 실제 적용 시 구축 비용보다 학습 비용이 진입 장벽이 될 수 있다.

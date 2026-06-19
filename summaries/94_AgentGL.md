# 94. AgentGL: Towards Agentic Graph Learning with LLMs via Reinforcement Learning

> 📄 **저자**: Yuanfu Sun, Kang Li, Dongzhe Fan, Jiajin Liu, Qiaoyu Tan (New York University Shanghai / New York University / Tsinghua University)
> 📚 **학회/발표 기관**: ACL 2026 (Main Conference)
> 📅 **발표 날짜**: 2026.04
> 🔗 **arXiv**: https://arxiv.org/abs/2604.05846
> 💻 **코드**: https://github.com/sunyuanfu/AgentGL

---

## Problem

LLM은 정적·파라미터적 지식만으로는 전문적이거나 빠르게 변하는 도메인을 풀기 어려워 RAG와 agentic search로 외부 정보를 반복 검색해 왔다.
그러나 기존 agentic 프레임워크는 외부 정보를 전부 "비구조적 텍스트"로만 취급하여, 실제 데이터에 내재한 위상적(topological) 의존성을 활용하지 못한다.
인용 네트워크, 소셜 플랫폼, 커머스 생태계 같은 도메인의 정보는 본질적으로 Text-Attributed Graph(TAG) 형태이며, 의미는 텍스트 내용과 그래프 구조의 상호작용에서 생긴다.
따라서 어휘적 유사도에만 의존하는 agentic 시스템은 이러한 구조적 의존성을 전혀 포착하지 못하는 병목을 가진다.
기존 graph learning도 부분적 해결에 그친다: 전통 GNN(GCN, GAT)은 구조 신호는 잡지만 풍부한 텍스트 의미를 다루지 못한다.
GraphLLM(GraphGPT, GraphICL 등)은 추론 시점에 한 번 추출한 정적 그래프 컨텍스트에 의존해 적응적 탐색이 불가능하다.
GraphRAG는 코퍼스로부터 텍스트가 보강된 지식 그래프(KG)를 재구성하지만, 구축 비용이 크고 실제 TAG의 네이티브 위상 상관관계를 보존하지 못한다.
즉 GraphLLM도 GraphRAG도 실제 그래프 구조 위에서 동적으로 증거를 획득하는 메커니즘을 제공하지 못한다.

---

## Motivation

저자들은 agentic learning 패러다임을 그래프 구조 환경으로 확장하여, LLM 에이전트가 그래프를 자율적으로 항해(navigate)하며 구조적 증거를 누적하고 추론에 따라 탐색 궤적을 반복 수정하는 Agentic Graph Learning(AGL)을 제안한다.
핵심 직관은 그래프 위의 증거가 multi-scale이라는 점이다: 어떤 단서는 좁은 지역 이웃에 있고, 어떤 단서는 더 넓은 구조적 패턴을 통해서만 드러난다.
따라서 에이전트가 텍스트를 다루듯 그래프를 자유롭게 탐색할 수 있는 graph-native 도구셋을 부여하면, 정적 컨텍스트 주입(static stuffing)보다 task에 맞는 증거를 적응적으로 모을 수 있다.
하지만 AGL 실현에는 두 가지 근본 난점이 있다.
(C1) Topology-aware navigation: 조합적으로 거대한 공간에서 중복·무정보 영역을 피하며 "다음에 어디로 갈지"를 결정해야 한다.
(C2) Long-horizon policy optimization: 효과적 그래프 추론은 다단계 탐색을 요구하지만 ground-truth 탐색 궤적이 거의 없어, step별 감독 없이 탐색·활용·추론 깊이의 균형을 학습해야 한다.
이를 위해 graph-native 행동 공간의 원칙적 정식화와, 장기 의사결정을 안정적으로 학습하는 RL 메커니즘이 동시에 필요하다는 것이 핵심 동기다.

---

## Method

AgentGL은 그래프 학습을 강화학습으로 최적화되는 agentic 의사결정 과정으로 정식화한다.
TAG G=(V,A,T) 위에서, 쿼리 Q와 타깃 인스턴스 x(노드 v 또는 노드쌍 (u,v))가 주어지면, 정책 π_θ가 행동 공간 S ∪ {ANSWER}에서 행동을 반복 샘플링하여 증거 E를 누적하고 최종 예측 ŷ를 내는 순차 의사결정으로 본다.
목적함수는 결과 기반 보상 R(ŷ,y*)에서 토큰 단위 KL 페널티 β·D_KL(π_θ‖π_ref)를 뺀 기대값을 최대화하는 형태다.

**(1) Graph-Native Search(GNS) 도구셋.**
에이전트에 4개의 graph-native 탐색 도구 S={τ_1HOP, τ_2HOP, τ_SS, τ_DENSE}를 부여하여 multi-scale 구조 탐색을 가능하게 한다.
τ_1HOP(1-hop 이웃 탐색)은 타깃쌍 (u,v)의 공통 이웃 C=N_1(u)∩N_1(v)을 우선하고 배타적 이웃을 균형 할당(k_u+k_v=max(0,K-|C|))하여 후보를 모은다.
후보 노드 n의 랭킹 점수는 융합 임베딩에 대한 코사인 유사도 s(n)=cos(h_n, λ_r·h_Q+(1-λ_r)·h_x)로 계산하며, h_x는 타깃쌍 임베딩의 평균이고 λ_r은 쿼리 관련성과 구조의 균형을 조절한다.
τ_2HOP는 동일 논리로 범위를 N_2(·)로 확장한 2-hop 탐색이다.
τ_SS(Structure Salience Search)는 사전계산된 PPR(Personalized PageRank) 점수 s'(v)로 그래프 전체에서 전역적으로 두드러진 TopK 후보를 뽑아 구조적 prior 역할을 한다.
τ_DENSE(Graph Dense Search)는 τ_SS와 동일하되 구조 점수 대신 노드/쌍 임베딩의 코사인 의미 유사도 ϕ(·)로 검색하여, RAG의 Dense Retrieval을 그래프로 옮겨 위상적으로 단절된 노드를 의미적으로 잇는다.
이 도구셋은 Local vs. Global, Structure vs. Semantics 두 축을 모두 포괄하도록 설계되었다.

**(2) 반복적 reason–act–observe 루프(Template & Trajectory).**
각 프롬프트는 (a) 데이터셋별 task 지시와 폐쇄 라벨 공간·타깃 텍스트, (b) 각 도구 풀 소개를 담은 toolbox S, (c) 출력 형식 지시를 포함한다.
모델은 <think>…</think> 블록 안에서 라운드당 최대 1회만 검색 행동을 할 수 있고, <|begin_of_query|>tool_name:query<|end_of_query|> 태그로 쿼리를 발행하면 환경이 해당 GNS 도구를 실행해 <|begin_of_documents|>…<|end_of_documents|>로 증거를 반환한다.
컨텍스트는 h_t = h_{t-1} ⊕ ⟨a_t, ⟦a_t⟧_G⟩로 재귀적으로 갱신되며, 행동 a_t=⟨s_t,q_t⟩는 도구 선택자 s_t와 텍스트 쿼리 q_t로 구성된다.
롤아웃은 에이전트가 <answer>…</answer>로 최종 답을 내거나 최대 예산 B가 소진될 때 종료된다.

**(3) RL 학습 — 보상 설계와 알고리즘.**
SFT식 감독 구축 비용을 피하기 위해 critic-free 정책 최적화인 GRPO와 REINFORCE++(R++) 두 알고리즘으로 직접 최적화한다.
Stage 1(GNS Policy Bootstrapping)의 합성 보상은 R(τ)=r_FMT+r_ACC+r_COV이다.
r_FMT는 도구 사용 템플릿 준수(정확히 하나의 think/answer 블록, 태그 정합성 등)를 강제해 궤적을 기계 파싱 가능하게 만들고, r_ACC=λ_a·I[ŷ=y]는 reward hacking을 막아 최종 task에 정렬시키며, r_COV는 네 도구를 모두 조기에 탐색하도록 유도해 단일 행동으로의 mode collapse를 방지한다(도구당 최대 1회, 상한 |S|·η).
Stage 2(Mitigating Search Overuse)는 "Think more, Search less" 원칙으로 탐색 과용을 줄인다: 정확도를 하드 제약으로 두고(argmax J_BASE 안에서) 총 탐색 비용 T(τ)를 최소화한다.
이를 위해 Search-Constrained Thinking을 도입하는데, 도구 실행 직후 "방금 검색한 문서를 먼저 검토하고 추가 검색이 필요한지 판단하라"는 Retrospective Termination Trigger(RTT)를 주입해 검색을 습관적 연쇄가 아닌 의도적 이진 결정으로 바꾼다.
또한 Cognitive Density Regularization(CDR)으로 검색 후 추론 블록 길이가 임계 δ 미만인 "결핍" 세그먼트 수 N_short를 세어 r_depth(z)=α·I[N_short=0]-λ_d·N_short로 얕은 추론을 페널티하여, 검색 감소가 단순 스킵이 아니라 깊은 추론 흡수에서 오도록 강제한다.
Stage 2 보상은 r_COV를 버리고 R(τ)=r_FMT+r_ACC+r_depth로 전환한다.

**(4) Graph-Conditioned Curriculum Learning(GCCL).**
그래프는 위상·의미 prior로 학습 난이도를 직접 정량화할 수 있다는 이점을 활용해, 분석적 난이도 점수 S(·)로 easy→hard 무료(cost-free) 커리큘럼을 구성한다.
노드 분류 난이도 S_NC(v)는 이웃 라벨 일관성 p̂_v를 Wilson Lower Bound로 보정하고 차수 d_v 항(η·log(1+d_v))을 더해, 구조적으로 두드러진 허브를 Easy, 모호·이질적(heterophilous) 외곽 노드를 Hard로 둔다.
링크 예측 난이도 S_LP(e)는 라벨 y_e와 노드 특징 코사인 유사도 sim(x_u,x_v)의 일관성으로 정의해, high-sim 양성/low-sim 음성을 Easy, high-sim 음성 같은 충돌 사례를 Hard로 미룬다.
Algorithm 1에 따라 두 Stage 모두 easy/medium/hard 3계층으로 사전 분할(NC 학습셋은 Stage1=800/500/500, Stage2=200/500/500 할당)되어 난이도 오름차순으로 학습된다.

---

## Key Contribution

1. Agentic Graph Learning(AGL)이라는 새 패러다임을 제시하여, 그래프 학습을 topology-aware 탐색과 LLM 추론이 교차(interleaved)되는 과정으로 재정의하고 그래프 구조·텍스트 의미·agentic 의사결정을 단일 프레임워크로 통합했다.
2. AGL을 위한 최초의 RL 기반 프레임워크 AgentGL을 제안하여 구조적 지각(perception)·전략적 추론·정책 학습을 결합했다.
3. multi-scale 탐색을 위한 graph-native 도구셋(1-hop/2-hop/Structure Salience/Dense)과, 과검색을 억제하는 search-constrained thinking(RTT+CDR)을 설계했다.
4. step별 감독 없이 장기 정책 학습을 안정화하는 graph-conditioned curriculum RL(GCCL)을 도입했다.
5. 7개 TAG 데이터셋·13개 baseline·2개 LLM 백본에서 광범위 검증하여, 노드 분류 최대 +17.5%, 링크 예측 최대 +28.4%의 절대 성능 향상을 입증했다.

---

## Experiment & Results

3개 도메인의 7개 TAG 데이터셋(인용망: OGB-Arxiv, PubMed, Arxiv-2023 / 아마존: OGB-Products, Amazon-Photo, Amazon-Computers / 소셜: Reddit)에서 노드 분류(NC)·링크 예측(LP)을 평가했다.
baseline은 5개 범주 13종으로, GNN(GCN, RevGAT, GraphSAGE), GraphLLM(LLaGA, GraphGPT, GraphPrompter, GraphICL), GraphRAG(LinearRAG, HippoRAG2, GraphCoT), 표준 agentic search(Search-R1, Search-O1), LLM SFT(Qwen2.5-3B/7B-Instruct)를 포함한다.
모든 모델은 OGB-Arxiv와 OGB-Products로만 학습 후 전체 데이터셋 test split에서 in-domain 및 zero-shot transfer로 평가했고, 지표는 정확도(ACC %)다.
**Obs 1 (전반 우위):** Qwen7B 기준 AgentGL은 NC에서 in-domain 평균 +12.7%, zero-shot +24.4%, LP에서 in-domain +26.3%, zero-shot +22.4%로 baseline을 능가했다.
구체적으로 Qwen7B에서 AgentGL-R++는 OGB-Arxiv NC 70.3%(Search-R1 63.2% 대비 우위), OGB-Products NC 76.8%, OGB-Arxiv LP 95.6%, OGB-Products LP 97.4%를 기록했다.
**Obs 2 (정적 stuffing 대비):** Qwen7B LP에서 AgentGL은 GraphRAG 대비 in-domain +47.4%, GraphLLM 대비 +23.2%로 앞섰고 zero-shot에서도 각각 +35.4%, +26.9%로 격차를 유지해, 정적 컨텍스트 주입이 분포 변화에 취약함을 보였다.
**Obs 3 (알고리즘 상보성):** GRPO는 NC에서 평균 +0.9% 더 높고, R++는 LP에서 평균 +3.3% 더 강해 task별로 선택 가능한 트레이드오프를 보였다.
**Obs 4 (스케일링):** 백본을 3B→7B로 키우면 NC는 in-domain +9.0%/zero-shot +11.8%, LP는 +5.6%/+8.7% 향상되어 zero-shot에서 특히 두드러졌다.
**Stage 절제(Table 2):** GNSPB만 쓰면 예산을 거의 다 소진하고, MSO만 쓰면 zero-search로 붕괴하며, 두 Stage 결합 시 OGB-Arxiv NC 68.9%에 도달하고 GNSPB 단독 대비 도구 호출을 약 17.5% 줄이면서 NC 정확도를 평균 +2.4% 높였다.
**컴포넌트 절제(Table 3):** r_COV 제거 시 -4.1%, CDR 제거 -2.9%, RTT 제거 -3.4%, GCCL 제거 -0.6%(OGB-Arxiv/Amazon-Photo 평균)로 모든 요소가 기여했고, RTT+CDR 결합은 수렴 시 검색 비용 약 22% 절감과 정확도 +3% 개선을 동시 달성했다.
**하이퍼파라미터:** λ_r=0.5(구조·의미 균형)에서 최적(OGB-Arxiv 68.9%, PubMed 82.7%, Amazon-Computers 68.6%)이었고, 이웃 크기 K=5에서 최고(OGB-Arxiv 68.9%, Amazon-Photo 59.9%)이며 K=7은 노이즈로 소폭 하락했다.

---

## Limitation

저자 명시 한계로, AgentGL은 현재 text-attributed graph에만 동작하고 multimodal-attributed graph는 지원하지 못해 노드가 풍부한 모달 정보를 담는 환경에 적용이 제한된다.
또한 MSO 단계의 안정적 성능이 두 Stage 간 데이터 할당의 섬세한 트레이드오프에 결정적으로 의존하며, MSO가 추론 시점 도구 사용 분포를 바꾸는지 여부도 추가 검증이 필요하다고 인정한다.
MSO 단계는 단순·직접적으로 설계되어 향후 더 정교한 설계 여지가 남아 있고, 더 조밀한(denser) 그래프로의 확장도 미해결 과제다.
독자 관점에서, 실험이 Qwen2.5 3B/7B 두 백본에 국한되어 더 큰 모델이나 다른 계열에서의 일반화는 미지수이며, 검색 예산을 B=4로 고정한 설정이라 더 깊은 다단계 추론이 필요한 그래프에서의 거동은 불확실하다.
GCCL의 난이도 점수가 homophily·차수 등 휴리스틱 prior에 기반하므로, 이런 prior가 잘 맞지 않는 강한 이질성 그래프에서는 커리큘럼 효과가 약해질 수 있다.
끝으로 GraphRAG baseline을 그래프 추론용으로 적응시켜 비교한 만큼, 본래 QA 목적과의 목표 불일치로 인한 비교 공정성 논쟁의 여지가 남는다.

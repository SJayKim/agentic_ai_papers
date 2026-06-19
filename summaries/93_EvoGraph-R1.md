# 93. EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval

> 📄 **저자**: Jiashi Lin, Changhong Jiang, Xiangru Lin, Ruifei Zhang, Xinyi Zhu, Jiyao Liu, Cheng Tang, Ye Du, Shujian Gao, Junzhi Ning, Lihao Liu, Ziyan Huang, Tianbin Li, Jin Ye, Junjun He (Northwestern Polytechnical University, Shanghai AI Laboratory, The University of Hong Kong, Monash University, CUHK-Shenzhen)
> 📚 **학회/발표 기관**: CVPR 2026
> 📅 **발표 날짜**: 2026.06
> 🔗 **arXiv**: CVPR 2026 (no arXiv)
> 💻 **코드**: 명시되지 않음 (본문에 GitHub/프로젝트 URL 없음, 구현 세부는 supplementary 안내)

---

## Problem

Retrieval-Augmented Generation(RAG)은 멀티모달 LLM(MLLM)을 외부 지식에 접지(grounding)하는 핵심 패러다임이지만, 기존 멀티모달 RAG는 검색된 근거를 단절된 텍스트 스니펫이나 거친 페이지 단위 스크린샷으로 환원해 세밀한 구조 모델링과 cross-modal 정렬을 방해한다.
최근 GraphRAG 계열은 entity-relation 그래프로 구조적 추론을 돕지만, 지식 그래프를 오프라인에서 한 번에 구축해 단일 패스로 질의하는 **정적(static) 데이터 구조**로 취급한다는 근본 한계가 있다.
이 one-shot 구축은 길거나 멀티모달인 입력에서 그래프 품질을 보장하기 어렵고, 불완전하거나 노이즈 많은 그래프가 검색·추론 전반으로 오류를 전파한다.
저자들은 이로 인한 세 가지 병목을 명시한다: (1) **Text-centric fragmentation** — LLM 기반 추출이 풍부한 멀티모달 근거를 고립된 텍스트 튜플로 붕괴시켜 관계 누락·구조 파편화·장거리/cross-modal 의존성 손실을 유발한다.
(2) **Static structure** — 추론 중 그래프가 고정되어 새 근거 통합, 오류 정정, 미지 토픽 커버리지가 불가능하다.
(3) **Rigid retrieval** — 검색이 반복적 정제 없는 단일 패스 연산이라 초기 근거가 불충분해도 전략 수정·대안 탐색·외부 검색 호출을 할 수 없다.

---

## Motivation

핵심 직관은 지식에 대한 인간의 추론이 본질적으로 상호작용적·반복적이라는 점이다 — 초기 근거를 모으고, 빈틈을 식별하고, 추가 정보를 찾고, 모순을 조정하며 이해를 점진적으로 정제한다.
이는 강화학습의 agent-environment 상호작용 패러다임(상태 인식 → 상태를 바꾸는 행동 → 피드백 수신)과 정확히 대응된다.
따라서 저자들은 멀티모달 GraphRAG를 **Markov Decision Process(MDP)** 로 재개념화하여, 지식 그래프를 추론 과정과 함께 진화하는 **동적 환경(dynamic environment)** 으로 본다.
이때 환경 상태는 멀티모달 지식 하이퍼그래프이고, 행동은 그래프를 질의(GRAPHRETRIEVE)·확장(WEBSEARCH)·정제(GRAPHEDIT)·종료(ANSWER)하며, 보상은 추론 품질(구조적 정확성·답변 정확도)과 효율(연산 비용)을 평가하는 trajectory-level 신호다.
이 정식화는 검색·추론·지식 진화를 단일 RL 루프로 통합하는 **self-evolving 패러다임**을 가능케 하며, 에이전트는 고정 그래프에서 단순히 검색하는 것이 아니라 검증된 근거 추가·불일치 정정·노이즈 가지치기·구조 재조직으로 그래프를 능동적으로 빚는다.
시각 컴포넌트를 제거해도 에이전트 주도 진화 메커니즘을 유지하면 텍스트 전용 환경에도 자연스럽게 적용되어, 모달리티 독립적 가치를 갖는다는 것이 동기다.

---

## Method

EvoGraph-R1은 세 컴포넌트로 구성된다: (1) 멀티모달 하이퍼그래프 구축, (2) 에이전트 기반 그래프 진화, (3) 강화학습 정책 최적화.

**(1) 멀티모달 하이퍼그래프 구축 (Multimodal Hypergraph Construction).**
멀티모달 코퍼스로부터 통합 cross-modal 하이퍼그래프 G_H=(V, E)를 세 단계로 만든다.
*Textual Subgraph Extraction*: 입력 텍스트를 지식 조각인 하이퍼엣지로 분할하고, 각 하이퍼엣지 e_i는 자연어 설명·엔티티 집합·관계 타입·신뢰도 σ_i∈(0,10]를 담는다.
MLLM 기반 추출기 π_ext에 **n-ary relation extraction 프롬프트**를 적용해, 한 텍스트 세그먼트가 여러 개의 겹칠 수 있는 n항 관계 사실을 기여하도록 하여 이진 관계를 넘어선 고차(high-order) 관계 추론을 지원한다.
*Visual Subgraph Construction*: 각 이미지에 대해 π_ext로 상세 장면 설명과 주요 객체명을 생성하고, 이 장면 설명을 고차 하이퍼엣지로 인코딩해 이미지에 접지된 모든 엔티티·관계의 "앵커(anchor)" 노드 u_x로 삼는다.
모든 시각 하이퍼엣지가 앵커 노드를 포함하도록 강제해 시각 사실이 출처 귀속 없이 떠다니는 것을 방지한다.
*Cross-Modal Graph Fusion*: 엔티티 라벨을 정규화하고 엔티티 해소 함수 ϕ(문자열 유사도+임베딩 근접도)로 시각·텍스트 멘션을 매칭하여 정규(canonical) 노드로 병합한다.
이후 멀티모달 인코더 f(·)(예: GME)로 모든 그래프 요소(엔티티·하이퍼엣지)를 공유 의미 공간에 임베딩해 오프라인 인덱싱하며, 이 통합 하이퍼그래프가 에이전트 진화의 초기 환경 상태가 된다.

**(2) 에이전트 기반 그래프 진화 (Agent-Based Graph Evolution, MDP 정식화).**
이산 시간 t=0,...,T의 MDP로 모델링한다.
환경 상태 s_t=(G_t, H_t, q)는 현재 하이퍼그래프 G_t(검색 근거와 연결성·cross-modal 정렬·관련도 점수 포함), 행동 이력 H_t(튜플 (a_k, r_k, G_{k+1}) 시퀀스), 질의 q로 구성된다.
행동 공간은 네 가지다.
*GRAPHRETRIEVE*는 현재 하이퍼그래프를 질의하며, cross-modal 엔티티 단위 lookup과 하이퍼엣지 단위 벡터 검색을 지원해 구조적으로 연결된 고차 사실을 활용한다.
*WEBSEARCH*는 그래프 내 근거가 불충분할 때 호출되어, 질의 q_web을 만들어 웹 검색 엔진에서 외부 정보를 가져오고 현재 상태에 정렬·추가한다.
*GRAPHEDIT*는 그래프 구조를 직접 수정하는 세 하위 연산으로 정제한다 — INSERT(검색 내용에서 도출한 새 엔티티/하이퍼엣지 추가로 검증된 근거 확장), UPDATE(기존 하이퍼엣지를 수정해 오류 정정·충돌 해소·근거 강화), DELETE(저품질/모순 요소의 신뢰도 점수를 낮추는 **soft removal**로 노이즈 가지치기).
*ANSWER*는 환경이 충분히 진화하고 근거가 축적되었다고 판단되면 현재 그래프 상태 기반으로 최종 답을 내며 추론을 종료한다.
상태 전이 G_{t+1}=π_evolve(a_t, G_t)에서 행동 타입별로 변화가 다르다 — GRAPHRETRIEVE는 접근 표시만 하고 구조를 바꾸지 않으며, WEBSEARCH는 새 사실·정렬로 증강하고, GRAPHEDIT만이 구조를 실제로 정제한다.

**(3) 강화학습 최적화 (RL Optimization).**
정책을 **Group Relative Policy Optimization(GRPO)** 로 학습하며, trajectory-level 보상 R(τ)는 세 요소로 구성된다.
*Structural Reward*: 각 단계가 의도된 상호작용 프로토콜(think/action/output 블록 형식)을 따르는지를 평가하며, 단계별 스케일 factor η=0.5로 well-formed 단계를 보상하되 상한 1.0으로 capped한다.
*Answer Reward*: 예측 답과 정답의 토큰 단위 overlap을 측정하는 F1 스타일 점수로, 정확한 문자열 일치 없이 의미 정렬을 보상한다.
*Overall Outcome Reward*: R(τ) = −λ·Σc(a_t) + R_struct(τ) + I[R_struct(τ)=1.0]·R_ans 형태로 정확성·구조·효율을 통합하며, c(a_t)는 행동 비용, λ는 효율 계수다.
중요한 점은 추론 과정이 구조적으로 일관(R_struct=1.0)할 때만 정답 보상이 주어져, 고품질·저비용 그래프 진화를 촉진한다는 것이다.
학습 시 GRAPHEDIT 행동만 그래프 상태 G_H를 수정하고 나머지 행동은 구조를 바꾸지 않고 정보만 수집하며, GRPO는 그룹 평균 대비 각 trajectory 보상으로 advantage를 계산해 다중 rollout에서 안정적으로 학습한다.

---

## Key Contribution

1. **Self-evolving retrieval 패러다임**: 멀티모달 지식 그래프를 MDP 환경으로 모델링하여 검색·추론·지식 진화를 agent-environment 상호작용으로 통합한 최초의 프레임워크를 제안한다.
2. **EvoGraph-R1 프레임워크**: 멀티모달 지식 하이퍼그래프 위에서 네 가지 행동(GRAPHRETRIEVE, WEBSEARCH, GRAPHEDIT, ANSWER)으로 작동하는 자율 에이전트를 설계해, 그래프 구조와 추론의 closed-loop co-evolution을 구현한다.
3. **모달리티 일반화**: 시각 컴포넌트를 제거하고 에이전트 주도 진화만 유지하면 텍스트 전용 시나리오에도 적용되어, 지식 그래프를 상호작용 환경으로 보는 가치가 모달리티와 무관함을 입증한다.
4. **SOTA 성능**: 지식 집약 멀티모달 VQA와 텍스트 QA 벤치마크에서 RAG·GraphRAG·search-augmented baseline을 정확도·효율·근거 추적성(traceability) 측면에서 큰 폭으로 능가한다.

---

## Experiment & Results

**셋업.**
멀티모달 태스크는 E-VQA, InfoSeek, OK-VQA(Wikipedia 지식원, EchoSight로 필터링), 텍스트 전용은 2WikiMultiHopQA, HotpotQA, Natural Questions(공식 Wikipedia dump)를 사용한다.
지식 구축은 GPT-4o-mini, 검색은 GME, 베이스 모델은 멀티모달에 Qwen2.5-VL-7B / 텍스트에 Qwen2.5-7B-Instruct를 쓰고, 3개 random seed로 80GB A100 4장에서 실험한다.
평가지표는 멀티모달 정확도에 LLM-as-Judge, 텍스트에 F1, 답변 품질에 G-E를 사용한다.

**텍스트 전용 성능 (RQ1).**
가장 강한 baseline Graph-R1 대비 2WikiMultiHopQA에서 +3.5%p, HotpotQA에서 +2.7%p, NQ에서 +6.9%p 향상하여 각각 **68.5 / 65.4 / 56.8 F1**을 달성한다(Graph-R1-7B는 65.0 / 62.7 / 49.9).
평균 F1은 63.57로 Graph-R1-7B(59.20), HippoRAG2(30.80), NaiveRAG(29.67)를 크게 앞선다.

**멀티모달 성능 (RQ1).**
E-VQA에서 **43.6%** 정확도로 MMSearch-R1(36.9) 대비 +6.7%p, MMKB-RAG(35.9) 대비 +7.7%p 우위를 보인다.
OK-VQA에서 **68.6%** 로 GPT-4o-mini(65.9) 대비 +2.7%p, MMSearch-R1(59.9) 대비 +8.7%p, InfoSeek에서 42.3%를 기록하며 평균 51.50으로 모든 baseline 중 최고다.
웹 검색 장착 방식과 비교 시 텍스트 벤치마크에서 MMSearch-R1 대비 +21.8%p, Search-R1 대비 +17.5%p 우위로, 근거를 단계마다 버리지 않고 지속 진화 상태로 누적하는 것의 이점을 확인한다.

**Ablation (RQ2, 2Wiki/E-VQA).**
멀티모달 하이퍼그래프 제거 시 2Wiki −5.4%p / E-VQA −4.8%p 하락한다.
GRAPHEDIT 중 **INSERT가 가장 중요**해 제거 시 2Wiki −8.4%p / E-VQA −6.8%p, UPDATE 제거 시 −5.5 / −3.9%p, DELETE 제거 시 −2.4 / −1.5%p 하락한다.
**WEBSEARCH 제거 시 2Wiki −9.6%p / E-VQA −11.2%p** 로 가장 큰 손실을 보여 정적 코퍼스의 long-tail 한계를 드러낸다.

**효율 (RQ3).**
EvoGraph-R1은 2Wiki를 평균 2.57 라운드, E-VQA를 1.65 라운드에 완료하는 반면, −INSERT는 3.48 라운드(+35.4%), −WEBSEARCH는 3.17 라운드(+23.3%)가 필요하다.
또한 약 2.4 검색 턴·약 1,300 토큰의 간결한 응답으로 수렴해, graph editing 없는 변형(약 3.1 턴·2,850 토큰)과 MMSearch-R1(약 3.5 턴·2,200 토큰)보다 효율적이다.

**생성 품질·저자원·그래프 정제 (RQ4/RQ5).**
HelloBench 7개 차원(relevance, correctness, comprehensiveness, factuality, logical coherence, knowledgeability, diversity) 모두에서 baseline을 일관되게 능가한다.
저자원 설정에서 Wikipedia를 1%로 제한해도 37.2% 정확도로 baseline(13.2~18.9%)을 크게 앞서며, MMKB-RAG 대비 격차가 full corpus +7.7%p에서 1% corpus +13.2%p로 **데이터가 줄수록 격차가 벌어진다**(5%에서 +13.8, 10%에서 +12.9).
그래프 정제 통계상 노드 +2.60%, 하이퍼엣지 +2.26%, graph density +7.81%, clustering coefficient +16.67%, edge semantic similarity +3.16%로 구조적·의미적 일관성이 모두 개선된다.

---

## Limitation

저자들이 명시적으로 별도 Limitation 섹션을 두지는 않았으나, 본문에서 드러나는 한계는 다음과 같다.
첫째, 그래프 구축과 시각 장면 설명·n-ary 추출 모두 GPT-4o-mini와 π_ext(MLLM 추출기)에 의존하므로, 초기 하이퍼그래프 품질과 visual anchor 정확도가 외부 폐쇄형 모델에 종속되고 추출 오류가 후속 진화에 전파될 수 있다.
둘째, WEBSEARCH 제거 시 성능 하락이 가장 크고 저자원에서 격차가 커진다는 결과는, 강력한 성능이 상당 부분 실시간 웹 검색 접근에 기인함을 시사한다 — 웹 접근이 불가하거나 검색 품질이 낮은 폐쇄 도메인에서는 이점이 축소될 수 있다.
셋째, DELETE가 실제 삭제가 아닌 신뢰도 점수를 낮추는 soft removal이라, 모순·노이즈 요소가 그래프에 잔존하며 장기적으로 누적될 가능성이 있다.
넷째, 답변 보상이 토큰 overlap 기반 F1 스타일이고 멀티모달 평가가 LLM-as-Judge(GPT-4o-mini)에 의존하므로, 의미적으로 옳지만 표현이 다른 답에 대한 보상 부정확성과 judge 편향 위험이 존재한다.
다섯째, 평가가 7B 베이스 모델·A100 4장·Wikipedia 지식원에 한정되어, 더 큰 모델이나 비-위키 도메인(전문/실시간 도메인)으로의 확장성과 다중 행동·GRPO rollout에서 오는 학습/추론 비용은 충분히 검증되지 않았다.

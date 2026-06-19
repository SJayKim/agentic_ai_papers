# 95. TESSERA: LLM-Guided Monte Carlo Tree Search over Knowledge Graphs

> 📄 **저자**: Rishabh Jakhar, Michel Dumontier, Remzi Celebi (Maastricht University, Institute of Data Science)
> 📚 **학회/발표 기관**: IJCAI-ECAI 2026
> 📅 **발표 날짜**: 2026.05
> 🔗 **arXiv**: https://arxiv.org/abs/2605.09542
> 💻 **코드**: https://github.com/RishabhJakhar/tessera

---

## Problem

지식 그래프(KG)에서 약물-질병 쌍의 다단계(multi-step) 기전 설명을 추출하는 것은 본질적으로 조합 폭발(combinatorial explosion) 문제다.
탐색 깊이가 깊어질수록 후보 경로가 기하급수적으로 늘어나 전수 열거(exhaustive enumeration)가 불가능해진다.
따라서 이 문제는 "배경 지식이 유망한 후보 쪽으로 탐색을 유도하는" 휴리스틱 탐색(heuristic search)으로 정식화되어야 하며, 두 가지 핵심 요구를 동시에 만족해야 한다.
첫째는 휴리스틱 가이드(후보가 깊이에 따라 증식하므로 어디를 볼지 안내)이고, 둘째는 신용 할당(credit assignment, 긴 시퀀스 전반에서 경로 품질이 드러나므로 초기 선택의 기여도를 평가)이다.
기존 KG 추론·경로 탐색 방법은 사후 귀속(post-hoc attribution, 예: Kelpie, GNNExplainer)이나 RL 기반 경로 탐색(MINERVA, PoLo, CoCo, REx)에 의존하는데, 전자는 일관성·간결성 같은 설명 요건을 결여하고 후자는 손으로 짠 구조적 프록시(degree heuristic 등)에 묶여 고정 길이(보통 3-4 hop) 롤아웃만 가능하다.
즉 "어떤 상황에서 왜 이 경로가 좋은가"라는 의미적(semantic) 판단을 직접 반영하지 못하고, 가변 깊이·장기 horizon 설명을 합성하지 못한다.

---

## Motivation

프런티어 LLM은 생의학 지식·추론 벤치마크에서 강력하므로 휴리스틱의 매력적인 원천이지만, 저자들은 LLM의 본질적 한계를 직시한다.
LLM은 "근사적 전지성(approximate omniscience)"을 지녀 도메인 지식 커버리지는 넓으나 정확성 보장이 없고 환각·작화(confabulation)에 취약하다.
특히 합성적(compositional) 성능이 과제 복잡도에 따라 체계적으로 저하되어, 단일/소수 단계 판단은 잘하지만 단계를 길게 이어 붙이면 오류가 누적되어 실패한다(Dziri et al.의 "Faith and Fate").
이 진단은 LLM을 자율적 다단계 생성기가 아니라 "국소적 판별 판단(local discriminative judgment)"의 원천으로만 제한적으로(circumscribed) 써야 한다는 결론을 낳는다.
핵심 직관은 neuro-symbolic 분업이다: KG가 가설 공간을 정의하고 하드한 구조적 제약을 강제하며, LLM은 부드러운 국소 의미 판단을 공급하고, MCTS가 backpropagation을 통한 원칙적 신용 할당으로 장기 탐색을 조율한다.
이렇게 휴리스틱 가이드(탐색 편향)와 의미 평가(보상 신호)를 결합하면, 검증되지 않은 LLM 지식의 위험을 통제하면서도 약물-질병 기전 설명을 합성할 수 있다는 것이 동기다.

---

## Method

TESSERA(Tree-search for Explanation Synthesis via Semantic Evaluation and Ranked Actions)는 KG·LLM·MCTS 3-pillar 신경기호 프레임워크다.

**(0) 문제 정식화 및 상태/행동 정의.**
방향성·타입 다중관계 KG G=(V,R,E) 위에서, 약물 d로부터 질병 z를 조건으로 설명 서브그래프 g(d,z)를 추출한다.
탐색 상태는 s=(u,H,z)로, u는 현재 노드, H는 u까지 도달한 순서 경로, z는 고정된 목표 노드다.
같은 그래프 노드라도 도달 경로가 다르면 별개 상태로 취급(path-dependent)한다.
합법 행동 A(s)는 두 단계로 결정된다: 먼저 질병 z를 one-hot personalization으로 둔 personalized PageRank 점수 ppr_z로 top-k 이웃을 필터링하고(A_k(s)), 다음으로 특정 노드 타입 집합 T가 비율 λ에 못 미치면 랭킹 꼬리에서 증강 예산 τ만큼 행동을 주입(A+τ)한다.
전이 함수는 결정적이어서 행동 (r,v) 실행 시 s'=(v, H++(u,r,v), z)가 된다.

**(1) MCTS 4단계와 LLM 개입 지점.**
탐색은 루트 s0=(d,∅,z)에서 시작해 시뮬레이션 예산 T 동안 4단계를 순환한다.
**Selection**에서는 루트부터 리프까지 PUCT로 Q(s,a)+U(s,a)를 최대화하며 내려가는데, 사전확률 P(s,a)=π_LLM(a|s)가 LLM 기반 prior policy다.
저자들은 탐색계수 c_puct=δ(d)·φ(N)를 깊이·방문수 의존으로 설계해(δ(d)=c0/(1+αd), φ(N)=1+βe^(−N/K)), 깊이가 깊어지면 탐색을 누그러뜨리고 초기 방문엔 보너스를 준다.
**Evaluation**에서 리프 s_L이 목표(u=z)면 경로를 설명 집합 H_exp에 admit하고 v=0, 막다른 길(A(s_L)=∅)도 v=0, 그 외 비종단 상태는 LLM 상태 평가기로 v(s_L)∈[−1,1]을 얻는다.
**Backpropagation**은 경로 위 모든 엣지의 N, W를 갱신하고 Q=W/N으로 신용을 역전파한다.
**Expansion**은 리프를 무조건 확장하여 모든 후속 상태를 구체화하고 prior P(s_L,a)=π_LLM(a|s_L)를 부여한다.
종료 시 H_exp의 모든 경로 엣지 합집합으로 서브그래프 g(d,z)를 구성한다.

**(2) Prior Policy — listwise 비교 랭킹.**
LLM은 행동들을 절대 점수가 아니라 상대 비교로 평가하는 데 강하므로, IR의 multi-pivot n-ary quicksort(Godfrey et al.)를 그래프 행동 점수화에 적용한다.
행동 수 |A(s)|가 한 번의 LLM 호출 한도를 넘으므로 배치 크기 W로 잘라 long-context 저하(position bias)를 피하고, 배치를 동시(concurrent) 채점한다.
quicksort는 m 패스에 걸쳐 작업 행동 집합을 T1=|A(s)|에서 Tm=W로 선형 truncate하며, 각 패스마다 분위수 간격 pivot k=⌊W/2⌋를 골라 공유 pivot 집합 P를 비-pivot 청크에 붙여 배치를 만든다.
각 배치는 부모 상태, 루브릭 R_prior, 행동의 술어·노드 속성(식별자/타입/레이블/설명)을 컨텍스트로 받아 rank π_B(a)와 score s_B(a)를 반환하며, 배치 내 z-score 표준화로 ˜s_B(a)를 얻는다.
공유 pivot을 anchor로 삼아 배치 간 rank·score를 평균해 전역 순서를 만들고 비-pivot은 이웃 pivot 사이를 보간하며, 최종 유틸리티를 temperature softmax로 확률 분포(prior)로 매핑한다.

**(3) State Evaluation — 비교적·경로 인식 보상.**
비종단 리프는 (i) 소수 경쟁 경로 집합 C(s_L)와 함께 평가되고 (ii) 현재 설명 집합 H_exp 대비 한계 기여(marginal contribution)로 채점된다.
경쟁자는 s_L과 깊이 차가 ∆ 이내인 상태 풀 F∆(s_L)에서, logP_path(prior 로그합)와 N_cum(방문수 합) 기준 사전식(lexicographic) 정렬로 top-k를 뽑는다.
모델은 정수 라벨로 된 순서형 루브릭 R_state-eval로 각 상태를 평가하되, 출력 라벨을 직접 쓰지 않고 토큰 수준 log-probability에 softmax를 취해 불확실성 인지(uncertainty-aware) 기대 점수를 계산한 뒤 [−1,1]로 정규화한다.
결정적 baseline인 PPR-eval은 LLM 평가기를 target-conditioned PageRank ppr_z의 전역 백분위 순위 보정값으로 대체한다.

---

## Key Contribution

1. MCTS와 LLM 유래 휴리스틱을 결합해 생의학 KG에서 기전 설명을 추출하는 neuro-symbolic 프레임워크 TESSERA를 제안했다.
2. 대규모 행동 집합으로 확장 가능한 listwise prior policy를 설계했다 — 배치 평가로 LLM의 상대 판단 강점을 활용하면서 long-context 저하를 회피한다.
3. 비교적 state evaluator를 도입했다 — 부분 경로를 깊이 제한 경쟁자 집합과 비교 채점하고, 토큰 수준 확률로 불확실성을 반영하며, 이미 accept된 경로에 조건화하여 한계 기여를 평가한다.
4. 두 개의 상보적 substrate에서 평가했다 — 정답 비교가 가능한 DrugMechDB와, 정답이 없어 고분기 탐색을 검증할 수 있는 Multi-scale Interactome(통제·검증된 LLM-as-judge 프로토콜 사용).
5. ablation으로 두 LLM 구성요소(prior policy, state evaluator) 각각의 판별적 기여를 실증하고, 압축적이면서 일관된 기전적 대안을 표면화함을 보였다.

---

## Experiment & Results

**데이터셋.**
DrugMechDB(DMDB)는 전문가 큐레이션 기전을 병합한 supergraph(5,128 노드, 10,064 엣지)로 평균 out-degree 2(p90=4, max=224)의 작은 행동 집합, SCC가 전체의 1%에 불과한 희소 연결성을 가진다.
Multi-scale Interactome(MSI)은 29,698 노드·921,953 엣지(단백질 17,527 / 생물학적 기능 9,798 / 약물 1,550 / 질병 821)의 대규모 그래프로, out-degree 평균 31(p90=75, max=2,299), 최대 SCC가 노드의 92%를 덮어 고분기·고경로 다중성을 보인다.
state evaluation에는 비추론(non-reasoning) SOTA 모델 GPT-4.1, DeepSeek-V3.1, Qwen3-235B를 실험했고, prior policy는 GPT-4.1로 고정(상태별 prior 캐싱으로 재사용)했으며, LLM 추론 비용 때문에 12개 MeSH 질병 범주·9개 ATC 치료군에 걸쳐 층화 샘플링한 15개 약물-질병 쌍으로 평가했다.

**DMDB 정량 결과(15쌍×3 모델=45 run).**
노드 수준 일치 NSA Micro P/R = 0.71/0.83으로 강했다.
엣지 수준 ESA@1(hop 여유 없음) Micro P/R = 0.44/0.64이고, 1-hop 허용 ESA@2에서 precision이 0.44→0.50으로 올랐으나 recall은 0.64로 평평해 detour보다 shortcut이 많음을 시사했다.
엣지를 curated 노드로 제한하면 Micro P가 h=1에서 0.86, h=2에서 0.99로 상승해 큐레이션 노드 간 spurious 엣지가 거의 없음을 확인했다.
도달성 일치 TCA Micro P/R = 0.99/0.66으로 알고리즘의 도달성 주장은 거의 모두 유효하나 gold 도달 쌍의 약 34%를 놓쳤다(주로 누락 노드 탓).
완전 약물→질병 경로 일치는 EPA-IV(in-vocabulary) Micro P = 0.84로 높았으나, EPA-OW(open-world)에서 0.27로 급락해 예측 경로가 큐레이션 외 매개 노드를 자주 포함(간결성 부족)함을 드러냈다.
구조 분해(Figure 1)에서 경로 길이 정렬은 대각선(일치 hop) 73.1%, |∆h|≤1 내 91.6%였고, shortcut 25.8% vs detour 1.1%, 매개자 Jaccard 중첩 평균 61.5%, 예측 매개자의 74.1%가 gold 노드였다.

**MSI 결과(LLM-as-judge, 5차원 1-5 척도, 3×3 설계).**
채점 신뢰도는 매우 높아 동일 모델의 3개 직렬화 간 ICC(3,3)=0.989(DeepSeek)/0.987(Qwen3)/0.981(GPT-4.1), 3개 심판 LLM 간 ICC(3,3)=0.946(95% CI 0.93-0.96)였다.
점수는 Contextual Specificity가 가장 높고(중앙값 4.23-4.51), Biological Plausibility(3.72-3.87), Mechanistic Coherence(3.70-3.84), Completeness(3.64-3.71) 순이며 Conciseness가 가장 낮았다(2.34-2.47).
두 PPR baseline 모두 전 차원에서 낮았고 특히 uniform prior+PPR인 Baseline-2가 급락해 LLM prior의 탐색 편향 기여를 입증했다.
state-eval 모델 간 일치도 강해 signed median은 거의 0, absolute median 0.13-0.16, Kendall's τb=0.60-0.79였다.
**Prior policy ablation(MSI, GPT-4.1 prior vs uniform):** uniform prior는 평균 2.5배 많은 경로를 admit하고 단백질 편중이 심했으며(f_PPI-only 0.39 vs 0.13, r_BP:Prot 0.29 vs 0.64), LLM prior는 더 적고 긴 process-매개 경로로 편향되어(평균 경로 길이 7.89 vs 5.97, 경로 수 7.58 vs 19.56) 완전성과 간결성을 동시에 개선했다.

---

## Limitation

저자들이 명시한 한계는 두 가지다.
첫째, 평가가 15개 약물-질병 쌍에 그쳐 다양성 층화에도 불구하고 더 광범위한 검증이 필요하다.
둘째, LLM 추론 비용과 희소한 정답 신호 때문에 체계적 하이퍼파라미터 최적화가 비자명하고 미탐색 상태로 남아, 현재 설정은 파일럿 실험에서의 수동 튜닝에 의존한다.
독자 관점에서 추가 한계는, 이 프레임워크가 신약-질병 기전 도메인(생의학 KG, PageRank 필터, DrugBank/DrugMechDB 근거)에 특화되어 있어 "구조화된 지식 위 합성적 추론의 일반 패러다임"이라는 주장에도 불구하고 타 도메인으로의 일반화가 실증되지 않았다는 점이다.
또한 EPA-OW precision 0.27이 보여주듯 검증되지 않은 매개 노드를 포함하는 경향이 있어, 생성된 "대안 기전"이 진짜 타당한 생물학인지 환각인지 구분하려면 도메인 전문가 검증이 필요하다.
MSI처럼 정답이 없는 그래프에서는 평가 자체가 LLM-as-judge에 의존하므로 ICC가 높더라도 동일 모델 계열의 공유된 편향을 측정하고 있을 위험(순환성)이 존재한다.
마지막으로 prior·state-eval 모두 매 탐색마다 다수의 LLM 호출을 요구해 계산 비용이 크고, 이것이 평가 규모와 하이퍼파라미터 탐색을 동시에 제약하는 실질적 병목으로 작용한다.

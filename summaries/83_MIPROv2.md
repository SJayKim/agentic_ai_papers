# 83. MIPROv2: Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs

> 📄 **저자**: Krista Opsahl-Ong, Michael J. Ryan, Josh Purtell, David Broman, Christopher Potts, Matei Zaharia, Omar Khattab
> 📚 **학회/발표 기관**: EMNLP 2024
> 📅 **발표 날짜**: 2024.06
> 🔗 **arXiv**: https://arxiv.org/abs/2406.11695
> 💻 **코드**: https://github.com/stanfordnlp/dspy

---

## Problem

LM Program(여러 모듈을 체이닝한 다단계 파이프라인, 예: multi-hop RAG, ReAct, CoT 앙상블)이 NLP 태스크에서 SOTA를 달성하고 있지만, 각 모듈의 prompt를 수동으로 작성하는 "prompt engineering"이 병목이다.
기존 prompt optimizer(APE, OPRO, EvoPrompt)는 단일 prompt를 대상으로 설계되어, 모듈별 gold label이나 중간 metric이 없는 multi-stage program에는 직접 적용할 수 없다.
DSPy의 BootstrapFewShot은 rejection sampling으로 few-shot demonstration만 최적화하며, free-form instruction을 튜닝하는 기능이 부재하다.
또한 multi-stage 환경은 두 가지 근본적 난점을 가진다 — (1) Proposal challenge: 모듈 수가 늘수록 prompt 조합 공간이 폭발적으로 커진다, (2) Credit assignment challenge: 최종 task-level metric만 관측되므로 어느 모듈의 어떤 instruction/demo가 성능에 기여했는지 식별하기 어렵다.
LM weight/log-prob/모듈별 라벨에 접근 불가하다는 약한 가정 하에서 이 문제를 풀어야 하므로, gradient 기반·RL 기반 prompt tuning 기법(Prefix-Tuning, RLPrompt 등)도 사용 불가하다.

---

## Motivation

핵심 직관: instruction과 demonstration은 서로 다른 역할을 담당하므로 함께 최적화해야 한다.
Demonstration은 reasoning 패턴과 출력 포맷을 가르치고, instruction은 few-shot으로 표현하기 어려운 조건부 규칙(conditional rule)이나 task의 미묘한 제약을 전달한다.
실제로 HotPotQA Conditional처럼 답변 포맷이 "person이면 X, date면 Y" 식으로 분기하는 경우 demo만으로는 규칙을 전부 보여줄 수 없다.
또 다른 직관: proposal LM에게 raw dataset 통계, program control flow, bootstrap된 성공 trace를 "grounding" context로 제공하면 무작위 instruction보다 task-aware한 후보를 생성할 수 있다.
Credit assignment 문제는 noisy black-box 최적화이므로, full-train 평가 대신 mini-batch surrogate(Bayesian optimization)를 사용해 평가 호출 수를 줄이면서도 joint sensitivity를 학습할 수 있다는 통찰을 차용했다.
Greedy 방식(한 모듈씩 고정 후 변경)은 종속적 모듈 상호작용을 놓치고 호출 비용도 더 들기 때문에 surrogate 모델이 더 효율적이라는 예비 실험 결과가 동기를 강화했다.

---

## Method

MIPRO(Multi-prompt Instruction PRoposal Optimizer)는 세 단계로 구성된다.

1. **Bootstrap Demonstrations (Step 1)**
   - Training input x를 program Φ에 통과시켜 모듈별 입출력 trace τ를 얻는다.
   - metric μ(Φ(x), x') ≥ λ인 trace만 채택해, 각 모듈의 candidate few-shot 후보로 저장한다.
   - 이 과정을 반복해 모듈당 N개의 K-shot demonstration set을 확보한다 (rejection sampling).

2. **Propose Instructions (Step 2)**
   - 별도의 proposer LM(기본 GPT-3.5, temperature 0.7)이 instruction 후보를 생성한다.
   - Grounding context로 (a) dataset summary(raw data 패턴 요약), (b) program control flow summary(코드 구조), (c) Step 1의 bootstrap된 성공 trace, (d) plain-text "tip" on prompt engineering을 함께 제공한다.
   - 각 모듈마다 N개의 instruction 후보를 생성한다.

3. **Bayesian Search (Step 3)**
   - 각 모듈의 instruction 선택과 demo set 선택을 latent categorical variable로 두고, uniform prior에서 시작한다.
   - Optuna의 Tree-structured Parzen Estimator(TPE)를 surrogate model로 사용해 joint distribution을 모델링한다.
   - Propose: TPE sampling rule로 (instruction, demo) 조합을 추출 → 파라미터화된 Φ를 mini-batch B개 샘플로 평가 → score로 TPE prior 업데이트.
   - 매 S 스텝마다 평균 점수가 가장 높은 후보를 full train set에서 재평가한다.
   - 최종적으로 full evaluation에서 최고 점수를 받은 (instruction, demo) 조합을 반환한다.

**변형들**: 0-Shot MIPRO는 instruction만 최적화(few-shot context 비용 절감용), Bayesian Bootstrap은 demo만 최적화, MIPRO++는 proposal hyperparameter(grounding 사용 여부, temperature, tip 등) 자체를 meta-optimize한다.
비교 baseline으로 Module-Level OPRO(모듈별 instruction과 score history를 proposer LM에 주고 새 instruction 생성)와 Bootstrap Random Search(demo만 random search)를 함께 정의했다.

---

## Key Contribution

1. **LM program prompt 최적화 문제의 형식화**: 모듈 m개·변수 집합 V·metric μ 하의 black-box 최적화로 정식화하고 Algorithm 1에서 Initialize/Propose/Update/ExtractOptimizedSets 인터페이스로 일반화 — 기존 단일 prompt optimizer를 multi-stage로 확장하는 공통 framework 제공.
2. **Proposal 3전략 + Credit assignment 3전략의 설계 공간 매핑**: Bootstrap demo, Grounding, Learning to Propose × Greedy, Surrogate(Bayesian), History-based의 조합을 체계적으로 비교 — 어떤 조합이 어떤 task에 맞는지 lesson화.
3. **MIPRO 알고리즘**: instruction grounding + TPE surrogate + mini-batch 평가를 결합해 instruction과 demo를 joint 최적화 — 7개 task 중 5개에서 baseline 대비 최대 +13% accuracy.
4. **DSPy Optimizer Benchmark 공개**: 7개 다양한 task(HotPotQA, HotPotQA Conditional, Iris, Iris-Typo, Heart Disease, ScoNe, HoVer)로 LM program optimizer 평가 표준 제공.
5. **5가지 practitioner lesson**: demo가 일반적으로 가장 영향력 크지만 conditional rule 태스크에선 instruction이 결정적, grounding의 task-의존성 등.

---

## Experiment & Results

**Benchmark**: 7개 task — HotPotQA(multi-hop QA, 2모듈/3 LM call), HotPotQA Conditional(답변 포맷 조건부), Iris/Iris-Typo(분류 CoT), Heart Disease(2모듈 ensemble), ScoNe(nested negation NLI), HoVer(3-hop retrieval, 4모듈). Train 500 / Dev 500 / Test 2k.
**Models**: Task LM은 Llama-3-8B, Proposer LM은 GPT-3.5(temperature 0.7), 어려운 task(ScoNe, HoVer)는 teacher로 GPT-4o.
**Budget**: 20~50 trial, 5회 평균, Wilcoxon signed-rank test(p<0.05).

핵심 수치 (Test):
- **ScoNe**: 베이스라인 69.1 → MIPRO 79.4 (**+10.3**); Bootstrap RS 75.4, Module-Level OPRO 73.5.
- **HotPotQA**: 36.1 → MIPRO 46.4 (**+10.3**); Bootstrap RS 45.8.
- **HoVer**: 25.3 → MIPRO 39.0 (**+13.7**, 최대 13% 개선의 근거); 0-Shot MIPRO 33.1.
- **HotPotQA Conditional**: 6 → MIPRO 23.3 (**+17.3**); 0-Shot MIPRO 14.6, Bootstrap RS 10.4 — instruction-only가 demo-only를 능가하는 유일한 케이스로 Lesson 3을 입증.
- **Iris**: 40.9 → MIPRO 88.6, Bootstrap RS 94.1; **Iris-Typo**: 32 → MIPRO 68.7, 0-Shot MIPRO 56.7 (instruction이 typo 교정).
- **Heart Disease**: 26.8 → Bootstrap RS 79.2, MIPRO 74.2.

**Ablation/Lesson**: (1) demo 최적화가 instruction-only를 7개 중 6개에서 통계적으로 능가, (2) MIPRO(joint)가 7개 중 5개에서 최고, (3) Module-Level OPRO에서 Grounding 제거(-G) 시 ScoNe만 향상되고 HotPotQA·HoVer는 하락 — proposal 전략의 task-의존성, (4) 0-Shot MIPRO++의 학습된 importance score는 bootstrap demo와 tip이 가장 중요함을 보여줌.

---

## Limitation

저자 명시: (1) 고정된 budget 하의 실험이라 극단적 low/high budget regime에서의 dynamic은 미검증 — 예컨대 low budget에선 mini-batch 기반 0-Shot MIPRO가, high budget에선 MIPRO++가 우위일 가능성.
(2) Proposer/Task LM이 고정(GPT-3.5 + Llama-3-8B)이라 모델 조합에 따른 일반화 검증 부족.
(3) Optimizer가 hand-written seed prompt 없이 복잡한 task rule을 inferring하는 능력에 제약 — Heart Disease처럼 분류 기준이 추상적인 경우 grounding만으론 부족.
독자 관점 한계: (4) Bayesian TPE는 categorical 후보 집합 내 선택만 최적화하므로 instruction 자체를 evaluation feedback으로 개선하는 closed loop가 없다(MIPRO++가 부분적으로만 해결).
(5) 7개 task가 주로 QA·분류·NLI 중심이라 코드 생성·tool use 같은 long-horizon agent task로의 확장성은 미검증.
(6) Mini-batch B 크기와 evaluation noise의 trade-off, surrogate model 수렴까지의 호출 비용이 실제 적용 시 main cost — 작은 dataset에선 over-fitting risk.
(7) Proposer LM의 품질이 instruction 후보 다양성을 결정하므로 weaker open-source LM만 쓸 수 있는 환경에서는 성능이 제한될 수 있다.

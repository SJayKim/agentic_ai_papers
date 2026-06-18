# 85. Automatic Prompt Optimization with "Gradient Descent" and Beam Search (ProTeGi)

> 📄 **저자**: Reid Pryzant, Dan Iter, Jerry Li, Yin Tat Lee, Chenguang Zhu, Michael Zeng
> 📚 **학회/발표 기관**: EMNLP 2023
> 📅 **발표 날짜**: 2023.05
> 🔗 **arXiv**: https://arxiv.org/abs/2305.03495
> 💻 **코드**: https://github.com/microsoft/LMOps/tree/main/prompt_optimization

---

## Problem

LLM은 prompt에 의해 성능이 크게 좌우되지만, 좋은 prompt를 수작업으로 작성하는 과정은 trial-and-error에 의존하는 비효율적이고 전문성이 요구되는 작업이다.
이를 자동화하려는 기존 연구는 크게 두 갈래로 나뉘는데, 둘 다 실무 적용에 한계가 있다.
첫째, soft prompt tuning이나 prompt generator 학습 방식은 LLM의 내부 hidden state나 gradient에 대한 접근을 가정하지만, 실제 practitioner는 대부분 black-box API(GPT-3.5/4 등)로만 LLM과 통신한다.
또한 이렇게 직접 최적화된 prompt는 자연어로서 해석 불가능한 형태가 되어 인간이 읽거나 검수할 수 없다.
둘째, RL 기반 phrase-level 편집(AutoPrompt, RLPrompt, GrIPS, TEMPERA 등)이나 Monte-Carlo 기반 paraphrase search(APE) 등 discrete prompt 조작 방법은 API만으로 접근 가능하지만, 편집의 "방향"이 없어 본질적으로 random walk에 가깝다.
이로 인해 탐색이 비효율적이고 의미적으로 일관된 개선을 보장하지 못한다.

---

## Motivation

연속 공간에서의 gradient descent가 효과적인 이유는 "오류를 줄이는 방향"이라는 명확한 신호를 제공하기 때문이다.
저자들은 텍스트 prompt 공간에서도 동일한 비유를 적용할 수 있다고 본다 — 즉 prompt가 어떤 입력에서 틀렸는지를 LLM에게 보여주면, LLM이 "이 prompt의 어떤 점이 문제인지"를 자연어로 비판할 수 있고, 이 비판 자체가 일종의 "textual gradient" 역할을 한다.
그런 다음 또 다른 LLM 호출을 통해 "이 비판의 반대 방향"으로 prompt를 편집하면, gradient descent의 update step과 유사한 directed 개선이 가능하다.
이 접근은 differentiation을 LLM 피드백으로, backpropagation을 LLM editing으로 치환하는 Socratic dialogue 형태의 비유다.
방향이 명확하므로 directionless Monte-Carlo search보다 효율적이며, 동시에 자연어 prompt를 유지하기 때문에 해석 가능성도 보존된다.
다만 한 번에 여러 후보 prompt가 생성되므로 탐색 공간이 커지는데, 이를 beam search와 bandit 기반 selection으로 관리한다.

---

## Method

ProTeGi는 초기 prompt $p_0$, 학습 데이터 $D_{tr}$, metric $m(\cdot)$을 입력받아 최적 prompt $\hat{p}$를 출력한다.
전체는 beam search의 outer loop와 textual gradient의 inner expansion으로 구성된다.

1. **Beam 초기화 및 반복 (Algorithm 1)**: beam $B_0 = \{p_0\}$에서 시작해, $r$번의 search depth 동안 각 prompt를 expand한 후 select하는 과정을 반복한다.

2. **Expansion Step (Algorithm 2) — 핵심**:
   - **(a) Mini-batch 평가**: 현재 prompt $p$를 학습 데이터에서 샘플링한 mini-batch $D_{mini}$(크기 64)에 적용해 LLM 예측을 얻는다.
   - **(b) 실패 사례 수집**: 예측이 라벨과 다른 오류 예시 집합 $e = \{(x_i, y_i): LLM_p(x_i) \neq y_i\}$를 추출한다.
   - **(c) Textual gradient 생성**: 정적 메타 prompt $\nabla$에 현재 prompt와 오류 예시들을 채워 LLM에 입력하면, LLM은 "이 prompt가 이런 예시에서 틀린 이유"를 자연어 비판으로 출력한다. 한 오류 그룹당 $m=4$개의 gradient를 생성.
   - **(d) Prompt 편집**: 또 다른 메타 prompt $\delta$에 (현재 prompt, gradient, 오류)를 채워 LLM에 입력하면, gradient가 지적한 문제를 수정한 새로운 prompt 후보들을 출력한다 — 즉 "gradient의 반대 의미 방향"으로 prompt를 이동.
   - **(e) Monte-Carlo paraphrase**: 편집된 후보 각각에 대해 LLM에게 의미 보존 paraphrase를 요청해 $p=2$개의 추가 후보를 만들어 local search 다양성 확보.

3. **Selection Step — Best Arm Identification으로의 환원**: 후보 prompt들을 전체 데이터셋에서 평가하는 것은 비용이 크므로, 이를 bandit의 best arm identification 문제로 재정의한다. 각 prompt = arm, prompt를 데이터 한 점에 평가 = arm pulling, 목표는 최소 query로 상위 $b$개 arm 식별.
   - **UCB / UCB-E**: $Q_t(p) + c\sqrt{\log t / N_t(p)}$ 식을 따라 exploration-exploitation 균형 (Algorithm 3).
   - **Successive Rejects (SR)** / **Successive Halving (SH)**: 하이퍼파라미터 없이 단계마다 하위 prompt 제거(SR은 1개, SH는 하위 절반), $n_t$를 점진적으로 늘려 budget을 effectively 분배 (Algorithm 4, Equation 1).

4. **하이퍼파라미터**: beam size $b=4$, search depth $r=6$, mini-batch 64, gradient 생성 시 오류 4개씩 묶고 후보당 paraphrase 2개, bandit 전 후보 무작위 8개로 제한.

---

## Key Contribution

1. **Textual gradient라는 개념적 프레임워크**: numerical gradient descent의 differentiation/backpropagation 단계를 각각 LLM feedback과 LLM editing으로 치환하여, discrete text 공간에서도 directed optimization을 가능하게 했다.
2. **API-only / nonparametric 설계**: LLM 내부 hidden state나 추가 reward model에 의존하지 않으며, 어떤 metric (F1뿐 아니라 user comment까지)도 score function으로 사용 가능.
3. **Beam search + bandit selection의 결합**: 후보 prompt 평가를 best arm identification으로 환원하여 query budget을 효율적으로 분배 — UCB, UCB-E, Successive Rejects, Successive Halving 4가지 알고리즘 비교 분석.
4. **해석 가능한 최적화 과정**: 모든 gradient와 prompt 수정이 자연어로 남아 있어, 인간이 검수하고 디버깅할 수 있다.

---

## Experiment & Results

**데이터셋**: 4개 분류 task — Jailbreak(LLM jailbreak 탐지, 다국어 452개, 본 논문에서 새로 정의), Ethos(영어 hate speech 997개), Liar(영어 fake news 4000개), Sarcasm(아랍어 sarcasm 10000개). 각 task에서 dev 50개, test 150개 샘플링, 3회 평균.

**셋업**: 기본 LLM은 `gpt-3.5-turbo` (2023.01 버전), 평가는 binary F1.

**Baseline**: Monte-Carlo(APE 스타일, directionless paraphrase search), RL(GrIPS / TEMPERA 스타일 phrase-level operation), AutoGPT(AI 스스로 feedback loop 결정), Uniform evolutionary search.

**주요 결과 (Figure 3)**:
- ProTeGi가 4개 task 전부에서 baseline을 능가.
- 평균적으로 **MC 대비 +3.9% F1, RL 대비 +8.2% F1** 개선.
- 초기 prompt $p_0$ 대비 **+15.3%**, AutoGPT 대비 **+15.2%** (최대 단일 task에서 +31% 개선).
- query budget을 12 → 50으로 늘려도 이 격차는 비교적 일정하게 유지.

**Beam Search Ablation (Table 1)**: Jailbreak에서 No-iter 0.80 / Greedy DFS 0.82 / Beam (ProTeGi) **0.85**, Liar에서 0.63 / 0.63 / **0.67**, Sarcasm에서 0.87 / 0.85 / **0.88** — beam이 일관되게 우위.

**Bandit Algorithm (Table 2, 50 query budget)**: Jailbreak에서 Unif 0.77 / UCB **0.85** / UCB-E 0.83 / SR 0.82 / SH 0.80. Liar에서는 UCB-E 0.67이 최고. 모든 bandit이 Uniform보다 우수하며, 이론상 best arm identification에 최적인 SR보다 UCB-style이 실제로는 잘 작동 (exploration parameter c=2.0).

**Base Model 비교 (Table 3)**: GPT-3(davinci) 0.73 / InstructGPT 0.83 / ChatGPT 0.86 / GPT-4 **0.86** on Sarcasm; Jailbreak에서는 GPT-3 0.55 → GPT-4 **0.88**. RLHF-tuned 모델이 textual gradient 생성에 결정적.

**Learning curve (Figure 4)**: 약 3 step에서 peak에 도달, 이후 overfitting / local minima 경향.

**Variance (Table 5)**: ProTeGi 0.95 (Ethos), 0.87 (Sarcasm), 0.81 (Jailbreak), 0.64 (Liar) — MC 대비 일관되게 높지만 SE가 약간 더 큼.

---

## Limitation

저자가 명시한 한계: (1) LLM API의 rate limit으로 인해 gradient 생성·beam candidate 전체 평가에 많은 호출이 필요하고, 작은 query budget에서도 1편 최적화에 1시간 이상 걸릴 수 있어 대규모/실시간 application에는 부적합.
(2) 실험이 4개 classification task로만 한정되어 generation, parsing, summarization 등 더 복잡한 task로의 일반화는 미검증.
독자 관점의 추가 한계: (3) 약 3 step에서 빠르게 overfitting / local minima에 빠지는 경향이 관찰되어 step size나 regularization을 도입하지 않은 점이 약점 — 저자도 "adaptive step size"는 future work로 남겨둠.
(4) Gradient 품질이 base LLM에 크게 의존(GPT-3 0.55 vs GPT-4 0.88)하여 약한 모델에서는 directed search의 이점이 사라진다.
(5) Qualitative 분석(Table 4)에서 보듯 gradient가 가끔 잘못된 방향(예: Jailbreak에서 task 자체를 child grooming 분류로 바꿔버림)을 가리키며, 이를 자동으로 거를 메커니즘이 없다.
(6) Few-shot example은 고정된 채로 prompt instruction만 최적화하므로, prompt와 example의 joint optimization은 다루지 않는다.

# Rethinking Fine-Tuning when Scaling Test-Time Compute: Limiting Confidence Improves Mathematical Reasoning

> **논문 정보**: Feng Chen, Allan Raventós, Nan Cheng, Surya Ganguli, Shaul Druckmann (Stanford University, University of Michigan), NeurIPS 2025, arXiv:2502.07154 (2025.02)

---

## Problem

LLM이 복잡한 수학/코딩 태스크에서 성능을 내는 핵심 축은 pretraining뿐 아니라 test-time compute scaling이다.
test-time 전략 중 가장 단순한 것은 pass@N, 즉 N개의 독립 샘플을 뽑아 그 중 하나라도 정답이면 성공으로 간주하는 coverage 메트릭이다.
기존 fine-tuning 관례는 pass@N 같은 test-time 전략과 무관하게 cross-entropy(CE) 손실로 수행되며, 훈련과 추론이 사실상 분리(decoupled)되어 있다.
그러나 저자들은 Llama-3-8B-base를 MATH 데이터셋에 CE로 fine-tune하면 pass@1은 단조 증가하지만 pass@N (특히 N≥256)은 학습이 길어질수록 단조 **감소**하는 역설을 발견한다.
이는 고전적 overfitting과 다른 새로운 형태의 overfitting으로, 훈련 손실이 테스트 전략과 misalign되어 있다는 명확한 증거다.
더 나아가, 이 misalignment는 SFT에만 국한되지 않고 GRPO 같은 RL 기반 post-training에서도 재현되어 현재 표준 훈련 파이프라인 전반이 large-N pass@N 시나리오에 부적합함을 암시한다.
따라서 "test-time compute를 pass@N으로 스케일하려 할 때, 우리는 어떤 훈련 손실을 사용해야 하는가?"라는 질문이 본 논문의 핵심 문제다.

---

## Motivation

Lemma 4.1은 단일 문제 상황에서 pass@1과 pass@N이 상호 단조 관계에 있어 CE 최소화가 pass@N 최대화와 일치함을 보여주지만, 다중 문제에서는 이 동치가 깨진다.
toy 예시로, 문제 x1에 100% 정답·x2에 100% 오답인 모델 1은 pass@1=50%로 고정되는 반면, 두 문제 모두 정답에 0.1·오답에 0.9를 주는 모델 2는 pass@1=10%로 낮지만 pass@N은 N→∞에서 100%로 수렴한다.
즉 **confidence를 낮춰 탐색(exploration)하는 정책**이 높은 N에서는 확신에 찬 착오(exploitation)보다 유리할 수 있음을 시사한다.
저자들은 이 직관을 well-calibrated policy 가정 하에서 일반화하여, 최적 pass@N 정책의 max confidence 상한(Lemma 4.2)과 하한(Lemma 4.3)이 모두 N에 대해 단조 감소한다는 이론을 증명한다.
따라서 큰 N에서는 unconfident exploration, 작은 N에서는 confident exploitation이 최적이며, CE 훈련은 후자만 유도하기 때문에 large-N 영역에서 반드시 suboptimal이 된다.
Figure 1(a,b)에서 CE로 학습된 모델의 greedy completion 신뢰도 분포가 epoch이 지날수록 1 근처로 몰리지만 정답 비율은 작아지는 "overconfident yet wrong" 현상이 관찰되어 이 이론적 예측이 경험적으로 확증된다.
결과적으로 훈련 단계의 손실 함수 설계가 test-time 전략과 co-design되어야 하며, 이는 단순한 engineering trick이 아니라 information-theoretic 수준에서 exploration-exploitation trade-off를 조율하는 근본적 작업이다.

---

## Method

1. **Direct Coverage Optimization (DCO) 손실 정의**: ℓ_DCO^N(x,y) = -log(1 - (1-p̂(y|x))^N)로, 모델이 N번 샘플링에서 정답 y를 적어도 한 번 내놓을 확률의 음수 로그를 직접 최소화한다.
2. **Gradient 분해**: ∇ℓ_DCO = F(N, p̂(y|x)) · ∇ℓ_CE, 여기서 F(N,p̂) = N(1-p̂)^(N-1)·p̂ / (1-(1-p̂)^N)는 overconfidence regularization factor로 기존 CE 기울기를 재가중한다.
3. **Regularizer 특성**: F는 p̂에 대해 단조 감소하며, N=1이면 F=1(=CE와 동일), 큰 N에서 p̂ ≳ 1/N을 넘는 순간 F≈0이 되어 기울기를 소거함으로써 특정 예제에 대한 과신 축적을 자연스럽게 차단한다.
4. **유효 배치 보정**: F가 일부 샘플을 사실상 dead로 만들기 때문에, 임계값 ε를 두고 F<ε인 예제는 다른 예제로 교체해 유효 배치 크기를 유지한다.
5. **Hyperparameter N' 선택**: 훈련 시 사용하는 N'이 테스트 시 pass@N의 N과 근접할 때 Pareto 최적 성능에 도달하므로, N'은 목표 test-time budget에 맞춰 선정한다.
6. **Easy example down-weighting 효과**: F는 쉬운 예제(모델이 이미 자신있는)에서 자동으로 작아져 hard example mining과 유사한 효과를 내며, 이는 별도의 데이터 큐레이션 없이도 어려운 샘플에 학습 용량을 집중시킨다.
7. **Theorem proving으로의 확장 (naive DCO)**: k-step 증명에서 p̂(y|x)를 한 proof trajectory 전체의 결합 확률 ∏ p̂(y[i]|x[i])로 치환하여 동일 공식으로 fine-tune한다.
8. **Step-wise DCO (DCO_step)**: 각 proof step별로 tactic 분포에 대해 DCO를 적용, training-time의 N_eff가 test-time 탐색 트리의 branching factor를 대략적으로 결정하도록 설계한다 — 작은 N_eff는 좁고 깊은 탐색, 큰 N_eff는 넓고 얕은 탐색.
9. **Branching factor 이론**: 길이 k의 증명이 pass@N으로 발견되려면 대략 N ≳ N_eff^k가 필요하므로, 긴 증명은 작은 N_eff, 짧은 증명은 큰 N_eff가 유리함을 공식화한다.
10. **Ensemble 전략**: 서로 다른 N_eff로 학습한 모델들을 합쳐서 짧은/긴 증명 모두에서 상호보완적 탐색 전략을 활용한다.
11. **CoT용 근사 DCO (DCO_a)**: CoT 설정에서는 p̂(y|x)를 직접 계산할 수 없으므로, 다수의 CoT 샘플 c에서 나온 답 y의 empirical mode 확률로 p̂(y_mode|x)를 추정하여 DCO를 적용한다.
12. **실험 프로토콜**: Llama-3-8B-base를 MATH 12,000 문제로 fine-tune(500 테스트), Qwen2.5-Math-1.5B를 LeanDojo로 theorem proving fine-tune, 비교군으로 CE와 GRPO 포함.

---

## Key Contribution

1. **Misalignment 현상 최초 정량화**: pass@1과 pass@N이 다중 문제 환경에서 일반적으로 정렬되지 않음을 이론(Lemmas 4.1~4.3)과 실험(Table 1)으로 동시에 증명하여, fine-tuning/test-time 협력 설계의 필요성을 확립했다.
2. **Overconfidence-as-impediment 가설 검증**: CE 학습이 greedy completion 신뢰도를 1 근처로 몰지만 그 중 상당수가 오답임을 직접 측정(Figure 1a,b)하고, 이를 pass@N 저하의 메커니즘으로 귀인한다.
3. **DCO 손실 제안**: pass@N coverage를 직접 최대화하는 미분 가능한 손실과 그 gradient 형태(F regularizer)를 명시적으로 도출하여, CE의 드롭인 대체로 쓸 수 있게 했다.
4. **Pareto frontier 관측**: N'과 N의 관계에 대한 최적성 구조를 실험으로 밝혀, 작은 N에서는 작은 N'이, 큰 N에서는 큰 N'이 우세한 frontier를 traced (Figure 2a).
5. **Theorem proving을 위한 step-wise DCO**: N_eff를 통해 test-time 탐색 트리의 branching factor를 훈련 단계에서 제어할 수 있음을 보여, depth/breadth trade-off를 튜닝 가능한 파라미터로 격상시켰다.
6. **Ensemble 접근법**: 서로 다른 N_eff 모델을 합쳐 MiniF2F에서 CE 대비 절대 +6.2%p 향상을 달성, diversity-through-training의 효용을 입증했다.
7. **GRPO의 overconfidence 확인**: RL 기반 post-training인 GRPO 역시 pass@1만 편중 최적화하여 pass@64에서 DCO_a에 뒤짐을 보여, 본 발견이 SFT 한정이 아니라 일반 현상임을 시사한다.

---

## Experiment

MATH(Llama-3-8B-base, direct answer) 실험에서 CE로 4 epoch 학습 시 pass@1은 개선되나 pass@256은 epoch이 늘수록 **monotonically 감소**함을 Table 1에서 확인했다.
DCO(N'=256)로 같은 조건 학습 시 greedy confidence 분포가 CE 대비 현저히 낮은 구간에 머무르며, 여러 N'별 pass@N 곡선이 Pareto frontier를 형성한다(Figure 2a).
CoT 설정(Table 3)에서 epoch 3 기준 pass@1은 CE 9.0%, GRPO 12.6%, DCO_a 8.3%로 GRPO가 우세하지만 pass@16은 CE 41.6%, GRPO 35.8%, DCO_a 42.6%로 역전되고, pass@64는 CE 61.7%, GRPO 46.3%, DCO_a **63.1%**로 DCO_a가 최고다.
Epoch 5 pass@64에서는 DCO_a 64.3% vs GRPO 35.4%로 **약 29%p 격차**가 벌어져 GRPO의 overconfidence가 큰 N에서 치명적임을 드러낸다.
Theorem proving(Qwen2.5-Math-1.5B, LeanDojo) naive DCO는 MiniF2F pass@4k에서 CE 37.4% → 37.4%~38.7%로 미미한 개선에 그쳤다.
DCO_step으로 Mathlib pass@4k는 N_eff=16에서 56.5%(CE 55.6% 대비 +0.9%p), MiniF2F는 N_eff=8에서 39.5%(CE 37.4% 대비 +2.1%p)로 향상됐다.
Ensemble(N_eff∈{1,4,8,16,32}, 5× test compute)은 Mathlib 62.2%, MiniF2F **43.6%**로 동일 compute의 CE(pass@20k=57.0%/39.5%) 대비 +5.2%p/+4.1%p 초과 성능을 보였다.
Figure 1(d)는 N'이 커질수록 DCO로 훈련된 모델의 greedy confidence 분포가 더 강하게 low-confidence 쪽으로 밀려나, F factor의 regularization 강도가 이론 예측대로 작동함을 시각화한다.
추가로 AIME24 OOD 테스트셋에서도 CE의 overconfidence 경향이 재현되어 일반성이 확인되며(Section C.4), Llama-3-70B-base에서도 동일 현상이 관찰된다(Section C.3).

---

## Limitation

저자 언급 한계는 분석이 SFT + pass@N이라는 가장 단순한 조합에 국한되어 있다는 점으로, best-of-N·tree-of-thought·MCTS 같은 정교한 test-time 전략으로의 확장은 미완이다.
또 pass@N은 정답 여부를 판별하는 oracle verifier(컴파일러, proof checker, unit test 등)가 존재하는 상황에서만 정의되므로, 검증기가 없는 일반 자연어 생성 태스크에는 직접 적용 불가하다.
GRPO에서도 overconfidence가 나타남을 관찰했으나 RL 방법 전반에 대한 포괄적 분석은 본 논문 범위를 벗어난다고 명시한다.
도메인 측면에서 수학 추론과 형식 정리 증명에만 실험이 집중되어, 코드 생성처럼 unit test가 자연스런 verifier인 영역으로의 일반화가 남겨진 과제다.
독자 관점 한계로, ℓ_DCO의 F factor는 p̂가 매우 작을 때 기울기가 극도로 불안정할 수 있어 ε-threshold 같은 임시방편이 필요하고, 이는 하이퍼파라미터 민감도를 증가시킨다.
훈련 시 N'이 테스트 시 N과 맞을 때만 최적이어서, 테스트 budget을 미리 알지 못하는 배포 시나리오에서는 ensemble 같은 비용이 추가로 요구된다.
또한 well-calibrated policy라는 이론적 가정은 Figure 13에서 경험적으로 검증되지만 일반 LLM이 항상 이 조건을 만족한다는 보장은 없다.
마지막으로 Llama-3 계열과 Qwen2.5-Math 외 다양한 아키텍처·규모·pretraining corpus에서의 재현 검증이 제한적이어서, 결론의 보편성은 추가 연구가 필요하다.

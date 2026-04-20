# Reinforcing Multi-Turn Reasoning in LLM Agents via Turn-Level Reward Design

> **논문 정보**: Quan Wei, Siliang Zeng, Chenliang Li, William Brown, Oana Frunza, Wei Deng, Anderson Schneider, Yuriy Nevmyvaka, Yang Katie Zhao, Alfredo Garcia, Mingyi Hong (University of Minnesota, Texas A&M University, Prime Intellect, Morgan Stanley)
> **arXiv**: 2505.11821v2 (2025.10) | **학회**: -
> **코드**: Search-R1 기반 구현

---

## Problem

RL 알고리즘(GRPO, PPO)을 활용하여 LLM 에이전트를 훈련할 때, 대부분의 기존 방법은 최종 결과에 대한 sparse outcome reward만 사용한다.

이는 전체 trajectory를 단일 의사결정 단계로 취급하여 contextual bandit 문제로 환원되며, 다중 턴 상호작용의 구조를 무시한다.

특히 long-horizon multi-turn 추론 태스크에서 중간 단계에 대한 피드백이 없으면, 에이전트는 어떤 행동이 최종 정답에 기여했는지 학습하기 어렵다.

기존의 naive한 해결책은 중간 보상과 결과 보상을 단일 trajectory-level 신호로 병합하는 것이지만, 이는 advantage estimation을 부정확하게 만들어 credit assignment 문제를 야기한다.

그 결과 훈련이 불안정해지고 suboptimal trajectory를 조기에 가지치기할 메커니즘이 없어, 모든 trajectory를 끝까지 시뮬레이션해야 하는 비효율이 발생한다.

예컨대 search agent에서는 초기 쿼리 선택이 매우 중요하나, 중간 검색 피드백이 없으면 어떤 쿼리가 최종 정답 도출에 기여했는지 에이전트가 학습할 수 없다.

특히 multi-hop QA와 같이 여러 단계의 연쇄적 추론이 필요한 복잡한 과제에서는 이러한 sparse 신호의 한계가 극명하게 드러나 성능이 크게 저하된다.

또한 기존 PPO와 GRPO 기반 훈련은 훈련 중 잦은 crash를 유발하여 안정적 수렴이 어렵다는 실용적 문제까지 동반한다.

---

## Motivation

Multi-turn 에이전트 태스크에서는 각 턴(도구 호출과 그 결과)이 독립적인 의사결정 단위이므로, 턴 단위의 세밀한 보상 설계가 필요하다.

기존 GRPO는 trajectory-level advantage를 전체 턴에 균일하게 할당하여, 개별 턴의 기여도를 구분하지 못한다.

이를 turn-level MDP M = {S, A, P, R, γ}로 공식화하면 중간 보상을 자연스럽게 통합할 수 있으며, fine-grained credit assignment가 가능해진다.

또한 verifiable reward는 지나치게 엄격하여 정답과 형식이 약간만 달라도 부정 피드백을 받으므로, LLM-as-judge를 통한 유연하고 nuanced한 평가도 보완적으로 필요하다.

PPO의 critic model과 GAE를 활용하면, GRPO의 지수적 rollout 비용 문제 없이 토큰 수준의 advantage estimation이 가능하여 확장성을 확보할 수 있다.

또한 MT-GRPO는 모든 rollout이 동일 턴 수를 가져야 한다는 제약이 있어, 쿼리에 따라 가변적 턴 수가 필요한 실제 search 태스크에 적용하기 어려운 반면, MT-PPO는 이러한 제약을 해소한다.

Search agent의 경우 초기 쿼리의 retrieval 성공 여부, 출력 형식 준수, 과도한 검색 억제 등 다양한 중간 신호를 턴 단위로 활용하면 더욱 효과적인 학습이 가능하다.

---

## Method

1. **Turn-Level MDP 공식화**: Multi-turn 에이전트 상호작용을 M = {S, A, P, R, γ}로 정의한다. 상태 s ∈ S는 상호작용 이력, 행동 a ∈ A는 생성된 토큰 시퀀스이며, 목표는 ∑_k γ^k R(s_k, a_k)의 기대 누적 보상을 최대화하는 것이다.

2. **MT-GRPO (Multi-Turn GRPO)**: 중간 보상 {R^I_i}와 결과 보상 {R^O_i}를 분리하여 턴별 advantage를 계산한다. 2턴 설정에서 1턴 advantage는 A^MT-GRPO_{i,1} = A^I_i + α A^O_i, 2턴 advantage는 A^MT-GRPO_{i,2} = A^O_i로 정의되며, 각 advantage는 그룹 평균과 표준편차로 정규화된다.

3. **MT-GRPO의 한계**: K턴 설정에서 중간 advantage를 계산하려면 각 턴마다 G개의 rollout이 필요해 총 G^(K-1)개의 rollout이 필요하고 지수적 계산 비용이 발생하며, 한 그룹의 모든 rollout이 동일 턴 수를 가져야 하는 fixed-turn 제약이 존재한다.

4. **MT-PPO (Multi-Turn PPO)**: PPO의 critic model과 Generalized Advantage Estimation(GAE)을 활용하여 토큰 수준 advantage estimation을 수행한다. GAE는 A_t = ∑_l (γλ)^l δ_{t+l}, δ_t = r_t + γV_{t+1} - V_t로 계산된다.

5. **토큰 수준 보상 할당**: trajectory 마지막 토큰에 R^O를, 각 중간 턴 마지막 토큰에 R^I를, 그 외 토큰에는 0을 부여하여 turn-level 보상을 token-level signal로 변환한다.

6. **Outcome Verifiable Reward**: Exact Match Reward(정답 일치 + 형식 정확 시 1.0, 형식만 정확 시 0.2, 형식 오류 시 -1.0) + Format Reward(<think>과 <answer> 태그가 각각 1회씩, <think>이 <answer> 선행하는지 검증).

7. **Intermediate Verifiable Reward**: R^I_retrieval = 0.3(검색 결과에 정답 포함 시, 대소문자 무시 매칭), R^I_format = 0.1 또는 -0.2(<think><search><information> 태그 정확성), R^I_search = -λ_s · n_search(과도한 검색 억제 페널티, λ_s=0.1 default).

8. **최종 Intermediate Reward**: R^I = R^I_retrieval + R^I_format + R^I_search로 합산되며, retrieval 가중치는 answer보다 작게 설정하여 reward hacking 위험을 줄인다.

9. **LLM-as-Judge 보상**: Generative Reasoning Model(GRM)을 judge로 활용하여 step-by-step reasoning 후 rubric 기반 점수를 부여한다. 형식 정확성, 추론 품질, 검색 효과성을 평가하며 search penalty도 함께 적용한다.

10. **Rubric 설계**: 단순 outcome-level 평가가 아닌 각 턴의 출력을 구조적으로 평가하여 fine-grained 피드백을 제공, multi-turn agentic task의 본질과 정렬한다.

11. **훈련 파이프라인**: Search-R1 기반, Qwen2.5-7B를 base model로 사용. E5 retriever, 2018 Wikipedia dump 코퍼스, retrieved passage 수 3개, 최대 턴 수 N_max=4로 설정.

12. **Policy Loss Masking**: 검색 결과로 반환된 retrieved token에 대해 policy loss를 마스킹하여, 에이전트가 외부 검색 결과를 자기 출력처럼 학습하는 것을 방지한다.

13. **System Prompt**: Search-R1의 시스템 프롬프트를 그대로 사용하여 <think>, <search>, <information>, <answer> 태그 기반 reasoning-search 루프를 유도한다.

---

## Key Contribution

1. **Turn-level reward design의 첫 체계적 연구**: Multi-turn LLM 에이전트 훈련에서 턴 단위 보상의 중요성을 최초로 규명하고 이론적 분석을 제시.

2. **MT-GRPO와 MT-PPO 확장**: GRPO와 PPO를 multi-turn 변형으로 확장하여 fine-grained credit assignment를 가능하게 함.

3. **MT-PPO의 확장성**: critic model과 GAE로 MT-GRPO의 지수적 rollout 비용 문제를 해결하고 가변 턴 수를 지원하여 일반 에이전트 태스크에 적용 가능.

4. **체계적 보상 설계**: verifiable reward(exact match, format, retrieval existence, search count)와 LLM-as-judge reward 두 유형의 turn-level 보상을 체계적으로 설계.

5. **Search count penalty**: 과도한 도구 호출을 억제하고 훈련 안정성을 확보하는 메커니즘 제안, ablation으로 효과 검증.

6. **Granularity 분류**: 표 1을 통해 GRPO/MT-GRPO/PPO/MT-PPO의 reward와 advantage granularity를 체계적으로 비교 분석.

7. **Reasoning-augmented search agent 사례 연구**: 6개 QA 벤치마크에서 state-of-the-art 성능과 100% 근접 format correctness 달성.

---

## Experiment

6개 QA 데이터셋(NQ, TriviaQA, PopQA, HotpotQA, 2WikiMultiHopQA, Musique)에서 평가, Qwen2.5-7B 기반.

**Answer Correctness (Exact Match) 평균**:
MT-PPO **0.447** vs PPO-OR(0.432), PPO-MR(0.429), GRPO-MR(0.414), GRPO-OR(0.351), PPO(OTC) 0.399, PPO(StepSearch) 0.373.

**데이터셋별 MT-PPO 최고 성능**:
NQ **0.490** (PPO-OR 0.483 대비 +0.7%p), TriviaQA **0.647** (0.639 대비 +0.8%p), PopQA **0.459** (0.456 대비 +0.3%p).

**Multi-Hop QA 성능**:
HotpotQA **0.453** (PPO-OR 0.435 대비 +1.8%p), 2WikiMultiHopQA **0.424** (0.382 대비 +4.2%p), Musique **0.209** (0.199 대비 +1.0%p).

**Format Correctness 평균**: MT-PPO **0.999** vs PPO-OR(0.895), GRPO-OR(0.534), PPO(StepSearch) 0.555, base Qwen2.5-7B(0.101).

**Format 데이터셋별**: MT-PPO는 NQ 0.999, TriviaQA 0.997, PopQA 0.999, HotpotQA 0.998, 2Wiki 0.999, Musique 0.999로 모든 데이터셋에서 99.7% 이상.

**Training Dynamics**: MT-PPO는 100스텝 이내 빠르게 수렴하며 낮은 분산(5회 독립 run 기반). PPO는 HotpotQA에서 high variance와 성능 저하 관찰, GRPO는 훈련 중 지속적 crash 발생.

**Ablation (Search Count Reward)**: λ_s=0.0 제거 시 훈련 불안정, uncontrolled search usage, non-convergent rollout 발생; λ_s=0.1 유지 시 턴 수가 초기 감소 후 안정화되며 accuracy 향상.

**Ablation (Max Turns)**: N_max를 4→5→6으로 변경해도 accuracy 추세가 유사하여, 턴 제한에 robust함 입증.

**Base/Instruct 비교**: Qwen2.5-7B-Base 답변 정확도 평균 0.174, Instruct 0.320, MT-PPO 0.447로 각각 +0.273, +0.127의 개선.

**학습 효율**: MT-PPO는 첫 100스텝에서 급격한 초기 수렴을 보이며, PPO 대비 일관된 개선 곡선 유지.

---

## Limitation

MT-GRPO는 K턴 설정에서 G^(K-1)개의 rollout이 필요하여 지수적 계산 비용이 발생하며, 모든 rollout이 동일 턴 수를 가져야 하는 fixed-turn 제약으로 인해 가변 턴 수가 필요한 현실적 태스크에 적용이 어렵다.

MT-PPO는 MT-GRPO의 한계를 개선하지만 critic model 학습이라는 추가 비용과 메모리 요구가 수반되어, 대규모 모델 scaling 시 부담이 증가한다.

실험이 reasoning-augmented search(Wikipedia 검색) 단일 도메인에 한정되어, 코드 실행, 웹 브라우징, 계산기 호출 등 다양한 에이전트 유형으로의 일반화가 미검증이다.

Verifiable reward 설계가 태스크별로 수작업 세밀 튜닝을 요구하여(R^I_retrieval, R^I_format, R^I_search의 가중치), 새로운 도메인 확장 시 엔지니어링 비용이 크다.

LLM-as-judge의 경우 judge model의 평가 일관성과 비용 문제가 미해결이며, 특히 대량 rollout마다 judge 호출이 필요해 훈련 속도가 저하된다.

Qwen2.5-7B 단일 모델 크기에서만 실험하여, 모델 스케일(예: 1B, 14B, 70B)에 따른 turn-level reward의 효과 변화 분석이 부재하다.

최대 턴 수 N_max=4~6의 비교적 짧은 horizon에서 평가되어, 10턴 이상의 long-horizon 에이전트 환경에서의 확장성은 추가 검증이 필요하다.

Search count penalty 등 일부 설계는 reward hacking을 완화하지만, 더 복잡한 환경에서 새로운 reward hacking 패턴이 출현할 가능성이 남아있다.

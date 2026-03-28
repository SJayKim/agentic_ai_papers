# Reinforcing Multi-Turn Reasoning in LLM Agents via Turn-Level Reward Design

> **논문 정보**: Quan Wei, Siliang Zeng, Chenliang Li, William Brown, Oana Frunza, Wei Deng, Anderson Schneider, Yuriy Nevmyvaka, Yang Katie Zhao, Alfredo Garcia, Mingyi Hong (University of Minnesota, Texas A&M University, Prime Intellect, Morgan Stanley)
> **arXiv**: 2505.11821v2 (2025.10) | **학회**: -
> **코드**: Search-R1 기반 구현

---

## Problem

RL 알고리즘(GRPO, PPO)을 활용하여 LLM 에이전트를 훈련할 때, 대부분의 기존 방법은 최종 결과에 대한 sparse outcome reward만 사용한다. 이는 전체 trajectory를 단일 의사결정 단계로 취급하여, 다중 턴 상호작용의 구조를 무시하는 문제를 야기한다. 특히 long-horizon multi-turn 추론 태스크에서 중간 단계에 대한 피드백이 없으면, 에이전트는 어떤 행동이 최종 정답에 기여했는지 학습하기 어렵다. 기존의 naive한 해결책은 중간 보상과 결과 보상을 단일 trajectory-level 신호로 병합하는 것이지만, 이는 advantage estimation을 부정확하게 만들어 credit assignment 문제를 야기한다. 결과적으로 훈련이 불안정해지고, 특히 multi-hop QA와 같은 복잡한 추론 과제에서 성능이 저하된다.

---

## Motivation

Multi-turn 에이전트 태스크에서는 각 턴(도구 호출과 그 결과)이 독립적인 의사결정 단위이므로, 턴 단위의 세밀한 보상 설계가 필요하다. 기존 GRPO는 trajectory-level advantage를 전체 턴에 균일하게 할당하여, 개별 턴의 기여도를 구분하지 못한다. 이를 turn-level MDP로 공식화하면 중간 보상을 자연스럽게 통합할 수 있으며, fine-grained credit assignment가 가능해진다. 또한 verifiable reward는 지나치게 엄격할 수 있으므로, LLM-as-judge를 통한 유연한 평가도 보완적으로 필요하다. PPO의 critic model과 GAE를 활용하면, GRPO의 지수적 rollout 비용 문제 없이 토큰 수준의 advantage estimation이 가능하여 확장성을 확보할 수 있다.

---

## Method

1. **Turn-Level MDP 공식화**: Multi-turn 에이전트 상호작용을 M = {S, A, P, R, γ}로 정의한다. 상태 s는 상호작용 이력, 행동 a는 생성된 토큰 시퀀스이며, 목표는 턴 단위 누적 보상을 최대화하는 것이다.

2. **MT-GRPO (Multi-Turn GRPO)**: 중간 보상 {R^I}와 결과 보상 {R^O}를 분리하여 턴별 advantage를 계산한다. 1턴 advantage는 A^I + αA^O, 2턴 advantage는 A^O로, 이전 턴이 이후 턴의 기여도를 반영하는 구조이다.

3. **MT-GRPO의 한계**: K턴에 걸쳐 G^(K-1)개의 rollout이 필요하여 지수적 계산 비용이 발생하며, 모든 rollout이 동일 턴 수를 가져야 하는 제약이 있다.

4. **MT-PPO (Multi-Turn PPO)**: PPO의 critic model과 GAE를 활용하여 토큰 수준 advantage estimation을 수행한다. 턴 단위 보상을 토큰 수준으로 할당하되, 중간 턴의 마지막 토큰에 R^I를, trajectory 마지막 토큰에 R^O를 부여한다.

5. **Outcome Verifiable Reward**: Exact Match Reward(정답 일치 시 1.0, 형식만 정확 시 0.2, 형식 오류 시 -1.0) + Format Reward(태그 사용 검증).

6. **Intermediate Verifiable Reward**: Retrieval Existence Reward(검색 결과에 정답 포함 시 0.3), Format Reward(태그 정확성), Search Count Reward(과도한 검색 억제 페널티).

7. **LLM-as-Judge 보상**: GRM을 judge로 활용하여 rubric 기반 점수를 부여. 형식 정확성, 추론 품질, 검색 효과성을 평가.

8. **훈련 파이프라인**: Qwen2.5-7B 기반, E5 retriever, 2018 Wikipedia dump, 최대 턴 수 4, retrieved token에 대한 policy loss masking 적용.

---

## Key Contribution

1. **Turn-level reward design의 첫 체계적 연구**: Multi-turn LLM 에이전트 훈련에서 턴 단위 보상의 중요성을 최초로 규명.
2. **MT-GRPO와 MT-PPO 확장**: GRPO와 PPO를 multi-turn 변형으로 확장하여 fine-grained credit assignment를 가능하게 함.
3. **MT-PPO의 확장성**: critic model과 GAE로 MT-GRPO의 지수적 비용 문제를 해결하고 가변 턴 수를 지원.
4. **체계적 보상 설계**: verifiable reward와 LLM-as-judge reward 두 유형의 turn-level 보상을 체계적으로 설계.
5. **Search count penalty**: 과도한 도구 호출을 억제하고 훈련 안정성을 확보하는 메커니즘 제안.

---

## Experiment & Results

6개 QA 데이터셋(NQ, TriviaQA, PopQA, HotpotQA, 2WikiMultiHopQA, Musique), Qwen2.5-7B 모델.

**Answer Correctness (EM)**:
- MT-PPO 평균 **0.447** vs PPO-OR(0.432), PPO-MR(0.429), GRPO-MR(0.414), GRPO-OR(0.351).
- HotpotQA: **0.453** (PPO-OR 대비 +1.8%p), 2WikiMultiHopQA: **0.424** (+4.2%p), Musique: **0.209** (+1.0%p).

**Format Correctness**: MT-PPO 평균 **99.9%** vs PPO-OR(89.5%), GRPO-OR(53.4%), StepSearch(55.5%).

**Training Dynamics**: MT-PPO는 100스텝 이내 빠르게 수렴하며 낮은 분산. GRPO는 훈련 중 지속적 crash 발생.

**Ablation**: Search count reward 제거 시 훈련 불안정 및 최대 검색 횟수 도달로 종료 실패. N_max 4→6 변경해도 정확도 추세 유사.

---

## Limitation

MT-GRPO는 K턴 설정에서 G^(K-1)개의 rollout이 필요하여 지수적 비용 발생. MT-PPO는 이를 개선하지만 critic model 훈련이라는 추가 비용이 수반된다. 실험이 검색 에이전트(reasoning-augmented search) 단일 도메인에 한정되어, 코드 실행, 웹 브라우징 등 다양한 에이전트 유형으로의 일반화가 미검증이다. Verifiable reward 설계가 태스크별로 수작업이 필요하며, LLM-as-judge의 평가 일관성과 비용 문제도 미해결이다. Qwen2.5-7B 단일 모델 크기에서만 실험하여 모델 스케일에 따른 효과 변화가 미분석이다.

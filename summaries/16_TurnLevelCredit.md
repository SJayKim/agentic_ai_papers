# Reinforcing Multi-Turn Reasoning in LLM Agents via Turn-Level Reward Design

> **논문 정보**: Quan Wei, Siliang Zeng, Chenliang Li, William Brown, Oana Frunza, Wei Deng, Anderson Schneider, Yuriy Nevmyvaka, Yang Katie Zhao, Alfredo Garcia, Mingyi Hong (University of Minnesota, Texas A&M University, Prime Intellect, Morgan Stanley)
> **arXiv**: 2025.05
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | GRPO, PPO 등 RL 알고리즘이 멀티턴 LLM 에이전트 학습에 적용되지만, 전체 trajectory에 대한 sparse outcome reward만 사용하여 각 턴의 기여도를 정밀하게 할당하지 못한다. 중간 단계의 credit assignment가 부재하여, 에이전트가 어떤 행동이 최종 결과에 기여했는지 학습하기 어렵다. |
| **Motivation** | 검색 에이전트에서 좋은 쿼리를 초기에 선택하는 것이 관련 정보 검색에 결정적이지만, 턴 수준 피드백 없이는 어떤 쿼리가 도움이 됐는지 학습할 수 없다. 기존 연구들이 MDP로 모델링하면서도 intermediate reward를 sparse trajectory-level signal로 병합하여 advantage estimation이 부정확해진다. |
| **Limitation** | (1) MT-GRPO는 K턴에서 G^(K-1) 롤아웃이 필요하여 장기 멀티턴에서 계산 비용이 지수적으로 증가. (2) 검색 에이전트 태스크에만 검증되어, 코딩/브라우징 등 다른 에이전트 유형에서의 효과는 미확인. (3) LLM-as-judge 보상의 신뢰성이 judge 모델 품질에 의존. (4) Qwen2.5-7B 크기의 모델에서만 실험하여 더 큰 모델에서의 scaling 효과는 미검증. |

---

## Method

이 논문은 멀티턴 에이전트 RL에서 **턴 수준 보상 설계**를 체계적으로 연구하고, GRPO와 PPO를 멀티턴 변형으로 확장한다.

1. **문제 정의: Single-Turn vs Multi-Turn MDP**
   - Single-Turn: 전체 trajectory를 하나의 행동으로 취급, outcome reward만 사용 → `max E[R(x,y)]`
   - Multi-Turn MDP: 턴 단위 의사결정, 중간+최종 보상 누적 → `max E[Σγ^k R(s_k, a_k)]`
   - 중간 보상 없이 최종 보상만 있으면 MDP가 terminal reward MDP로 환원

2. **MT-GRPO (Multi-Turn GRPO)**
   - 2턴 설정에서: 1턴 advantage = `A^I_i + α·A^O_i`, 2턴 advantage = `A^O_i`
   - 중간 보상과 최종 보상을 각각 그룹 내 정규화하여 턴별 advantage 계산
   - 한계: K턴에서 G^(K-1) 롤아웃 필요 (지수적 복잡도), 모든 롤아웃이 동일 턴 수여야 함

3. **MT-PPO (Multi-Turn PPO)**
   - 크리틱 모델 + GAE(Generalized Advantage Estimation)으로 토큰 수준 advantage 계산
   - 턴 수준 보상 할당: 중간 턴의 마지막 토큰에 R^I, trajectory 마지막 토큰에 R^O, 나머지 0
   - MT-GRPO의 지수적 복잡도 문제를 해결하는 확장 가능한 대안

4. **턴 수준 보상 설계 (검색 에이전트 케이스 스터디)**
   - **Verifiable Reward**: 검색 결과에 정답이 포함되는지 이진 판정 → 엄격하지만 객관적
   - **LLM-as-Judge Reward**: LLM이 검색된 정보의 관련성·충분성을 연속적으로 평가 → 유연하지만 주관적
   - 두 유형 모두 outcome reward(최종 답변 정확도)와 결합

---

## Key Contribution

1. **턴 수준 보상 설계의 첫 체계적 연구**: 멀티턴 LLM 에이전트 RL에서 dense intermediate reward의 중요성을 최초로 체계적으로 분석.
2. **MT-GRPO/MT-PPO 알고리즘**: GRPO와 PPO를 턴 수준 보상을 활용하도록 확장. MT-PPO가 크리틱 모델 통해 확장 가능한 솔루션 제공.
3. **검색 에이전트에서의 실증**: 멀티턴 검색 태스크에서 턴 수준 보상이 trajectory 수준 보상 대비 안정성·수렴 속도·정확도 모두에서 우수함을 입증.
4. **보상 유형 비교**: Verifiable vs LLM-as-judge 보상의 특성과 적용 가능성을 분석.

---

## Experiment & Results

**모델**: Qwen2.5-7B, 멀티턴 검색 에이전트 (추론+검색 반복 → 최종 답변)

**데이터셋**: 다양한 QA 데이터셋 (멀티턴 검색 태스크로 변환)

**핵심 결과**:
- MT-GRPO vs GRPO-OR(outcome only): 도구 실행 보상과 exact match 보상 모두에서 MT-GRPO가 더 안정적이고 높은 수렴값 달성
- GRPO-MR(merged rewards)도 GRPO-OR보다 우수하나, MT-GRPO가 가장 우수
- MT-PPO: MT-GRPO와 유사한 성능이지만 지수적 롤아웃 문제 없이 확장 가능

**훈련 안정성**: 턴 수준 보상 사용 시 reward curve의 분산이 현저히 감소, EMA 스무딩 곡선에서 일관된 상승 추세

**포맷 정확도**: 100% format correctness 달성 — 턴 수준 보상이 에이전트의 구조화된 출력 학습을 촉진

**Verifiable vs LLM-as-Judge**: Verifiable이 더 안정적이나 적용 범위 제한, LLM-as-Judge가 더 유연하나 약간의 노이즈 존재

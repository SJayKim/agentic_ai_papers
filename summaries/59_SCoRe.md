# SCoRe: Training Language Models to Self-Correct via Reinforcement Learning

> **논문 정보**: Aviral Kumar, Vincent Zhuang, Rishabh Agarwal, Yi Su 외 (Google DeepMind)
> **arXiv**: 2409.12917 (2024.09)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 내재적 자기 교정(intrinsic self-correction)이 현재 LLM에서 거의 불가능하다는 것이 확인되었지만(Huang et al., 2023), 기존 학습 접근(SFT)은 분포 불일치(distribution mismatch)나 행동 붕괴(behavior collapse)에 빠져 효과적인 자기 교정을 학습하지 못한다. |
| **Motivation** | LLM은 많은 문제에서 정답에 도달할 "지식"을 보유하고 있지만 이를 올바르게 끌어내지 못한다. 모델 자신이 생성한 데이터에서 RL로 학습하면, 자신의 실수 분포에 맞는 교정 전략을 배울 수 있다. SFT의 두 가지 실패 모드를 구체적으로 해결하는 설계가 필요. |
| **Limitation** | 저자 언급: Gemini 모델에만 적용, 오픈소스 모델로의 이전 미검증. 독자 관점: 2단계 RL의 하이퍼파라미터 민감도, 보상 함수 설계에 대한 의존. |

---

## Method

1. **SFT 실패 모드 분석**
   - **분포 불일치**: 베이스 모델이 생성한 오류 데이터로 학습하면, 학습된 모델의 자체 오류 패턴과 달라 교정이 전이되지 않음
   - **행동 붕괴**: 나이브 RL은 1차 응답을 최대한 잘 생성하고 2차를 피상적으로 수정하는 쪽으로 수렴

2. **SCoRe: 2단계 멀티턴 RL**
   - **Stage 1 (초기화)**: 2차 응답만 RL로 학습하되, 1차 응답 분포를 베이스 모델에 가깝게 제약 → 행동 붕괴 방지를 위한 안정적 초기화
   - **Stage 2 (본 학습)**: 1차+2차 응답 모두에 대해 멀티턴 RL 수행. "자기 교정 진행도(progress)"에 대한 보상 보너스를 추가하여, 최종 정답이 아닌 교정 과정 자체를 보상

3. **온 폴리시 학습**: 모델 자신이 생성한 교정 궤적에서 학습하여 분포 불일치 해결
4. **보상 셰이핑**: 정답 보상 + 교정 진행도 보너스로, 1차→2차에서 의미 있는 개선을 장려

---

## Key Contribution

1. **최초의 유의미한 내재적 자기 교정 달성**: SFT/프롬프팅으로 불가능했던 자기 교정을 멀티턴 RL로 해결
2. **SFT 실패 모드의 체계적 분석과 해결**: 분포 불일치와 행동 붕괴를 2단계 RL로 각각 극복
3. **추론 시간 스케일링의 새 축**: 병렬 샘플링 대비 순차 자기 교정이 더 효율적인 영역 발견

---

## Experiment & Results

- **모델**: Gemini 1.0 Pro, Gemini 1.5 Flash
- **벤치마크**: MATH, HumanEval

**MATH (Gemini 1.5 Flash)**:
- Base 직접 생성: ~55% → Base 자기 교정: ~44% (-11.2%, 성능 하락)
- SCoRe 자기 교정: ~59% (+4.4%, 유의미한 향상)
- 절대 자기 교정 개선: **+15.6%** (base 대비)

**HumanEval**: 자기 교정으로 **+9.1%** 향상

**추론 시간 스케일링**: K개 샘플 예산에서, SCoRe의 순차 교정이 K개 병렬 독립 샘플보다 K≥약20에서 더 효과적 (self-consistency@K vs SCoRe sequential)

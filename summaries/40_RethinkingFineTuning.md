# Rethinking Fine-Tuning when Scaling Test-Time Compute: Limiting Confidence Improves Mathematical Reasoning

> **논문 정보**: Feng Chen, Allan Raventós, Nan Cheng, Surya Ganguli, Shaul Druckmann (Stanford University, University of Michigan)
> **arXiv**: 2502.07154 (2025.02)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 테스트 타임 연산 스케일링(pass@N 등)이 주목받지만, 학습 시 사용하는 Cross-Entropy(CE) 손실 함수가 pass@N과 정렬(aligned)되어 있는지는 미탐구. CE 학습을 길게 할수록 pass@1은 증가하지만 pass@N(N≥256)은 오히려 단조 감소하는 역설적 현상이 존재. |
| **Motivation** | pass@N은 N개 독립 샘플 중 하나만 맞으면 되는 가장 단순한 테스트 타임 전략인데, 이마저도 CE 학습과 비정렬됨. CE가 유도하는 과신(overconfidence)이 모델을 소수의 답에 확률을 집중시켜 탐색(exploration)을 저해하고, 대부분의 높은 신뢰도 답이 틀리면 pass@N이 구제 불가능. |
| **Limitation** | 저자 언급: pass@N이라는 단순 전략에 한정. 트리 탐색 등 더 복잡한 전략과의 정렬은 향후 과제. 독자 관점: 검증기(verifier) 존재를 전제하여, 검증기가 없는 일반 NLP 태스크에는 적용 불가. Llama-3 기반 실험으로 다른 아키텍처에서의 일반성 미검증. |

---

## Method

1. **CE 학습과 pass@N의 비정렬 발견**
   - Llama-3-8B를 MATH에서 CE 파인튜닝 후 pass@N 평가
   - pass@1: 에폭 증가에 따라 단조 증가 (CE 최적화 목표와 일치)
   - pass@256: 에폭 증가에 따라 **단조 감소** — 학습할수록 테스트 타임 스케일링 효과 악화

2. **원인 분석: 과신(Overconfidence)**
   - **단일 문제**: pass@N은 pass@1의 단조 함수이므로 비정렬 불가능
   - **복수 문제**: 모델이 일부 문제에 과신(정답에 확률 집중)하면, 맞는 문제는 항상 맞고 틀린 문제는 N번 시도해도 항상 틀림
   - CE 학습이 greedy completion의 확률을 지속적으로 높여 과신 유도 (Figure 1a)
   - **탐색-활용 트레이드오프**: pass@N이 클수록 낮은 최대 신뢰도(=많은 탐색)가 최적, pass@1이면 높은 신뢰도(=활용)가 최적 (Lemma 4.2, 4.3)

3. **DCO (Diversity-Encouraging Confidence-limiting Objective) 손실 함수**
   - pass@N 커버리지를 직접 최적화하는 손실 함수 유도
   - CE에 과신 정규화 항(F)을 추가: 모델 신뢰도가 N에 따른 상한을 초과하지 않도록 제약
   - N'이 클수록 더 강한 신뢰도 제한 → 더 많은 탐색 유도 (Figure 1c,d)
   - 실질적으로 "어려운 문제"에 더 큰 학습 가중치를 부여하는 효과

4. **확장**: CoT 추론 경로에 적용, 정리 증명(MiniF2F)에서 다양한 증명 트리 탐색에 적용

---

## Key Contribution

1. **CE 학습과 테스트 타임 스케일링의 비정렬 최초 발견 및 이론적 설명**: 과신이 pass@N 성능을 저해하는 메커니즘을 탐색-활용 트레이드오프로 형식화
2. **DCO 손실 함수**: pass@N을 직접 최적화하는 원칙적 대안 학습 목표로, CE 대비 일관된 pass@N 개선 달성
3. **학습-추론 공동 설계의 중요성 제기**: 전통적으로 분리된 학습 프로토콜과 테스트 타임 전략의 공동 최적화가 필수적임을 실증

---

## Experiment & Results

- **모델**: Llama-3-8B-base, Llama-3-70B-base
- **벤치마크**: MATH (500 테스트), MiniF2F (정리 증명)
- **비교**: CE 학습 vs DCO 학습, 다양한 N 값에서 pass@N

**MATH Direct Answer (Llama-3-8B)**:
- CE: pass@1 = 37.4% (4 epochs), pass@256 = 61.6% (1 epoch이 최고, 이후 하락)
- DCO (N'=256): pass@1 약간 하락하지만 pass@256 = **70%+** — CE 대비 유의미한 개선
- 과신 측정: CE 학습 후 greedy confidence 중앙값 ~0.9 vs DCO ~0.3

**MATH CoT (Llama-3-8B)**:
- DCO가 CE 대비 pass@N 프론티어에서 일관되게 우위 (pass@8~256에서 2~5%p 개선)

**MiniF2F 정리 증명**:
- 증명 트리 탐색에서 DCO가 CE 대비 개선된 커버리지 달성
- GRPO 학습도 과신 문제를 보임 → DCO의 일반적 유용성 시사

**핵심 통찰**: "더 많이 학습 = 더 나은 성능"은 pass@1에서만 성립. pass@N에서는 적절한 시점에 학습을 멈추거나, DCO로 과신을 제어해야 테스트 타임 스케일링의 효과를 극대화할 수 있음.

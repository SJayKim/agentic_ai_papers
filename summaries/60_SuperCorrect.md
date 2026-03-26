# SuperCorrect: Advancing Small LLM Reasoning with Thought Template Distillation and Self-Correction

> **논문 정보**: Ling Yang et al. (Peking University)
> **arXiv**: 2410.09008 (2024.10)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 소형 LLM(7B 등)은 복잡한 추론에서 대형 모델에 크게 뒤처지며, 기존 증류 방법은 고수준 사고 패턴과 자기 교정 능력을 동시에 전달하지 못한다. |
| **Motivation** | 대형 교사 모델의 추론 패턴을 "사고 템플릿"으로 추출하여 구조적으로 전달하고, 교차 모델 협력적 DPO로 자기 교정 능력을 강화하면 소형 모델의 추론 성능을 비약적으로 향상시킬 수 있다. |
| **Limitation** | 저자 언급: 교사 모델의 품질에 의존. 독자 관점: 사고 템플릿이 수학에 특화되어 범용 추론으로의 전이 불확실. |

---

## Method

1. **Stage 1 — 사고 템플릿 증류**: 대형 교사 LLM의 추론 과정에서 계층적 사고 템플릿(고수준 전략 + 세부 단계)을 추출하여 소형 모델에 SFT
2. **Stage 2 — 교차 모델 협력적 DPO**: 교사 모델과 학생 모델의 출력을 교차 비교하여 DPO 학습, 자기 교정 능력 강화

---

## Key Contribution

1. **사고 템플릿 + 자기 교정의 2단계 증류**: 추론 패턴과 교정 능력을 분리하여 체계적으로 전달
2. **SuperCorrect-7B**: DeepSeekMath-7B 대비 MATH에서 +7.8%

---

## Experiment & Results

- **모델**: SuperCorrect-7B (Llama/Qwen 기반)
- **벤치마크**: MATH, GSM8K
- SuperCorrect-7B: MATH에서 DeepSeekMath-7B 대비 +7.8% 향상

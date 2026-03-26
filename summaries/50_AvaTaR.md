# AvaTaR: Optimizing LLM Agents for Tool-Augmented Reasoning via Contrastive Reasoning

> **논문 정보**: Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Jure Leskovec, James Zou (Stanford University)
> **arXiv**: 2406.11200 (2024.06)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 도구 사용 프롬프트를 수동으로 최적화하는 것은 비효율적이고 태스크 특화적이다. 기존 자동 프롬프트 최적화는 도구 사용의 복잡한 추론 과정을 충분히 다루지 못한다. |
| **Motivation** | 도구 사용 성공/실패 사례를 대조적으로 분석하면, 어떤 도구 호출 패턴이 효과적인지 자동으로 학습할 수 있다. 이를 프롬프트에 반영하면 범용적 도구 사용 능력 향상 가능. |
| **Limitation** | 저자 언급: 프롬프트 최적화의 수렴 속도가 태스크 복잡도에 비례. 독자 관점: 대조적 추론이 도구 수가 매우 많을 때의 확장성 미검증. |

---

## Method

1. **대조적 추론 모듈**: 성공(positive)과 실패(negative) 도구 사용 궤적을 비교하여 효과적인 패턴 식별
2. **자동 프롬프트 최적화**: 대조적 분석 결과를 도구 사용 프롬프트에 반영하여 반복적으로 개선
3. 태스크별 재학습 없이 프롬프트 수준에서 도구 사용 능력을 향상

---

## Key Contribution

1. **대조적 추론 기반 도구 사용 최적화**: 성공/실패 사례 비교로 프롬프트를 자동 개선하는 최초의 접근
2. 검색 태스크에서 +14%, QA 태스크에서 +13% 평균 향상

---

## Experiment & Results

- **벤치마크**: 검색 태스크, QA 태스크
- 검색: 평균 +14% 향상, QA: 평균 +13% 향상
- 다양한 도구 조합에서 일관된 개선

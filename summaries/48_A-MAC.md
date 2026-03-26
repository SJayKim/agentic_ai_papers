# A-MAC: Adaptive Memory Admission Control for LLM Agents

> **논문 정보**: Guilin Zhang, Wei Jiang et al.
> **arXiv**: 2603.04549 (2026.03)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 메모리 시스템은 무엇을 저장할지 결정하는 "입장 제어(admission control)"가 체계적이지 않다. 무분별한 메모리 축적은 노이즈 증가와 검색 품질 저하를 야기한다. |
| **Motivation** | 메모리 검색과 업데이트에 대한 연구는 많지만, 어떤 정보를 장기 기억으로 승격시킬지 결정하는 문제는 구조적으로 다뤄지지 않았다. 이를 5가지 독립 요인으로 분해하면 체계적 의사결정이 가능. |
| **Limitation** | 저자 언급: ICLR 2026 Workshop 논문으로 예비적 검증. 독자 관점: 5가지 요인의 가중치 결정이 태스크 의존적이며, 자동 튜닝 메커니즘 미제공. |

---

## Method

1. **5가지 입장 요인**: 메모리 입장을 구조적 의사결정 문제로 정의하고 5개 요인으로 분해:
   - **Future Utility**: 미래에 유용할 가능성
   - **Factual Confidence**: 사실적 신뢰도
   - **Semantic Novelty**: 기존 메모리와의 의미적 차별성
   - **Temporal Recency**: 시간적 최신성
   - **Content-Type Prior**: 내용 유형별 사전 확률

2. 각 요인을 독립적으로 평가하고 조합하여 입장 여부를 결정

---

## Key Contribution

1. **메모리 입장 제어를 구조적 의사결정으로 형식화**: 기존에 암묵적이던 "무엇을 기억할 것인가"를 5가지 명시적 요인으로 분해
2. **모듈형 설계**: 각 요인을 독립적으로 교체·조정 가능한 프레임워크

---

## Experiment & Results

- ICLR 2026 MemAgent Workshop 논문으로, 예비 실험에서 무분별 축적 대비 메모리 품질 향상과 검색 정밀도 개선을 보고

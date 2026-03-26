# Plan-on-Graph: Self-Correcting Adaptive Planning of LLM on Knowledge Graphs

> **논문 정보**: Liyi Chen, Panrong Tong, Zhongming Jin, Ying Sun, Jieping Ye, Hui Xiong
> **arXiv**: 2410.23875 (2024.10)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | ToG 등 기존 KG 추론은 각 단계에서 독립적으로 탐색하여, 전체 추론 계획이 부재하고 오류가 누적된다. 중간 결과를 반성하고 계획을 수정하는 메커니즘이 없다. |
| **Motivation** | 복잡한 질문을 서브 목표로 분해하고, 각 서브 목표를 KG에서 탐색하면서 적응적 가이드(Guidance), 메모리(Memory), 반성(Reflection) 메커니즘으로 계획을 동적으로 수정하면 효율과 정확도를 동시에 향상시킬 수 있다. |
| **Limitation** | 저자 언급: 서브 목표 분해의 품질이 LLM 의존적. 독자 관점: 반성 메커니즘의 오버헤드. |

---

## Method

1. **서브 목표 분해**: 복잡한 질문을 해결 가능한 서브 목표 체인으로 분해
2. **적응적 가이드(Guidance)**: 현재 서브 목표에 기반하여 KG 탐색 방향을 동적으로 안내
3. **메모리(Memory)**: 이전 서브 목표의 탐색 결과를 저장하여 후속 탐색에 활용
4. **반성(Reflection)**: 탐색 결과가 불충분하면 자기 교정하여 탐색 전략을 수정

---

## Key Contribution

1. **계획 기반 KG 추론**: 서브 목표 분해 + 적응적 메커니즘으로 ToG의 무계획 탐색 한계 극복
2. **효율성**: ToG 대비 40.8% 적은 LLM 호출, ~76% 적은 출력 토큰

---

## Experiment & Results

- **벤치마크**: CWQ, WebQSP 등
- ToG 대비: 정확도 향상 + LLM 호출 40.8% 감소 + 출력 토큰 ~76% 감소

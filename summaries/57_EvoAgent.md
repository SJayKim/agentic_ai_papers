# EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms

> **논문 정보**: Siyu Yuan, Kaitao Song, Jiangjie Chen, Xu Tan, Dongsheng Li, Deqing Yang (Fudan University, Microsoft Research Asia)
> **arXiv**: 2406.14228 (2024.06)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 다중 에이전트 시스템(MAS) 구축 시 에이전트 역할, 수, 상호작용 패턴을 수동으로 설계해야 하며, 새 태스크마다 재설계가 필요하다. |
| **Motivation** | 생물학적 진화가 환경에 적응하는 다양한 개체를 만들듯, 진화 알고리즘(돌연변이, 교차, 선택)으로 단일 전문 에이전트에서 자동으로 다중 에이전트 시스템을 생성할 수 있다면, 인간 재설계 없이 태스크 해결 능력을 확장 가능. |
| **Limitation** | 저자 언급: 진화 과정의 수렴 속도가 태스크에 따라 상이. 독자 관점: 진화 과정에서 생성되는 에이전트의 다양성 보장이 어려울 수 있음. |

---

## Method

1. **진화 연산자 적용**: 기존 에이전트에 돌연변이(mutation), 교차(crossover), 선택(selection) 연산을 적용
2. **돌연변이**: 에이전트의 시스템 프롬프트, 도구 구성, 역할을 변형하여 새 에이전트 생성
3. **교차**: 두 에이전트의 특성을 조합하여 하이브리드 에이전트 생성
4. **선택**: 태스크 성능 기반으로 우수한 에이전트 조합을 선별
5. 단일 전문 에이전트에서 시작하여 반복 진화로 MAS를 자동 확장

---

## Key Contribution

1. **진화적 MAS 자동 생성**: 수동 설계 없이 단일 에이전트에서 다중 에이전트로 자동 확장하는 범용 방법론
2. 다양한 태스크에서 수동 설계 MAS 대비 일관된 성능 향상

---

## Experiment & Results

- 다양한 추론, 코드 생성, 수학 태스크에서 단일 에이전트 및 수동 설계 MAS 대비 성능 개선
- 진화 과정에서 에이전트 수와 역할 다양성이 자동으로 증가함을 확인

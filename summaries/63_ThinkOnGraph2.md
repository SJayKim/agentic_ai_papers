# Think-on-Graph 2.0: Deep and Faithful LLM Reasoning with KG-guided RAG

> **논문 정보**: Shengjie Ma et al. (IDEA Research, FinAI)
> **arXiv**: 2407.10805 (2024.07)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | ToG 1.0은 KG만 사용하여 비구조화 문서의 풍부한 컨텍스트를 활용하지 못하고, 기존 RAG는 KG의 구조적 추론 능력이 없다. KG와 문서 검색의 장점을 동시에 활용하는 방법이 필요. |
| **Motivation** | KG 빔 서치와 비구조화 문서 검색을 긴밀하게 교대(alternate) 수행하면, KG가 제공하는 구조적 추론 경로와 문서가 제공하는 상세 컨텍스트를 상호 보완적으로 활용 가능. |
| **Limitation** | 저자 언급: 두 소스 간 교대의 최적 빈도/시점이 태스크 의존적. 독자 관점: KG와 문서의 불일치 시 해결 전략 미명시. |

---

## Method

1. **KG 빔 서치 + 문서 검색 교대 수행**: 각 추론 단계에서 KG 탐색과 문서 검색을 번갈아 실행
2. KG가 구조적 추론 방향을 제시하면, 문서 검색이 세부 증거를 제공하고, 다시 KG가 다음 탐색 방향을 결정

---

## Key Contribution

1. **KG-RAG 하이브리드 프레임워크**: KG 탐색과 문서 검색을 긴밀하게 교대하는 최초의 통합 접근
2. **7개 벤치마크 중 6개에서 SOTA**: GPT-3.5 기반으로 SOTA 달성, LLaMA-2-13B를 GPT-3.5 수준으로 향상

---

## Experiment & Results

- **벤치마크**: 7개 지식 집약적 벤치마크
- GPT-3.5 + ToG 2.0: 7개 중 6개에서 SOTA
- LLaMA-2-13B + ToG 2.0: GPT-3.5 수준으로 향상

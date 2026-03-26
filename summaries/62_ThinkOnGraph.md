# Think-on-Graph: Deep and Responsible Reasoning of LLM on Knowledge Graph

> **논문 정보**: Jiashuo Sun, Chengjin Xu, Lumingyuan Tang, Saizhuo Wang 외 (IDEA Research, Xiamen Univ., USC, HKUST, Microsoft Research Asia)
> **arXiv**: 2307.07697 (2023.07)
> **코드**: https://github.com/IDEA-FinAI/ToG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 심층 추론과 최신 지식이 필요한 태스크에서 환각을 일으키며, 기존 LLM⊕KG 접근(SPARQL 변환 등)은 KG가 불완전하면 실패한다. LLM이 그래프 추론 과정에 직접 참여하지 않아 KG의 빈 부분을 보완하지 못한다. |
| **Motivation** | LLM을 KG 위에서 탐색하는 에이전트로 활용(LLM⊗KG)하면, KG의 구조적 지식과 LLM의 내재적 지식을 각 추론 단계에서 보완적으로 사용할 수 있다. KG에 관계가 없어도 LLM 지식으로 간접 경로를 발견 가능. |
| **Limitation** | 저자 언급: KG 규모에 따른 탐색 비용 증가. 독자 관점: 빔 서치 폭이 제한적이라 복잡한 다중 홉에서 최적 경로를 놓칠 수 있음. |

---

## Method

1. **LLM⊗KG 패러다임**: LLM이 KG 위에서 에이전트로 동작하며, 각 단계에서 관련 엔티티와 관계를 탐색
2. **반복적 빔 서치**: LLM이 현재 노드에서 가장 유망한 이웃을 선택하고, 충분한 정보가 모이면 추론 종료
3. **플러그앤플레이**: 추가 학습 없이 다양한 LLM과 KG에 적용 가능
4. **지식 추적 가능성**: 추론 경로가 KG 위의 명시적 경로로 기록되어 검증·수정 가능

---

## Key Contribution

1. **LLM⊗KG 패러다임**: LLM이 KG를 수동적으로 참조하는 것이 아니라 능동적으로 탐색하는 새 패러다임
2. **학습 불필요**: 프롬프트만으로 소형 LLM도 GPT-4를 특정 시나리오에서 초과
3. **9개 데이터셋 중 6개에서 SOTA** (학습 기반 방법 포함 비교)

---

## Experiment & Results

- **KG**: Freebase, Wikidata
- **벤치마크**: WebQSP, CWQ, GrailQA 등 9개 KGQA 데이터셋
- 9개 중 6개에서 SOTA (대부분 기존 SOTA가 추가 학습 필요)
- 소형 모델(LLaMA-2-13B) + ToG가 특정 시나리오에서 GPT-4를 능가

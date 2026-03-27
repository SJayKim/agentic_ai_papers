# Think-on-Graph: Deep and Responsible Reasoning of LLM on Knowledge Graph

> **논문 정보**: Jiashuo Sun, Chengjin Xu, Lumingyuan Tang, Saizhuo Wang 외 (IDEA Research, Xiamen Univ., USC, HKUST, Microsoft Research Asia)
> **arXiv**: 2307.07697 (2023.07)
> **학회**: ICLR 2024
> **코드**: https://github.com/IDEA-FinAI/ToG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 최신 지식이 필요하거나 다중 홉 추론이 필요한 태스크에서 환각을 일으킨다. 기존 LLM⊕KG(SPARQL 자동 생성 등)는 KG가 불완전하면 실패하며, LLM이 그래프 탐색에 직접 참여하지 않아 빈 공간을 보완하지 못한다. |
| **Motivation** | LLM을 KG 위에서 능동적으로 탐색하는 에이전트로 활용하는 LLM⊗KG 패러다임을 도입하면, 각 추론 단계에서 KG의 구조적 지식과 LLM의 내재적 지식을 상호 보완적으로 활용할 수 있다. |
| **Limitation** | KG 규모에 따라 탐색 비용이 증가하며, 빔 너비·깊이가 제한적이라 복잡한 다중 홉에서 최적 경로를 놓칠 수 있다. 대규모 KG(Wikidata)에서는 가지치기 난도가 높아진다. 단일 홉에서는 상대적 이점이 작다. |

---

## Method

### 1. LLM⊗KG 패러다임
기존 LLM⊕KG가 KG를 정적 참조 소스로 쓰는 것과 달리, LLM을 KG 위의 **능동적 탐색 에이전트**로 위치시킨다. 각 단계에서 어떤 관계와 엔티티를 확장할지 스스로 판단하며, KG에 필요한 관계가 없을 때는 LLM 내재적 지식으로 보완.

### 2. ToG 알고리즘 3단계 구조 (Initialization → Exploration → Reasoning)

**Initialization**: 질문에서 LLM이 topic entity를 추출하여 초기 추론 경로 P = {p₁,...,pN}의 시작점 구성

**Exploration (반복 빔 서치)**:
- *Relation Exploration*: 꼬리 엔티티에 연결된 후보 관계를 KG에서 수집(Search) → LLM이 상위 N개 선택(Prune)
- *Entity Exploration*: 선택된 관계로 후보 엔티티를 수집(Search) → LLM이 상위 N개 선택(Prune)하여 경로 확장

**Reasoning**: 현재 경로로 답 가능 여부를 LLM이 판단. 충분하면 답 생성, 불충분하면 Exploration 반복. 최대 D_max 도달 시 LLM 내재 지식으로 답변.

### 3. ToG-R (Relation-based 변형)
- 엔티티 가지치기에서 LLM 대신 랜덤 빔 서치 사용
- LLM 호출 횟수를 절반으로 절감 (2ND+D+1 → ND+D+1)
- 엔티티 리터럴 정보가 불명확할 때 오도된 추론 방지 효과

### 4. 지식 추적·수정
- 추론 경로를 KG 위의 명시적 트리플 체인으로 기록
- 오답 시 경로를 역추적하여 오류 트리플을 찾고 KG 직접 수정 가능

### 5. 플러그앤플레이
- 추가 학습 없이 다양한 LLM(ChatGPT, GPT-4, Llama-2)과 KG(Freebase, Wikidata)에 즉시 적용

---

## Key Contribution

1. **LLM⊗KG 패러다임**: LLM을 KG 위의 능동적 탐색 에이전트로 활용하는 새 패러다임
2. **9개 중 6개 SOTA**: 추가 학습 없이 다양한 KGQA·QA·Fact Checking 벤치마크에서 SOTA
3. **비용 효율적 경로**: Llama-2-70B+ToG가 GPT-4 단독을 능가
4. **지식 추적·수정 가능성**: 추론 경로의 명시적 기록으로 오류 추적 및 KG 개선 루프

---

## Experiment & Results

- **KG**: Freebase, Wikidata
- **9개 데이터셋**: CWQ, WebQSP, GrailQA, QALD10-en, Simple Questions, WebQuestions, T-REx, Zero-Shot RE, Creak
- **LLM**: ChatGPT, GPT-4, Llama-2-70B-Chat
- **설정**: 빔 N=3, 최대 깊이 D_max=3

**주요 결과**:
- **GrailQA**: ToG(GPT-4) **81.4** vs CoT(ChatGPT) 28.1 (+53.3%p)
- **Zero-Shot RE**: ToG(GPT-4) **88.3** vs CoT(ChatGPT) 28.8 (+59.5%p)
- **WebQSP**: ToG(GPT-4) **82.6** vs Prior FT SOTA(DeCAF) 82.1 — 학습 없이 초과
- **CWQ**: ToG(GPT-4) **69.5** vs Prior FT SOTA 70.4 — 0.9%p 이내

**소형 모델 + ToG**: Llama-2-70B + ToG CWQ 53.6 > CoT(GPT-4) 46.0

**CoT→ToG 향상 폭**: GPT-4에서 CWQ +23.5%p, WebQSP +15.3%p — 모델이 강할수록 KG 활용 이점 큼

**가지치기 비교**: LLM 프루닝이 BM25/SentenceBERT 대비 CWQ +8.4%p, WebQSP +15.1%p 우위

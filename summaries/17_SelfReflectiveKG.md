# Self-Reflective Planning with Knowledge Graphs: Enhancing LLM Reasoning Reliability for QA

> **논문 정보**: Jiajun Zhu, Ye Liu, Meikai Bao, Kai Zhang, Yanghai Zhang, Qi Liu (University of Science and Technology of China)
> **arXiv**: 2505.19410 (2025.05)
> **코드**: https://anonymous.4open.science/r/SRP-E06C

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 내부 지식이 불충분할 때 환각을 일으키며, KG와 통합하더라도 기존 방법은 불완전하거나 사실적으로 일관되지 않은 추론 경로(reasoning path)를 생성한다. 특히 올바른 관계를 무시하고 잘못된 중간 엔티티를 선택하는 문제가 빈번하다. |
| **Motivation** | KG 기반 QA에서 추론 경로의 신뢰성이 최종 답변 정확도를 결정한다. 기존 방법(ToG, PoG 등)은 경로 생성 후 오류를 반성·수정하는 메커니즘이 부재하여, 한 번 잘못된 관계를 선택하면 이후 전체 경로가 틀어진다. 인간의 자기 성찰적 문제 해결을 모방한 반복적 계획-반성 프레임워크가 필요하다. |
| **Limitation** | (1) Reference Searching이 KNN 기반이므로 참조 사례의 품질에 의존하며, 참조 베이스 구축에 사전 작업 필요. (2) 반복적 반성이 LLM 호출을 다수 발생시켜 latency와 비용 증가. (3) 3개 데이터셋(WebQSP, CWQ, GrailQA)에서만 검증. (4) KG의 불완전성 자체는 해결하지 못하며, KG에 없는 정보에 대한 답변은 불가. |

---

## Method

SRP(Self-Reflective Planning)는 KG 기반 QA에서 **참조 기반 계획과 반복적 반성**으로 추론 경로의 신뢰성을 높이는 프레임워크다.

1. **Reference Searching (참조 검색)**
   - 질문의 임베딩을 PLM으로 계산 → KNN으로 참조 베이스에서 유사한 사례 검색
   - 참조 사례: 질문 + KG에서 답을 찾는 추론 경로 + 정답
   - 검색된 참조가 이후 계획·반성 과정을 가이드

2. **Path Planning (경로 계획)**
   - **Relation Check**: 토픽 엔티티 e_q의 1-hop 관계를 KG에서 조회, LLM이 질문과의 관련성 점수 매김 → 상위 K개 초기 관계 R0 선정
   - **Path Generation**: LLM이 토픽 엔티티에서 시작하여 초기 관계 R0를 활용해 전체 추론 경로 p 생성
   - Relation Check로 첫 관계의 불확실성을 줄여 경로 생성 신뢰도 향상

3. **Knowledge Retrieval (지식 검색)**
   - 생성된 추론 경로 p를 KG에서 실체화하여 트리플 시퀀스 S = {(e_d, r_d, e_{d+1})} 검색
   - 예측 관계와 실제 KG 관계 간 매칭

4. **Reflection and Reasoning (반성 및 추론) — 핵심 반복 루프**
   - **Sequence Judge**: 검색된 트리플 시퀀스를 프루닝하여 무관한 경로 제거
   - **Path Edit**: 판정 메시지에 기반하여 LLM이 추론 경로를 수정
   - **Answering**: 답이 검색되면 참조를 활용하여 최종 답변 생성
   - 답이 없으면 수정된 경로로 Knowledge Retrieval → Reflection을 반복

---

## Key Contribution

1. **자기 반성적 추론**: KG 기반 QA에서 LLM이 추론 경로를 반복적으로 판단·수정하는 최초의 자기 성찰 프레임워크. 한 번에 올바른 경로를 찾지 못해도 반성을 통해 수렴 가능.
2. **참조 기반 가이드**: 유사 사례를 참조로 제공하여 계획과 반성의 품질을 높이는 실용적 접근.
3. **Relation Check**: 1-hop 관계 사전 검증으로 경로 생성 초기 단계의 오류를 방지.

---

## Experiment & Results

**데이터셋**: WebQSP, CWQ(ComplexWebQuestions), GrailQA

**비교 대상**: ToG, PoG, RoG, Interactive-KBQA, StructGPT, Pangu, KG-Agent 등

**WebQSP (Hits@1, F1)**:
- SRP(GPT-4o-mini): Hits@1 **80.8**, F1 **76.4** vs ToG 76.2/-, PoG 79.0/-, Interactive-KBQA 68.5/-
- SRP(GPT-3.5-turbo): Hits@1 73.3, F1 66.1

**CWQ (Hits@1, F1)**:
- SRP(GPT-4o-mini): Hits@1 **67.2**, F1 **59.5** vs ToG 58.2/-, PoG 62.5/-

**GrailQA (Hits@1, F1)**:
- SRP(GPT-4o-mini): Hits@1 **77.2**, F1 **72.3**

**Ablation**:
- w/o Reference: WebQSP F1 76.4→72.8 (-3.6) — 참조의 기여 확인
- w/o Relation Check: WebQSP F1 76.4→73.1 (-3.3) — 초기 관계 검증의 중요성
- w/o Reflection: WebQSP F1 76.4→71.5 (-4.9) — 반성 메커니즘이 가장 큰 기여

# SUBQRAG: Sub-Question Driven Dynamic Graph RAG

> **논문 정보**: Jiaoyang Li, Junhao Ruan, Shengwei Tang, Saihan Chen, Kaiyan Chang, Yuan Ge, Tong Xiao, Jingbo Zhu (Northeastern University, NiuTrans Research)
> **arXiv**: 2510.07718 (2025.10)
> **코드**: https://github.com/ljy1228/SubQRAG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 Graph RAG는 복잡한 질문 전체를 단일 단계로 그래프 진입점을 검색하여, 추론 과정을 분해하지 못하고 각 논리적 홉에 대해 검색 초점을 동적으로 조정하지 못한다. 사전 구축된 KG의 정적이고 불완전한 특성이 이를 악화시키고, 초기 진입 노드의 부정확함이 전체 추론 체인으로 오류 전파. |
| **Motivation** | 멀티홉 QA에서 단일 단계 검색은 하나의 지배적 토픽에 집중하여 다른 홉에 필요한 정보를 누락한다. 서브 질문으로 분해하면 각 홉을 독립적으로 검색·검증할 수 있고, KG가 불완전하면 원본 문서에서 새 트리플을 추출하여 동적으로 업데이트할 수 있다. |
| **Limitation** | 저자 언급: 서브 질문 분해의 품질이 LLM 능력에 의존. 독자 관점: 동적 그래프 업데이트가 쿼리 시점에 발생하여 응답 지연 증가. 서브 질문 간 의존 관계가 복잡할 때 순차 처리의 한계. |

---

## Method

1. **오프라인 인덱싱**: LLM으로 텍스트에서 엔티티·관계를 추출하여 코퍼스 수준 KG 구축 (트리플 ⟨h, r, t⟩ 형태)

2. **질문 분해 및 재작성 (Question Decomposition & Rewriting)**
   - 복잡한 원본 질문을 검증 가능한 서브 질문 체인으로 분해
   - 후속 서브 질문은 이전 서브 질문의 답변을 포함하도록 재작성하여 일관성 유지

3. **검색 및 동적 그래프 업데이트**
   - 각 서브 질문에 대해 KG에서 관련 트리플 검색
   - KG에 필요한 정보가 없으면: 원본 문서에서 새 트리플을 추출하여 **실시간으로 KG 업데이트**
   - 동적 업데이트로 정적 KG의 불완전성 극복

4. **Graph Memory 기반 답변 생성**
   - 모든 서브 질문에서 사용된 트리플을 "Graph Memory"로 집계
   - 구조화되고 추적 가능한 증거 경로를 LLM에 제공하여 최종 답변 생성
   - 전체 문서가 아닌 관련 트리플만 제공하므로 컨텍스트 윈도우 효율적 활용

---

## Key Contribution

1. **서브 질문 기반 동적 검색**: 복잡한 질문을 분해하여 각 홉의 검색 초점을 독립적으로 조정, 단일 단계 검색의 한계 극복
2. **실시간 KG 업데이트**: 사전 구축된 KG의 불완전성을 쿼리 시점에 원본 문서에서 새 트리플을 추출하여 보완하는 동적 메커니즘
3. **Graph Memory**: 추론 과정의 모든 근거 트리플을 구조화된 서브그래프로 집계하여 추적 가능한 증거 경로 제공

---

## Experiment & Results

- **벤치마크**: HotpotQA, 2WikiMultihopQA, MuSiQue (멀티홉 QA)
- **비교**: NaiveRAG, GraphRAG, RAPTOR, HippoRAG 등

**Exact Match (EM) 결과**:
- SubQRAG가 3개 벤치마크 모두에서 일관된 EM 향상 달성
- 특히 다중 홉이 깊은 MuSiQue에서 가장 큰 개선폭
- 동적 그래프 업데이트가 정적 KG 기반 방법 대비 불완전 정보 보완에 효과적

**Ablation**: 서브 질문 분해 제거 시 성능 하락 가장 큼, 동적 업데이트 제거 시 KG 커버리지가 낮은 데이터셋에서 특히 하락, Graph Memory 제거 시 답변의 근거 추적성 저하

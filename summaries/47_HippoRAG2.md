# HippoRAG 2: Towards Efficient and Robust Long-Term Memory for LLM Agents

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su (Ohio State University / UIUC)
> **arXiv**: 2502.14802 (2025.02) — ICML 2025
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 표준 RAG는 벡터 검색에만 의존해 사실 기억(factual memory)에는 강하지만, 연상 기억(associativity, 멀티홉 추론)과 의미 파악(sense-making)에는 취약하다. GraphRAG·LightRAG·RAPTOR 등 구조 보강 RAG는 이 두 능력을 일부 개선하지만, 오히려 단순 사실 QA에서 표준 RAG보다 현저히 성능이 떨어지는 의도치 않은 저하가 발생한다. 기존 HippoRAG 1.0은 NER 기반 엔티티 매칭에 의존하여 컨텍스트 손실이 크고, 패시지 수준의 밀집 정보를 KG에 통합하지 못한다. |
| **Motivation** | 인간의 장기 기억은 사실 기억·연상 기억·의미 파악 세 가지를 동시에 지원한다. LLM 에이전트의 비파라메트릭 지속 학습 시스템도 세 차원 모두에서 표준 RAG를 능가해야 하며, 이를 위해 KG에 패시지 노드를 도입(Dense-Sparse Integration)하고 온라인 LLM 인식 기억(recognition memory)을 활용해야 한다. |
| **Limitation** | (1) PPR 그래프 탐색의 깊이 한계 — 매우 복잡한 다단계 추론 체인에서는 탐색 커버리지가 부족할 수 있다. (2) 온라인 LLM 호출(트리플 필터링)이 검색 지연을 증가시켜 실시간 응용에 부담. (3) 코퍼스가 지속적으로 확장될 때 멀티홉 성능은 두 방법 모두 유사하게 저하되어 장기 지속 학습 시나리오에서의 한계가 명확하다. (4) 대화형 에피소딕 메모리나 초장문 컨텍스트 시나리오에 대한 검증은 미래 과제. |

---

## Method

### 오프라인 인덱싱

1. **OpenIE 기반 트리플 추출**: Llama-3.3-70B-Instruct로 각 패시지에서 스키마 없는 KG 트리플(subject, relation, object) 추출. 추출된 phrase는 KG의 phrase node가 됨
2. **유의어 엣지 추가**: NV-Embed-v2로 phrase node 쌍의 벡터 유사도를 계산, 임계값 초과 쌍에 synonym edge 추가하여 서로 다른 패시지 간 동의어 연결
3. **Dense-Sparse Integration — 패시지 노드 도입**: HippoRAG 1.0의 phrase node(sparse)만의 KG에서, 각 패시지를 passage node로 추가하고 `contains` context edge로 phrase node와 연결. KG가 개념적 정보와 문맥적 정보를 동시에 포함

### 온라인 검색 — Deeper Contextualization

4. **Query-to-Triple 링킹**: HippoRAG 1.0의 NER-to-Node 대신 쿼리 전체를 임베딩하여 KG 내 트리플 전체와 직접 매칭. 트리플은 개념 간 관계를 담아 쿼리 의도와의 정렬이 더 정확. Ablation에서 NER-to-Node 대비 Recall@5 평균 +12.5%
5. **Recognition Memory (트리플 필터링)**: 상위 k개 트리플 검색 후 LLM이 무관한 트리플을 제거. 인간의 재인 기억에서 영감. 프롬프트는 DSPy MIPROv2 옵티마이저로 튜닝

### PPR 기반 그래프 탐색

6. **시드 노드 선정**: 필터링된 트리플에서 phrase node를 시드로, 초기 우선순위는 평균 랭킹 점수로 결정
7. **Passage Node 시드 추가**: passage node도 시드로 포함 (weight factor 0.05로 phrase node와 균형)
8. **PPR 실행**: KG 전체에 확률 질량 전파. Context edge를 통해 passage node도 확률 질량을 받아 멀티홉 관련 패시지 부상
9. **최종 패시지 선택**: PPR 결과 상위 5개 패시지를 LLM QA 리더에 제공하여 최종 답변 생성

---

## Key Contribution

1. **세 가지 메모리 차원 동시 개선**: 사실 기억(NQ, PopQA), 연상 기억(MuSiQue, 2Wiki, HotpotQA, LV-Eval), 의미 파악(NarrativeQA) 모두에서 표준 RAG를 능가한 최초의 구조 보강 RAG
2. **Dense-Sparse Integration**: phrase node(sparse)에 passage node(dense)를 추가하여 개념과 문맥 정보를 통합하는 설계
3. **Query-to-Triple + Recognition Memory**: NER 기반 엔티티 매칭을 쿼리-트리플 임베딩 매칭 및 LLM 필터링으로 대체하여 검색 정밀도 크게 향상
4. **비파라메트릭 지속 학습**: 파라미터 수정 없이 코퍼스를 동적으로 확장할 수 있는 방식으로, 지속 학습 시나리오에 강건함 입증

---

## Experiment & Results

- **벤치마크**: 7개 데이터셋 — NQ, PopQA (Simple QA), MuSiQue, 2Wiki, HotpotQA, LV-Eval (Multi-Hop), NarrativeQA (Discourse)
- **구현**: Llama-3.3-70B-Instruct, NV-Embed-v2(7B)
- **평가**: QA F1, Passage Recall@5

**QA 결과 (F1)**:
- HippoRAG 2 평균: **59.8** vs NV-Embed-v2: 57.0 (+2.8p), HippoRAG 1.0: 53.1 (+6.7p)
- 2Wiki 멀티홉: HippoRAG 2 **71.0** vs NV-Embed-v2 61.5 (+9.5p)
- LV-Eval: HippoRAG 2 **12.9** vs NV-Embed-v2 9.8 (+3.1p)
- NQ(factual): HippoRAG 2 **63.3** vs HippoRAG 1.0 55.3 (+8.0p)

**검색 성능 (Recall@5)**:
- 평균: HippoRAG 2 **78.2** vs NV-Embed-v2 73.4 (+4.8p)
- 2Wiki: HippoRAG 2 **90.4** vs NV-Embed-v2 76.5 (+13.9p)
- HotpotQA: HippoRAG 2 **96.3** vs NV-Embed-v2 94.5

**Ablation (Recall@5 평균)**:
- Full: 87.1 / NER-to-Node로 교체: 74.6 (-12.5p) / Passage Node 제거: 81.0 (-6.1p) / 트리플 필터 제거: 86.4 (-0.7p)

**Dense Retriever 유연성 (MuSiQue Recall@5)**:
- GTE-Qwen2-7B: Dense 63.6 → HippoRAG 2 68.8 (+5.2p)
- GritLM-7B: Dense 66.0 → HippoRAG 2 71.6 (+5.6p)
- NV-Embed-v2: Dense 69.7 → HippoRAG 2 74.7 (+5.0p)
- 다양한 리트리버에서 일관된 +5p 향상 확인

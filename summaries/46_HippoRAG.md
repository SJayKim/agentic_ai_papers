# HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su (Ohio State University, Stanford University)
> **arXiv**: 2405.14831 (2024.05)
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 현재 RAG 시스템은 각 패시지를 독립적으로 인코딩하여, 패시지 경계를 넘어 지식을 통합(knowledge integration)해야 하는 태스크에서 실패한다. 멀티홉 QA에서 서로 다른 패시지의 정보를 연결하려면 비용이 높은 반복적 검색(IRCoT 등)이 필요하다. |
| **Motivation** | 포유류 뇌의 해마 기억 인덱싱 이론(hippocampal indexing theory)에 따르면, 신피질이 실제 기억을 저장하고 해마가 기억 간 연관 인덱스를 유지하여 빠른 연상 검색을 가능하게 한다. 이 메커니즘을 LLM의 장기 기억으로 모방하면 단일 검색 단계에서 멀티홉 추론이 가능. |
| **Limitation** | 저자 언급: KG 추출의 LLM 의존성, 엔티티 매칭의 정확도. 독자 관점: PPR 기반 탐색이 KG의 밀도와 연결성에 민감. 대규모 코퍼스에서의 KG 구축 비용 미분석. |

---

## Method

1. **오프라인 인덱싱 (신피질 + 해마 모방)**
   - **신피질 역할**: LLM이 각 패시지에서 엔티티와 관계를 추출하여 스키마리스(schemaless) 지식 그래프(KG) 구축
   - **해마 역할**: KG가 패시지 간 연관 인덱스 역할 수행. 엔티티 노드가 여러 패시지를 연결하는 허브로 기능

2. **온라인 검색 (PPR 기반 연상 검색)**
   - 쿼리에서 핵심 개념(seed nodes) 식별
   - Personalized PageRank(PPR) 알고리즘으로 seed에서 KG를 탐색, 관련 서브그래프 발견
   - PPR이 멀티홉 경로를 따라 확산하여, **단일 검색 단계에서 멀티홉 추론** 수행
   - 발견된 서브그래프에 연결된 패시지를 검색하여 LLM에 제공

3. **IRCoT와의 결합**: HippoRAG를 IRCoT의 검색 백엔드로 사용하면 추가 향상 가능

---

## Key Contribution

1. **해마 인덱싱 이론의 RAG 적용**: 뇌과학 영감의 KG + PPR 설계로 단일 단계 멀티홉 검색을 실현
2. **비용 효율**: IRCoT 대비 10~20배 저렴, 6~13배 빠르면서 동등 이상의 성능
3. **경로 탐색형 멀티홉 QA 해결**: 기존 방법으로 불가능했던 path-finding 유형의 질문에 대응

---

## Experiment & Results

- **벤치마크**: MuSiQue, 2WikiMultiHopQA, HotpotQA
- **Baseline**: NaiveRAG, ColBERTv2, IRCoT, RAPTOR

**주요 결과**:
- MuSiQue: HippoRAG가 기존 SOTA 대비 최대 +20% 향상
- 2WikiMultiHopQA: 기존 방법 대비 ~3% 향상
- IRCoT 대비: 10~20x 저렴, 6~13x 빠름에도 동등 성능
- HippoRAG + IRCoT: MuSiQue +4%, 2Wiki +20% 추가 향상
- HotpotQA (덜 어려운 데이터셋)에서도 IRCoT 결합 시 개선 확인

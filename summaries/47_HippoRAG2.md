# HippoRAG 2: Towards Efficient and Robust Long-Term Memory for LLM Agents

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su (Ohio State University)
> **arXiv**: 2502.14802 (2025.02)
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | HippoRAG 1.0은 오프라인 인덱싱에서 LLM을 사용하여 비용이 높고, KG의 엔티티 매칭 정확도에 취약점이 있었다. GraphRAG, LightRAG 등 후속 연구가 등장했지만 비용·지연·정확도 트레이드오프가 여전히 존재. |
| **Motivation** | LLM 에이전트의 장기 기억 시스템은 비용 효율적이면서도 연상 기억(associative memory) 능력을 유지해야 한다. 패시지 수준의 더 깊은 통합과 온라인 LLM 활용으로 HippoRAG의 한계를 극복 가능. |
| **Limitation** | 저자 언급: 복잡한 추론 체인에서 PPR 탐색의 깊이 한계. 독자 관점: 온라인 LLM 사용이 검색 지연을 증가시킬 수 있음. 대규모 벤치마크에서의 검증 범위 확대 필요. |

---

## Method

1. **개선된 오프라인 인덱싱**: 패시지 수준의 더 깊은 통합으로 엔티티 간 연결 강화. 엔티티 매칭 정확도 향상
2. **온라인 LLM 활용**: 검색 시점에 LLM을 활용하여 쿼리 이해 및 검색 결과 정제
3. **비용·지연 최적화**: GraphRAG/LightRAG 대비 인덱싱 비용 절감, 검색 지연 최소화

---

## Key Contribution

1. **HippoRAG의 실용적 확장**: 비용 효율성과 연상 기억 정확도를 동시에 개선
2. **연상 기억 태스크에서 SOTA**: GraphRAG, LightRAG 대비 +7% 향상하면서 비용·지연 효율적

---

## Experiment & Results

- **벤치마크**: 멀티홉 QA, 연상 기억 태스크
- **비교**: GraphRAG, LightRAG, HippoRAG 1.0

**주요 결과**:
- 연상 기억 태스크에서 기존 SOTA 대비 +7% 향상
- GraphRAG, LightRAG 대비 비용·지연 모두 효율적
- HippoRAG 1.0 대비 패시지 통합 깊이와 엔티티 매칭 정확도 개선

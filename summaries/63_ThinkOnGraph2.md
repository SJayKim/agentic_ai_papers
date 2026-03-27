# Think-on-Graph 2.0: Deep and Faithful LLM Reasoning with KG-guided RAG

> **논문 정보**: Shengjie Ma, Chengjin Xu, Xuhui Jiang, Muzhi Li, Huaren Qu, Cehao Yang, Jiaxin Mao, Jian Guo (IDEA Research, RUC, CUHK, HKUST)
> **arXiv**: 2407.10805 (2024.07)
> **학회**: ICLR 2025
> **코드**: https://github.com/IDEA-FinAI/ToG-2

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 text-based RAG는 문서 간 구조적 관계를 포착하지 못하고, KG-based RAG는 불완전성과 세부 컨텍스트 부재로 다단계 추론에 실패한다. 두 소스를 단순 병합하는 loose-coupling도 한 소스가 다른 소스를 개선하지 못한다. |
| **Motivation** | KG 탐색과 문서 검색을 긴밀하게 교대(tight-coupling) 수행하면, KG가 문서 검색 방향을 안내하고 문서가 엔티티 선택을 정교화하는 상호보완적 시너지가 달성된다. |
| **Limitation** | KG와 문서 간 정보 불일치 시 해결 전략 부재. KG 구축 비용과 entity linking 품질에 의존적. 교대 빈도/시점의 자동 조정 메커니즘 부재. EM 기반 평가에서 false negative 다수. |

---

## Method

### 1. Initialization
질문에서 엔티티 추출 → KG 연결(entity linking) → LLM이 Topic Prune으로 초기 topic entity 집합 선정 → DRM으로 상위 k개 문서 청크 추출

### 2. Hybrid Knowledge Exploration (반복)

**Context-enhanced Graph Search:**
- Relation Discovery: KG에서 topic entity의 모든 관계 탐색
- Relation Prune: LLM이 질문 관련성 기반으로 가지치기
- Entity Discovery: 선택된 관계를 통해 candidate entity 발견

**Knowledge-guided Context Retrieval:**
- 각 candidate entity의 문서 풀에서 DRM이 triple path를 쿼리로 활용하여 정밀 검색
- Context-based Entity Prune: 지수 감쇠 가중합으로 candidate entity 순위 산출, 상위 W개를 다음 반복의 topic entity로 선정 — KG 탐색 방향을 역으로 정제

### 3. Reasoning with Hybrid Knowledge
반복 종료 시 triple paths + top-K entity context + 이전 Clues를 함께 제공하여 답변 여부 판단. 불충분하면 Clues 생성 후 다음 반복.

하이퍼파라미터: Width W=3, Depth D=3, Context K=10

---

## Key Contribution

1. **KG×Text Tight-coupling RAG**: 각 단계에서 서로를 정교화하는 최초의 긴밀한 통합 프레임워크
2. **Context-enhanced Graph Search**: 문서 기반 entity pruning이 KG 탐색 방향을 역으로 정제
3. **Training-free, Plug-and-play**: GPT-3.5, GPT-4o, Llama-3-8B, Qwen2-7B 등에 즉시 적용
4. **7개 중 6개 SOTA**: 학습 없이 다양한 벤치마크에서 기존 방법 능가

---

## Experiment & Results

- **데이터셋**: WebQSP, AdvHotpotQA, QALD-10-en, Zero-Shot RE, FEVER, Creak + ToG-FinQA

**GPT-3.5 기준**:
- WebQSP: ToG-2 **81.1%** vs ToG 76.2% (+4.9%p)
- AdvHotpotQA: ToG-2 **42.9%** vs ToG 26.3% (**+16.6%p**)
- Zero-Shot RE: ToG-2 **91.0%** vs ToG 88.0%

**도메인 특화 (ToG-FinQA)**: ToG-2 **34.0%** vs ToG 14.0% vs GraphRAG 6.2%

**LLM별 효과 (AdvHotpotQA)**: Llama-3-8B +66.8%, Qwen2-7B +72.1%, GPT-3.5 +85.7%

**엔티티 pruning 런타임**: ToG 대비 평균 **68.7%** 수준으로 처리 (DRM 사용 덕분)

# MemoryAgentBench: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

> **논문 정보**: Yuanzhe Hu, Yu Wang, Julian McAuley (University of California, San Diego)
> **arXiv**: ICLR 2026 (2026.03)
> **코드**: https://github.com/HUST-AI-HYZ/MemoryAgentBench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 에이전트 벤치마크는 추론·계획·실행 능력에 집중하며, 메모리(기억·업데이트·검색)라는 핵심 역량을 체계적으로 평가하지 못한다. 기존 장문맥 벤치마크(NovelQA, ∞-Bench 등)는 전체 문맥을 한 번에 제공하여, 점진적으로 정보를 축적하는 메모리 에이전트의 특성을 반영하지 못한다. |
| **Motivation** | 메모리 과학·인지 과학 이론에 기반하여, 메모리 에이전트의 4대 핵심 역량을 정의: (1) Accurate Retrieval, (2) Test-Time Learning, (3) Long-Range Understanding, (4) Selective Forgetting. 기존 벤치마크 중 이 4개를 모두 커버하는 것은 없다. 또한 LoCoMo(~9K토큰), LongMemEval(합성 대화) 등은 규모·다양성·현실성이 부족하다. |
| **Limitation** | (1) EventQA와 FactConsolidation은 자동 생성 파이프라인에 의존하여 질문 품질의 체계적 검증이 제한적이다. (2) 전체 질문 수가 2,071개로, 대규모 벤치마크 대비 비교적 소규모다. (3) 멀티모달 메모리나 코드 기반 메모리는 평가 범위에 포함되지 않는다. (4) Selective Forgetting 평가가 반사실적(counterfactual) 편집에 의존하여, 실제 메모리 업데이트 시나리오와 다를 수 있다. |

---

## Method

MemoryAgentBench는 인지 과학 기반 4대 메모리 역량을 포괄적으로 평가하는 벤치마크로, 기존 장문맥 데이터셋을 멀티턴 형식으로 재구성하고 2개의 신규 데이터셋을 도입한다.

1. **4대 핵심 역량 정의**
   - **Accurate Retrieval (AR)**: 쿼리에 대해 정확한 정보 조각을 검색하는 능력 (단일홉/멀티홉)
   - **Test-Time Learning (TTL)**: 추가 학습 없이 배포 중 새로운 행동·기술을 습득하는 능력
   - **Long-Range Understanding (LRU)**: 100K+ 토큰에 걸친 분산 정보를 통합하여 전체적 이해에 기반한 질문에 답하는 능력
   - **Selective Forgetting (SF)**: 모순되는 증거 앞에서 이전 저장 정보를 수정·덮어쓰기·제거하는 능력

2. **데이터셋 구성 (총 2,071 질문, 103K~1.44M 토큰)**
   - **AR**: SH-Doc QA (197K), MH-Doc QA (421K), LongMemEval-S* (355K, 5개 대화+300질문으로 재구성), **EventQA** (신규, 534K, 소설 기반 사건 순서 다지선다)
   - **TTL**: BANKING77, CLINC150, NLU, TREC Coarse/Fine (103K, 분류 태스크), Recommendation (영화 추천)
   - **LRU**: ∞-Bench Summarization (소설 요약), Detective QA (71질문, 추리소설 추론)
   - **SF**: **FactConsolidation** (신규, MQUAKE 기반 반사실적 편집, 6K~262K)

3. **평가 프레임워크**
   - 모든 데이터셋을 청크로 분할하여 멀티턴 대화 형식으로 순차 주입
   - 각 청크에 "이 내용을 기억하세요" 지시 포함 → 에이전트의 메모리 메커니즘 트리거
   - 3종 에이전트 평가: Long-Context Agents, RAG Agents (Simple/Embedding/Structure-Augmented), Agentic Memory Agents

4. **평가 대상 에이전트**
   - Long-Context: GPT-4o, GPT-4o-mini, GPT-4.1-mini, Gemini-2.0-Flash, Claude-3.7-Sonnet
   - RAG: BM25, Contriever, Text-Embed-3, Qwen3-Embedding, RAPTOR, GraphRAG, MemoRAG, HippoRAG-v2, Mem0, Cognee, Zep
   - Agentic Memory: Self-RAG, MemGPT, MIRIX

---

## Key Contribution

1. **4대 메모리 역량 프레임워크**: 인지 과학에 기반한 체계적 메모리 평가 틀(AR, TTL, LRU, SF)을 최초로 제안. 기존 벤치마크의 부분적 커버리지 한계를 해결.
2. **멀티턴 점진적 평가**: 장문맥 데이터셋을 멀티턴 형식으로 재구성하여 메모리 에이전트의 점진적 정보 축적을 실제적으로 평가.
3. **2개 신규 데이터셋**: EventQA(사건 순서 추론)와 FactConsolidation(선택적 망각)으로 기존 벤치마크가 커버하지 못한 역량 평가.
4. **포괄적 에이전트 비교**: 상용 메모리 에이전트, 장문맥 모델, RAG 시스템을 동일 프로토콜로 비교하는 최초의 통합 평가.

---

## Experiment & Results

**전체 성능 (Overall Score, GPT-4o-mini 백본)**:
- Claude-3.7-Sonnet: **49.6** (Long-Context 최고), GPT-4.1-mini: 46.9, GPT-4o: 48.8
- HippoRAG-v2: **41.6** (RAG 최고), BM25: 41.5
- MIRIX(4.1-mini): **37.7** (Agentic Memory 최고), MemGPT: 28.3

**Accurate Retrieval (AR)**:
- GPT-4.1-mini: **71.8** (Long-Context), HippoRAG-v2: **65.1** (RAG), MIRIX(4.1-mini): **63.0** (Agentic)
- Mem0: 32.6, Cognee: 28.3 — 상용 메모리 시스템들이 AR에서 의외로 부진

**Test-Time Learning (TTL)**:
- Claude-3.7-Sonnet: **53.9**, Long-Context 방식이 압도적 우위
- RAG/Agentic 방식은 TTL에서 취약 (검색으로 기술 습득이 어려움)

**Long-Range Understanding (LRU)**:
- Claude-3.7-Sonnet: **62.2**, GPT-4o: 54.9
- 대부분의 RAG/Agentic 에이전트가 30% 미만 — 전체적 이해를 요하는 태스크에서 검색 기반 한계 노출

**Selective Forgetting (SF)**:
- GPT-4o: FactCon-SH 60.0 (Long-Context 최고)
- HippoRAG-v2: **29.5** (RAG 최고), 대부분의 메모리 시스템이 10-15% — 선택적 망각이 가장 어려운 역량

**핵심 발견**: 어떤 단일 방법도 4대 역량을 모두 지배하지 못함. Long-Context는 TTL/LRU에 강하나 AR에서 RAG에 밀리고, RAG는 AR에 강하나 LRU/SF에서 취약. 모든 방법이 SF에서 가장 큰 어려움.

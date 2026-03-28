# MemoryAgentBench: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

> **논문 정보**: Yuanzhe Hu, Yu Wang, Julian McAuley (University of California, San Diego)
> **arXiv**: 2507.05257v3 (2025) | **학회**: ICLR 2026
> **코드**: 공개 예정 (MIT License, 데이터셋 CC BY 4.0)

---

## Problem

기존 LLM 에이전트 벤치마크(GAIA, SWE-Bench 등)는 추론, 계획, 실행 능력 평가에 집중하며, 에이전트의 메모리(기억 저장, 갱신, 검색) 능력은 체계적으로 평가되지 않고 있다. 초기 메모리 벤치마크인 LOCOMO(~9K 토큰), LooGLE(~24K 토큰), LongBench(~20K 토큰)는 맥락 길이가 짧아 현재 모델에게 더 이상 도전적이지 않다. NovelQA(~200K), NOCHA(~127K), Loong(~100K) 등 최신 장문맥 벤치마크는 정적 단일 입력 설정으로, 점진적으로 정보를 축적하는 메모리 에이전트의 특성을 반영하지 못한다. 메모리는 과거 정보의 압축된 표현으로, 원문 전체를 저장하는 장문맥 처리와 근본적으로 다르다. LongMemEval은 합성 대화를 활용하지만, 주제 다양성이 제한적이고 상호작용 패턴이 비현실적이다. 또한 기존 어떤 벤치마크도 정확한 검색(AR), 테스트 시점 학습(TTL), 장거리 이해(LRU), 선택적 망각(SF)의 네 가지 핵심 역량을 모두 평가하지 못한다.

---

## Motivation

인지과학 및 기억과학의 고전 이론(James 1890; McClelland et al. 1995; Anderson & Neely 1996)에 기반하여, 메모리 에이전트가 갖춰야 할 네 가지 상호보완적 역량을 정의한다. 메모리 에이전트는 정보를 점진적으로 흡수하고, 시간에 걸쳐 추상화 및 통합하며, 새로운 추론을 생성하고, 축적된 이력에서 규칙을 학습하도록 설계된다. 전체 맥락을 한 번에 제공하는 기존 데이터셋은 이러한 점진적 처리 특성을 평가할 수 없으므로, 다중 턴 상호작용 형식의 새로운 벤치마크가 필요하다. MemGPT, Mem0, Cognee, Zep, MIRIX 등 다양한 상용 메모리 에이전트가 등장했으나, 이들의 실효성은 일화적(anecdotal) 수준에 머물러 있다. 통일된 평가 프로토콜 하에서 장문맥 에이전트, RAG 에이전트, 에이전틱 메모리 에이전트를 포괄적으로 비교할 수 있는 체계적 테스트베드가 필요하다.

---

## Method

1. **네 가지 핵심 역량 정의**: (1) Accurate Retrieval(AR) — 쿼리에 대해 정확한 스니펫을 추출하는 능력, (2) Test-Time Learning(TTL) — 추가 학습 없이 배포 중 새로운 행동/스킬을 습득하는 능력, (3) Long-Range Understanding(LRU) — 100K+ 토큰에 걸쳐 분산된 정보를 통합하는 능력, (4) Selective Forgetting(SF) — 모순 증거에 직면하여 기존 정보를 수정/삭제하는 능력.

2. **AR 카테고리**: SH-Doc QA/MH-Doc QA(NIAH 스타일, 평균 197K/421K 토큰), LongMemEval(S*)(~355K 토큰), EventQA(신규, 소설 기반 시간적 사건 순서 QA, ~534K 토큰).

3. **TTL 카테고리**: Multi-Class Classification(BANKING77, CLINC150, NLU, TREC-Coarse, TREC-Fine), Movie Recommendation(~1.44M 토큰, Recall@5 평가).

4. **LRU 카테고리**: Novel Summarization(∞-Bench En.Sum, ~172K 토큰), Detective QA(10개 소설, 71개 질문, ~124K 토큰).

5. **SF 카테고리**: FactConsolidation(신규) — MQUAKE의 반사실적 편집 쌍 활용, 단일 홉(FC-SH)과 다중 홉(FC-MH).

6. **다중 턴 형식 변환**: 기존 장문맥 데이터셋을 여러 대화 청크로 분할하고, 시간 순서대로 점진적으로 에이전트에 입력. 각 청크에 기억 지시문을 부착.

7. **에이전트 범주**: Long-Context Agents(GPT-4o, GPT-4.1-mini, Gemini-2.0-Flash, Claude-3.7-Sonnet), RAG Agents(BM25, Contriever, RAPTOR, GraphRAG, HippoRAG-v2, Mem0, Cognee, Zep), Agentic Memory Agents(Self-RAG, MemGPT, MIRIX).

8. **평가 프로토콜**: 모든 에이전트가 청크를 순차적으로 흡수하고 메모리를 점진적으로 갱신한 후 질문에 응답. 총 2,071개 질문, 103K~1.44M 토큰 범위.

---

## Key Contribution

1. **네 가지 핵심 역량(AR, TTL, LRU, SF) 체계적 정의**: 인지과학 이론에 기반하여 메모리 에이전트의 역량을 최초로 형식화.
2. **다중 턴 점진적 입력 형식**: 기존 장문맥 데이터셋을 메모리 에이전트 평가에 적합한 형식으로 변환하는 방법론 제안.
3. **신규 데이터셋**: EventQA(시간적 사건 추론)와 FactConsolidation(선택적 망각) 구축.
4. **통합 비교 평가**: 장문맥/RAG/에이전틱 메모리 에이전트를 통일된 프로토콜 하에 비교한 최초의 체계적 실증 연구.
5. **기존 메모리 에이전트의 한계 규명**: 어떤 에이전트도 네 가지 역량 모두를 마스터하지 못한다는 결정적 증거를 제시.

---

## Experiment & Results

- **전체 규모**: 15개 데이터셋, 2,071개 질문, 20+ 에이전트 변형을 평가.
- **AR 최고 성능**: GPT-4.1-mini(장문맥)가 AR 평균 71.8%로 최고. HippoRAG-v2가 RAG 중 AR 평균 65.1%.
- **TTL 우위**: Claude-3.7-Sonnet(장문맥)이 MCC 평균 89.4%, TTL 평균 53.9%로 전체 최고. RAG 에이전트와 상용 메모리 에이전트는 부분 정보만 검색하여 학습 불가.
- **LRU 우위**: Claude-3.7-Sonnet이 LRU 평균 62.2% 달성. RAG 기반 최고인 HippoRAG-v2는 LRU 평균 36.2%에 그침.
- **SF 전반적 실패**: 모든 에이전트가 FactConsolidation-MH에서 극히 낮은 성능. GPT-4o가 FC-SH 60.0%, FC-MH 5.0%로 장문맥 모델 중 최고.
- **상용 에이전트 성능**: Mem0(전체 평균 21.1%), Cognee(20.6%), Zep(24.0%) 등 상용 구조 증강 RAG 에이전트가 단순 BM25(41.5%)보다도 낮은 성능.
- **MIRIX(GPT-4.1-mini)**: 에이전틱 메모리 중 최고(전체 37.7%).
- **전체 최고**: Claude-3.7-Sonnet이 전체 평균 49.6%로 1위. 어떤 에이전트도 50%를 넘기지 못함.
- **백본 모델 효과**: MIRIX에서 GPT-4o-mini → GPT-4.1-mini로 업그레이드 시 EventQA 29.8→53.0 (+23.2pp) 대폭 향상.
- **FactConsolidation 검증**: o4-mini가 6K 맥락에서 FC-SH 100.0%, FC-MH 80.0% 달성하나, 32K에서 FC-SH 61.0%, FC-MH 14.0%로 급락.

---

## Limitation

- 예산 제약으로 인해 일부 대표적인 메모리 에이전트만 평가하였으며, 더 많은 에이전트에 대한 평가 결과 확장이 향후 과제로 남아 있다.
- 파라메트릭 메모리 시스템(MemoryLLM, SELF-PARAM 등)은 학술 연구 단계에 머물러 있어 평가 대상에서 제외되었다.
- FactConsolidation 데이터셋은 MQUAKE의 반사실적 편집 쌍에 의존하여, 실제 세계의 자연스러운 정보 갱신 시나리오와 차이가 있을 수 있다.
- LRU 평가가 소설 요약과 탐정 QA 두 과제에 한정되어, 다양한 도메인의 장거리 이해를 포괄하지 못한다.
- 모든 데이터셋이 영어 텍스트 기반이며, 다국어 메모리 에이전트 평가는 다루지 않는다.
- 선택적 망각(SF)에서 모든 에이전트가 극도로 낮은 성능을 보이나, 이를 해결하기 위한 구체적 방법론은 제안하지 않았다.

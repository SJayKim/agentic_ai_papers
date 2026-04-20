# MemoryAgentBench: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

> **논문 정보**: Yuanzhe Hu, Yu Wang, Julian McAuley (University of California, San Diego)
> **arXiv**: 2507.05257v3 (2025) | **학회**: ICLR 2026
> **코드**: 공개 예정 (MIT License, 데이터셋 CC BY 4.0)

---

## Problem

기존 LLM 에이전트 벤치마크(GAIA, SWE-Bench 등)는 추론, 계획, 실행(코드 합성, 도구 사용) 능력 평가에 거의 전적으로 집중한다.
그러나 에이전트의 또 다른 핵심 요소인 메모리 — 즉 정보를 저장(store), 갱신(update), 검색(retrieve), 추상화(abstract)하는 능력 — 는 체계적 벤치마크 부재로 인해 제대로 평가되지 않고 있다.
초기 메모리 벤치마크인 LOCOMO(~9K 토큰), LooGLE(~24K 토큰), LongBench(~20K 토큰)는 맥락 길이가 짧아 현재 장문맥 모델에게 더 이상 도전적이지 않다.
NovelQA(~200K), NOCHA(~127K), Loong(~100K), ∞-Bench(~150K) 등 최신 장문맥 벤치마크는 정적 단일 입력 설정으로, 점진적으로 정보를 축적·통합하는 메모리 에이전트의 핵심 특성을 반영하지 못한다.
메모리는 과거 정보의 압축·증류된 표현(compressed and distilled representation)으로, 원문 전체를 축어적(verbatim)으로 저장하는 장문맥 처리와는 근본적으로 구분된다.
LongMemEval은 합성 대화를 세션 단위로 주입하는 방식을 도입했지만, 주제 다양성이 제한적이고 상호작용 패턴이 비현실적이어서 실세계 메모리 에이전트 시나리오에 대한 적용성이 떨어진다.
또한 기존의 어떤 벤치마크도 정확한 검색(AR), 테스트 시점 학습(TTL), 장거리 이해(LRU), 선택적 망각(SF)의 네 가지 핵심 역량을 모두 포괄하지 못한다.
결과적으로 MemGPT, Mem0, Cognee, Zep, MIRIX 등 상용 메모리 에이전트의 실효성은 일화적(anecdotal) 수준에 머물러, 통일된 평가 프로토콜이 부재한 상태다.

---

## Motivation

인지과학 및 기억과학의 고전 이론(James 1890; McClelland et al. 1995; Anderson & Neely 1996; Wimber et al. 2015)에 기반하면, 메모리 에이전트는 정보를 점진적으로 흡수(absorb piece by piece)하고, 시간에 걸쳐 추상화·통합(abstract and consolidate)하며, 새로운 추론을 생성하고, 축적된 이력에서 규칙을 학습해야 한다.
이러한 점진적 처리 특성은 전체 맥락을 한 번에 제공하는 기존 장문맥 데이터셋으로는 평가할 수 없으므로, 다중 턴(multi-turn) 형식의 새로운 벤치마크가 요구된다.
상용 솔루션으로 MemoryLLM, SELF-PARAM, M+ 등 파라메트릭 메모리 시스템과 MemGPT, Mem0, Cognee, Zep, MIRIX 등 토큰 레벨 메모리 시스템이 쏟아지고 있으나, 이들을 공정하게 비교할 기반이 없다.
메모리는 파라미터, 벡터, 텍스트 이력, 외부 데이터베이스 등 다양한 형태를 가지지만, 실세계에 배포되는 주요 형태는 텍스트 이력과 외부 DB 기반이므로 이를 공통 평가 대상으로 삼는다.
저자들은 RAG 방식이 top-k 검색의 한계로 인해 모호한 쿼리, 다중 홉 추론, 장거리 이해에 취약함을 관찰하고, 에이전틱 루프를 통한 반복적 검색·반성이 이를 얼마나 완화하는지 실증하고자 한다.
장문맥 에이전트, RAG 에이전트, 에이전틱 메모리 에이전트의 세 범주를 통일된 프로토콜 하에서 비교함으로써, 각 패러다임의 강점·약점과 향후 연구 방향을 규명하는 것이 본 연구의 동기다.

---

## Method

1. **네 가지 핵심 역량 정의**: (1) Accurate Retrieval(AR) — 쿼리에 대응하는 정확한 스니펫을 단일 쿼리로 추출(1-hop/multi-hop 포함), (2) Test-Time Learning(TTL) — 추가 훈련 없이 배포 중 새로운 행동·스킬을 습득, (3) Long-Range Understanding(LRU) — 100K+ 토큰에 분산된 정보를 통합하여 전체 시퀀스를 전역적으로 이해, (4) Selective Forgetting(SF) — 모순되는 증거 등장 시 기존 정보를 수정·덮어쓰기·삭제(모델 편집 및 언러닝과 연계).

2. **AR 데이터셋 구성**: SH-Doc QA(NIAH 스타일 단일 홉, ~197K 토큰)와 MH-Doc QA(다중 홉, ~421K 토큰), LongMemEval(S*)(5개 긴 대화에 300개 질문 매핑, ~355K 토큰), 그리고 신규 EventQA(소설 기반, 이전 5개 사건 후 다음 사건을 후보에서 선택, ~534K 토큰).

3. **EventQA 자동화 파이프라인**: 기존 장거리 내러티브 데이터셋들이 수작업 주석에 의존하는 것과 달리, 소설에서 사건 시퀀스를 자동 추출하여 시간 추론용 다중 선택 QA를 대규모로 생성하는 파이프라인을 구축.

4. **TTL 데이터셋 구성**: Multi-Class Classification은 BANKING77(77라벨), CLINC150(151라벨), NLU(68라벨), TREC-Coarse(6라벨), TREC-Fine(50라벨) 다섯 개를 재구성하여 ~103K 토큰 규모로 평가; Movie Recommendation은 수천 턴의 영화 대화 이력에서 20편을 추천(Recall@5, ~1.44M 토큰).

5. **LRU 데이터셋 구성**: ∞-Bench의 En.Sum 소설 요약(엔티티 치환, 1000~1200단어 요약 생성, ~172K 토큰)과 Detective QA(10개 탐정 소설, 71개 질문, ~124K 토큰)로 장거리 추론을 측정.

6. **SF 데이터셋 FactConsolidation 구축**: MQUAKE의 반사실적 편집 쌍을 활용하여, 원래 사실 뒤에 그와 모순되는 새 사실을 배치한 업데이트 시나리오를 시뮬레이션. 단일 홉(FC-SH)은 직접 사실 회상, 다중 홉(FC-MH)은 여러 사실에 대한 연쇄 추론을 요구. 맥락 길이를 6K, 32K, 64K, 262K로 확장하며 가드레일 프롬프트("newer facts have larger serial numbers")로 최신 정보 우선을 명시.

7. **다중 턴 형식 변환**: 기존 장문맥 데이터셋을 chunks(c₁,...,cₙ) → questions(q₁,...,qₘ) → answers(a₁,...,aₘ)의 표준 형식으로 재구성. 각 청크에 "Please memorize it and I will ask some questions..." 형태의 메모리 지시문을 부착하여 User-Assistant 대화로 래핑.

8. **청크 크기 정책**: 장문맥 합성 텍스트(MH-Doc QA, LME(S*), SF 전체)는 데이터셋별 기본 청크 설정을 따르되, 나머지 모든 과제는 청크 크기 4096으로 통일(Mem0/Cognee/Zep/MIRIX 포함).

9. **Long-Context Agents 평가 대상**: GPT-4o, GPT-4o-mini, GPT-4.1-mini, Gemini-2.0-Flash, Claude-3.7-Sonnet.

10. **RAG Agents 평가 대상**: Simple(BM25), Embedding(Contriever, Text-Embedding-3-Small/Large, Qwen3-Embedding-4B), Structure-Augmented(RAPTOR, GraphRAG, MemoRAG, HippoRAG-v2, Mem0, Cognee, Zep).

11. **Agentic Memory Agents 평가 대상**: Self-RAG, MemGPT, MIRIX(GPT-4o-mini 및 GPT-4.1-mini 백본).

12. **상호작용 프로토콜**: 모든 에이전트가 청크를 순차적으로 흡수하여 메모리를 점진적으로 갱신한 뒤 관련 질문에 응답. 전 에이전트에 표준화된 프롬프트 템플릿을 적용하여 공정 비교 보장.

13. **평가 지표**: AR은 Accuracy, Movie Recommendation은 Recall@5, ∞-Bench-Sum은 F1-Score, 나머지는 Accuracy. 총 15개 데이터셋, 2,071개 질문, 맥락 깊이 103K~1.44M 토큰 범위.

14. **Ablation 설계**: 청크 크기(512/1024/2048/4096), 검색 top-k(2/5/10), 백본 모델(GPT-4o-mini/GPT-4.1-mini/Gemini-2.0-Flash) 세 축으로 민감도 분석.

---

## Key Contribution

1. **네 가지 핵심 역량(AR, TTL, LRU, SF)의 체계적 형식화**: 인지과학·기억과학 이론에 기반하여 메모리 에이전트의 필수 역량을 최초로 개념화.
2. **다중 턴 점진적 입력 프레임워크**: 기존 장문맥 데이터셋을 메모리 에이전트 평가에 적합한 대화 청크 형식으로 재구성하는 일관된 방법론 제시.
3. **신규 데이터셋 EventQA와 FactConsolidation**: 시간적 사건 추론(자동화 파이프라인)과 선택적 망각(MQUAKE 편집 쌍 기반)을 각각 평가하는 신규 리소스 구축.
4. **통합 비교 평가 최초 수행**: Long-Context / RAG / Agentic Memory 세 범주(20+ 에이전트 변형)를 통일된 프로토콜로 비교한 가장 포괄적 실증 연구.
5. **기존 메모리 에이전트 한계 규명**: 어떤 에이전트도 네 역량 모두를 동시에 마스터하지 못한다는 결정적 증거와 원인 분석 제공.
6. **공개 재현성 보장**: 코드 MIT, 데이터 CC BY 4.0, Dockerfile·conda/requirements·프롬프트·재생성 스크립트 전체 공개 예정.

---

## Experiment

- **전체 규모**: 15개 데이터셋, 2,071개 질문, 20+ 에이전트 변형 평가; 맥락 깊이 103K~1.44M 토큰.
- **AR 최고 성능(장문맥)**: GPT-4.1-mini가 AR 평균 71.8%(SH-QA 83.0, MH-QA 66.0, LME(S*) 55.7, EventQA 82.6)로 전체 최고.
- **AR 최고 성능(RAG)**: HippoRAG-v2가 RAG 중 AR 평균 65.1%(SH-QA 76.0, MH-QA 66.0)로 BM25(60.5%)를 능가. 대부분의 RAG가 GPT-4o-mini 백본(49.2%)을 상회.
- **TTL 우위(장문맥)**: Claude-3.7-Sonnet이 MCC 89.4%, TTL 평균 53.9%로 전체 최고. 모든 RAG/상용 메모리 에이전트는 부분 정보만 검색하여 전역 학습 불가.
- **LRU 우위(장문맥)**: Claude-3.7-Sonnet이 Summ. 52.5, Det QA 71.8, LRU 평균 62.2% 달성. RAG 최고인 HippoRAG-v2는 36.2%에 그침.
- **SF 전반적 실패**: 모든 에이전트가 FC-MH에서 극히 낮은 성능. GPT-4o가 FC-SH 60.0, FC-MH 5.0으로 장문맥 모델 중 최고. HippoRAG-v2가 SF에서 FC-SH 54.0, FC-MH 5.0.
- **상용 구조 증강 RAG의 부진**: Mem0 전체 21.1%, Cognee 20.6%, Zep 24.0%로 단순 BM25(41.5%)보다 낮아, 복잡한 구조 증강이 모든 경우에 유효하지 않음을 시사.
- **에이전틱 메모리 성능**: Self-RAG 18.7%, MemGPT 28.3%, MIRIX(GPT-4o-mini) 26.2%로 전반적으로 낮음. MIRIX(GPT-4.1-mini) 업그레이드 시 37.7%로 상승.
- **전체 최고**: Claude-3.7-Sonnet이 전체 평균 49.6%로 1위이나, 어떤 에이전트도 50%를 넘기지 못함.
- **백본 효과(MIRIX)**: GPT-4o-mini → GPT-4.1-mini로 업그레이드 시 EventQA 29.8→53.0(+23.2pp), ∞Bench-Sum 9.9→18.9(+9.0pp), 전체 평균 15.9→25.6(+9.7pp) 대폭 향상 — 에이전틱 메모리는 백본에 강하게 의존.
- **백본 효과(RAG)**: BM25는 GPT-4o-mini → GPT-4.1-mini로 38.8→40.2(+1.4pp) 그침 — RAG는 이미 백본 병목에서 벗어나 있음.
- **FactConsolidation 난이도 검증**: o4-mini가 6K 맥락에서 FC-SH 100.0, FC-MH 80.0을 달성하지만, 32K에서 FC-SH 61.0, FC-MH 14.0으로 급락. GPT-4o도 6K→32K에서 FC-MH 28.0→10.0으로 하락하여 장거리 추론 한계가 본질적.
- **청크 크기 Ablation**: AR 과제에서는 작은 청크 + 많은 검색 호출이 성능 향상에 유리(임베딩 기반에 특히 유효). LRU 과제는 청크 분할 시 오히려 성능 하락 — RAG가 응집된 장거리 맥락 통합에 본질적으로 부적합.
- **Top-k Ablation**: top-k를 2→5→10으로 키우면 대부분 과제에서 성능 향상. 다만 청크 4096 × top-10 = ~40K 토큰 주입이라 top-20은 API 비용상 미실시.

---

## Limitation

- 예산 제약으로 인해 대표적인 메모리 에이전트만 평가하였으며, 더 많은 에이전트·백본 조합으로의 확장은 향후 과제로 남아 있다.
- 파라메트릭 메모리 시스템(MemoryLLM, SELF-PARAM, M+ 등)은 아직 학술 연구 단계이고 상용 API 모델 대비 성능이 낮아 평가 대상에서 제외되어, 이 범주에 대한 결론은 유보된다.
- FactConsolidation 데이터셋은 MQUAKE의 반사실적 편집 쌍에 의존하여 실제 세계의 자연스러운 지식 업데이트 시나리오(부분적 수정, 조건부 진실 등)와 차이가 존재할 수 있다.
- LRU 평가가 소설 요약(∞-Bench En.Sum)과 탐정 QA 두 과제에 한정되어, 과학 논문·법률 문서·코드베이스 등 다양한 도메인의 장거리 이해는 포괄하지 못한다.
- 모든 데이터셋이 영어 텍스트 기반이며, 다국어 메모리 에이전트 및 교차 언어 메모리 유지 능력은 다루지 않는다.
- 선택적 망각(SF)에서 거의 모든 에이전트가 극단적으로 낮은 성능을 보이지만, 이를 해결할 구체적 알고리즘이나 설계 가이드라인은 제안하지 않아 처방적(prescriptive) 기여가 부족하다.
- 평가 프로토콜이 User-Assistant 대화로 래핑된 단일 대화 세션을 가정하여, 멀티 세션 간 장기 지속성이나 사용자 선호 누적 같은 실세계 시나리오는 완전히 반영되지 않는다.

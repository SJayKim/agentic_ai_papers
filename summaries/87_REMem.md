# 87. REMem: Reasoning with Episodic Memory in Language Agents

> 📄 **저자**: Yiheng Shu, Saisri Padmaja Jonnalagedda, Xiang Gao, Bernal Jiménez Gutiérrez, Weijian Qi, Kamalika Das, Huan Sun, Yu Su (The Ohio State University, Intuit AI Research)
> 📚 **학회/발표 기관**: ICLR 2026
> 📅 **발표 날짜**: 2026.02
> 🔗 **arXiv**: https://arxiv.org/abs/2602.13530
> 💻 **코드**: https://github.com/intuit-ai-research/REMem

---

## Problem

언어 에이전트의 메모리는 대부분 의미 기억(semantic memory)에 머물러 있어, 과거 상호작용 이력을 정확히 회상(recollection)하고 그 위에서 추론(reasoning)하는 능력이 결여되어 있다.
파라메트릭 메모리(모델 가중치)는 적응성이 없고 특정 경험에 대한 맥락적 근거(contextual grounding)가 부족하며, 모델 편집(model editing) 기법은 정적인 의미 지식 수정에 국한된다.
임베딩 기반 RAG는 동적 지식 접근은 가능하나 시공간 맥락(spatiotemporal context)에서 분리된 채(de-contextualized) 작동한다.
LLM으로 요약·의미 그래프를 구성하는 비파라메트릭 시스템(HippoRAG, GraphRAG)도 구조화된 세계 지식을 우선시할 뿐 개인의 경험 특화 정보를 다루지 못한다.
에피소드 설정을 직접 겨냥한 최근 연구들(Graphiti/Zep, Mem0)조차 (시간적) 지식 그래프의 엔티티 관계로만 표현하여 일관된 이벤트 맥락을 잃거나, 중요해 보이는 것만 선별 요약하여 명시적 이벤트 모델링(explicit event modeling)이 빠져 있다.
결정적으로 기존 방법들은 시간·장소·참여자 같은 상황 차원(situational dimensions)을 이벤트에 결합하지 못하며, 여러 이벤트를 연결하는 추론이 필요할 때 유사도 기반 단발성 검색에 과도하게 의존해 복잡한 이벤트 간 관계 추론에 실패한다.

---

## Motivation

핵심 직관은 인간 지능의 특징인 "정신적 시간여행(mental time travel)" 능력, 즉 에피소드 기억에서 출발한다.
인간은 과거 사건을 시공간 축을 따라 그 순서·지속시간·인과성과 함께 정밀하게 재경험하는데, 이는 개념·세계 지식만 저장하는 의미 기억과 본질적으로 다르다.
인지과학에 따르면 인간은 의사결정 시 축어적(verbatim) 기억보다 핵심 요지(gist)에 더 의존하며, 담화 기억은 시간·공간·인과·상황 차원을 통합하는 상황 모델(situation model)을 중심으로 형성된다.
또한 최근 RAG 연구는 개념 수준(concept-level)과 맥락 수준(context-level) 정보를 결합한 하이브리드 메모리 구조가 어느 한쪽만 쓰는 것보다 효과적임을 보였다.
이로부터 저자들은 (1) 이벤트를 시간 인식형(time-aware) 요지와 사실로 명시적으로 표현하고, (2) 단발성 매칭 대신 유연한 검색과 반복 추론을 결합하는 포괄적 이벤트 표현이 에피소드 기억의 두 진행적 과제—에피소드 회상과 에피소드 추론—를 동시에 풀 수 있다고 본다.

---

## Method

REMem은 **인덱싱(indexing)**과 **에이전틱 추론(agentic inference)** 두 단계로 동작한다.

**[인덱싱 단계 — 하이브리드 메모리 그래프 구축]**
1. **Gist 추출**: 각 이벤트 진술/대화 세션마다 LLM이 하나 이상의 자연어 gist 문장을 생성한다.
각 gist는 해당 에피소드의 기준 시각(reference time)을 접두로 붙이고, 상대적 시간 표현("지난 일요일")을 절대 날짜("14 Jan 2024")로 해소(resolve)한다.
하나의 gist는 참여자·행동·대상·장소·의도·수량을 담은 단일 원자적 이벤트 요약이다.
2. **Fact 추출**: 원문과 추출된 gist 리스트에서 (주어, 술어, 목적어) 형태의 스키마리스(schemaless) 트리플을 추출한다.
여기에 Wikidata식 시간 한정자(point in time / start time / end time)를 선택적으로 부착해 각 사실을 타임라인에 고정(ground)한다.
모순되는 gist·fact도 삭제하지 않고 시간순으로 보존하여 역사적 재방문이 가능한 기록을 유지한다.
3. **그래프 구성**: gist 노드(맥락 수준)와 phrase 노드(개념 수준)를 통합한 타입 멀티그래프 M=(V,E)를 만든다.
엣지는 세 종류다 — relation edge(사실 트리플의 주어-목적어 phrase를 술어·유효구간과 함께 연결), context edge(같은 청크에서 나온 gist를 그 phrase들에 바인딩), synonymy edge(임베딩 유사도가 임계값 0.8을 넘는 gist 노드끼리 연결, HippoRAG 2 방식으로 의미적으로 유사한 에피소드를 군집화).
마지막으로 gist·phrase 표면형에 대한 임베딩 인덱스와 BM25 어휘 인덱스를 구축한다.

**[에이전틱 추론 단계 — ReAct 스타일 반복 검색]**
ReAct 형태의 에이전트가 5종의 엄선된 도구를 호출하며 그래프를 탐색한다. 모든 검색/탐색 도구는 gist 리스트와 fact 리스트를 함께 반환해 포괄적 시야를 제공한다.
4. **검색(Retrieval) 단계**: `semantic_retrieve`(임베딩) 또는 `lexical_retrieve`(BM25)로 시드 노드·시간 윈도·주제 단서를 얻는다.
두 도구 모두 query에 더해 start_time, end_time, start_operator, end_operator 인자를 받아 시간 조건 필터링이 가능하다.
에이전트는 복잡 질문을 하위 질의로 분해한다.
5. **그래프 탐색(Graph Exploration) 단계**: 시드 노드를 기반으로 `find_gist_contexts`(에피소드 수준 서사·시간 근거 확보)나 `find_entity_contexts`(주어/술어/목적어 지정 + 시간 조건 + limit/ordering/offset/aggregation으로 서수·집계 질의 처리)를 호출한다.
이로써 시간 범위 필터링, 이웃 탐색, 서수 제약 등 논리적 합성(logical composition)이 가능해진다.
6. **흐름 제어(Flow Control) 단계**: 충분한 증거가 모이면 `output_answer`를 호출하여 누적된 gist·fact 증거(E)와 상호작용 이력(H)을 종합해 최종 답을 생성한다.
이 "정신적 시간여행" 루프는 데이터셋별로 최대 2~5 스텝(회상 3, 추론 5)으로 제한된다.

---

## Key Contribution

1. 에피소드 기억의 두 핵심 과제를 **에피소드 회상**(이벤트와 시간·장소·참여자·감정 등 상황 차원의 결합 재구성)과 **에피소드 추론**(회상 위에서 이벤트 간 관계·서수·최상급의 다단계 추론)으로 형식화하여, 기존 연구가 간과한 에피소드성(episodicity)을 명확히 정의했다.
2. **하이브리드 메모리 그래프**를 제안하여, 시간 파싱된 gist(맥락 수준)와 시간 스코프 트리플(개념 수준)을 동시에 인코딩한다. 이는 엔티티 관계만 저장하는 Graphiti의 맥락 손실과, 선별 요약으로 명시적 이벤트 모델링이 없는 Mem0의 한계를 동시에 해결한다.
3. **선별 추출이 아닌 명시적 지시(instruct)** 방식으로 LLM에게 시간 중심으로 메모리를 조직하고 상황 차원에 연결하도록 강제하여, 기존의 "중요해 보이는 것만 남기는" 정보 손실 문제를 푼다.
4. 시간 인식 도구를 갖춘 **에이전틱 추론 절차**로 단발성 텍스트 매칭을 넘어 시간 범위 필터링·이웃 탐색·서수 제약 같은 복잡한 논리 합성을 가능케 하여, 유사도 검색만으로는 불가능한 이벤트 간 추론을 지원한다.
5. 4개 벤치마크에 걸친 현재까지 가장 포괄적인 평가와 함께, 답할 수 없는 질문에 대한 **강건한 거부(refusal) 행동**을 입증하여 환각을 완화했다.

---

## Experiment & Results

**데이터셋**: 에피소드 회상으로 LoCoMo(합성 대화, 질의 1,986개)와 REALTALK(실제 인간 대화, 728개), 에피소드 추론으로 Complex-TR(1,000개 샘플)과 Test of Time(의미 부분 2,800개)을 사용했다.
**Baseline**: 대형 임베딩 모델 Qwen3-Embedding-8B·NV-Embed-v2(7B), 구조 증강 메모리 Mem0·Graphiti·HippoRAG 2, 시간추론 프롬프트 TISER, 참조용 Oracle Message·Full-Context.
기본 LLM은 GPT-4.1-mini, 기본 임베딩은 NV-Embed-v2이며, REMem-I(반복형)와 REMem-S(단발형) 두 설정을 평가했다.
**회상 결과(LLM-J)**: LoCoMo에서 REMem-S가 77.5로 HippoRAG 2(74.0) 대비 +3.5, NV-Embed-v2(73.0) 대비 +4.5; REALTALK에서 REMem-S 65.3으로 HippoRAG 2(55.8) 대비 +9.5를 기록했다. Mem0는 LoCoMo 49.7, REALTALK 14.3으로 크게 뒤처졌고, 평균적으로 SOTA 대비 +3.4% 절대 향상을 달성했다.
**추론 결과**: Test of Time EM에서 REMem-I가 93.1로 90%를 넘은 유일한 방법이며 HippoRAG 2(66.9) 대비 +26.2, Full-Context(79.7) 대비 +13.4를 기록했다. Complex-TR LLM-J에서 REMem-I 89.6으로 HippoRAG 2(81.5) 대비 +8.1, REMem w/ TISER는 92.0(F1 90.6)으로 최고치를 기록했고, 평균 +13.4% 절대 향상을 달성했다.
REMem-I는 REMem-S 대비 추론에서 LLM-J +7.0, EM +20.6의 명확한 우위를 보여 다단계 검색의 필요성을 입증했다.
**거부 성능(LoCoMo, 446개 답불가)**: REMem F1 64.0%(정밀도 73.3%, 재현율 56.8%)로 Graphiti(F1 53.1%, 정밀도 38.9%) 대비 정밀도 +34.4, F1 +10.9이며 거부 횟수는 344 vs 954로 약 1/3에 불과했다.
**효율**: LoCoMo 질의당 입력 토큰이 Full-Context 26k 대비 REMem-I 9k, REMem-S 0.9k로 훨씬 적다.
**Ablation**: gist 제거 시 LoCoMo LLM-J 76.2→48.9로 최대 하락(상황 요소의 주 운반체임을 입증), fact 제거 시 Complex-TR 89.6→87.2(다단계 추론 보조 역할), synonymy 엣지·semantic/lexical 검색 도구 제거도 일관된 성능 저하를 보였다.
인간 평가에서 LLM 판정은 100개 샘플 중 93%가 인간과 일치했고(Pearson r=0.827), F1(0.551)·BLEU-1(0.417)보다 인간 판단에 훨씬 잘 정렬되었다.

---

## Limitation

저자가 명시한 한계로, 오프라인 배치 인덱싱과 달리 메모리를 스트리밍 형식으로 구축하는 것은 별도의 엔지니어링 과제로 남아 있다.
또한 "before/after"의 모호성이 도구 호출 시 부등호에 등호 포함 여부의 불확실성을 유발해, 시간 윈도가 명확한 질의에서는 TISER나 RAG보다 떨어지는 경우가 있다(Test of Time의 NE·RD 유형, Complex-TR의 time-to-event 일부).
오류 분석상 LoCoMo 오류의 46%는 선택·근거 매칭 오류(올바른 슬롯을 찾았으나 값을 잘못 할당), 19%는 시간·수치 추론 오류, 18%는 증거가 검색됐음에도 부당하게 "정보 없음"으로 회피하는 문제였고, Complex-TR 오류의 42%는 시간 윈도 불일치였다.
독자 관점에서 REMem-I는 LoCoMo 인덱싱에 3,604초, 질의당 추론 18.10M 입력 토큰·약 $10의 비용이 들어 REMem-S($2.53)나 임베딩 baseline($0.75) 대비 비싸므로, 다단계 추론이 불필요한 단일 세션 질의(LoCoMo 다세션 질의는 14.2%에 불과)에는 오히려 맥락 노이즈를 유발해 REMem-S보다 나쁠 수 있다.
실제 적용 시 GPT-4.1-mini와 NV-Embed-v2를 가정한 결과라 더 작은 모델에서의 일반화나 장기·복잡 환경에서의 확장성은 미검증이며, 평가가 LLM-as-a-judge에 의존하므로 유효한 패러프레이즈 미인식 같은 판정 편향이 잔존한다.

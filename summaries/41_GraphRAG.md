# From Local to Global: A Graph RAG Approach to Query-Focused Summarization

> **논문 정보**: Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson (Microsoft Research, Microsoft Strategic Missions and Technologies, Microsoft Office of the CTO)
> **arXiv**: 2404.16130v2 (2024.04, 2025.02 개정)
> **코드**: https://github.com/microsoft/graphrag

---

## Problem

기존 벡터 기반 RAG(vector RAG)는 외부 코퍼스에서 쿼리와 국소적으로 관련된 텍스트 레코드를 검색해 LLM 컨텍스트에 주입하는 방식으로, 로컬 질문에는 효과적이지만 전체 코퍼스를 관통하는 주제·패턴을 묻는 "global sensemaking query"에서는 근본적으로 실패한다.
예를 들어 "이 데이터셋의 주요 주제는 무엇인가?" 혹은 "지난 10년간 과학적 발견이 학제간 연구에 의해 어떻게 영향받았는가?" 같은 질문은, 특정 청크 몇 개만으로는 답할 수 없는 query-focused summarization(QFS) 태스크에 속한다.
벡터 RAG는 코사인 유사도 기반 top-k 검색으로 관련 청크만 뽑아오므로, 전체 코퍼스를 포괄하는 상위 주제 구조를 놓치고 "검색된 사실의 샘플을 전역 요약인 것처럼 잘못 제시"하는 위험이 크다.
반면 기존 QFS 방법들은 대개 수천~수만 토큰 규모 문서에 맞춰져 있어, RAG가 처리해야 하는 수십만~수백만 토큰 규모의 private corpus에는 확장되지 않는다.
LLM의 컨텍스트 윈도우 제한(수만~수십만 토큰)은 1M 토큰급 코퍼스를 한 번에 처리하는 것을 불가능하게 만든다.
또한 기존 KG 기반 RAG는 대부분 subgraph나 그래프 속성을 프롬프트에 직접 넣거나 쿼리 시점에 LLM 에이전트가 그래프를 탐색하는 방식이라, 전역 주제 구조를 사전에 체계적으로 요약해두지 못한다.
결과적으로 "대규모 코퍼스에 대한 쿼리 일반성(generality)과 텍스트 양(quantity) 양쪽에 동시에 확장되는" RAG 방법이 부재한 상황이다.
이 간극을 메우는 새로운 인덱싱·질의 처리 구조가 필요하다.

---

## Motivation

센스메이킹(sensemaking)은 Klein et al.(2006)의 정의처럼 "사람·장소·사건 간 연결을 추론하여 궤적을 예측하고 효과적으로 행동하는 과정"으로, 과학적 발견·정보 분석·정책 수립에서 핵심 역량이다.
GPT·Llama·Gemini 같은 LLM은 복잡한 도메인에서 센스메이킹 자체에는 매우 뛰어나지만, 1M 토큰 규모 코퍼스 전체를 한 번의 컨텍스트에 담을 수 없다는 물리적 한계가 존재한다.
따라서 코퍼스를 쿼리 시점에 통째로 처리하는 대신, 사전에 "해석된 구조(interpreted structure)"로 변환해두고 쿼리 시점에는 그 구조만 보는 접근이 필요하다.
그래프는 이러한 구조의 강력한 후보다: 노드=엔티티, 엣지=관계로 코퍼스의 개념적 골격을 압축 표현할 수 있다.
특히 그래프의 modularity(Newman 2006)와 Louvain/Leiden 같은 알고리즘으로 탐지되는 nested modular community 구조는, 코퍼스를 "긴밀히 연결된 엔티티 군집의 계층"으로 자동 분할하는 수단을 제공한다.
각 커뮤니티를 LLM으로 요약하고, 하위 커뮤니티 요약을 상위 커뮤니티 요약으로 재귀적으로 roll-up하면, 전 코퍼스에 대한 다층적 글로벌 요약 인덱스를 사전 구축할 수 있다.
쿼리 시점에는 이 커뮤니티 요약들을 map-reduce로 처리해 부분 답변을 병렬 생성·통합함으로써, 전체 코퍼스를 직접 훑지 않고도 전역 질문에 답할 수 있다.
이 설계는 "local retrieval"과 "global summarization"이라는 상반된 강점을 하나의 파이프라인에서 결합한다.

---

## Method

1. **Source Documents → Text Chunks**: 코퍼스의 원본 문서를 고정 토큰 크기 청크로 분할한다. 본 논문은 600-token 청크에 100-token overlap을 사용한다. 청크 크기는 핵심 설계 파라미터로, 긴 청크는 LLM 호출 횟수를 줄여 비용을 절감하지만 청크 초반부 정보의 recall이 저하된다(lost-in-the-middle 효과).

2. **Text Chunks → Entities & Relationships**: 각 청크에 대해 LLM이 (a) 중요 엔티티(인물·장소·조직 등 named entity)와 (b) 엔티티 간 관계, (c) 각각에 대한 짧은 설명을 추출한다. 예: "NeoChip은 저전력 프로세서 전문 상장 기업", "Quantum Systems가 2016년 NeoChip을 인수해 상장 전까지 보유". 도메인 특화 few-shot exemplar를 통해 과학·의학·법률 등 전문 영역에 커스터마이즈할 수 있다.

3. **Claim Extraction (선택적 covariate)**: 엔티티에 대한 검증 가능한 사실 진술(claims)을 추가로 추출한다. 예: "NeoChip 주가가 NewTech Exchange 상장 첫 주에 급등했다", "Quantum Systems가 2016년 NeoChip을 인수했다". Claims는 엔티티/관계와 함께 그래프의 covariate로 인덱싱된다.

4. **Entities & Relationships → Knowledge Graph**: 여러 청크에서 중복 추출된 동일 요소를 집계한다. 본 논문은 entity matching에 exact string matching을 사용하며, 동일 관계의 중복 횟수가 해당 엣지의 가중치(weight)로 사용된다. 여러 설명은 LLM으로 추상적 요약되어 노드·엣지 단위 설명으로 통합된다.

5. **Knowledge Graph → Graph Communities (Hierarchical Leiden)**: Leiden community detection(Traag et al. 2019)을 계층적으로 적용한다. 각 커뮤니티 내부에서 재귀적으로 sub-community를 탐지해 leaf community까지 내려간다. 각 계층은 그래프 노드를 mutually exclusive, collectively exhaustive(ME/CE)하게 분할해 divide-and-conquer summarization을 가능하게 한다. 구현은 graspologic 라이브러리 사용.

6. **Leaf-level Community Summaries**: 각 leaf 커뮤니티 내부의 엣지들을 source node degree + target node degree 합(overall prominence) 내림차순으로 정렬한 뒤, source 노드 설명 → target 노드 설명 → 엣지 설명 → 관련 claims를 토큰 한계(8k)에 도달할 때까지 템플릿에 추가해 LLM 요약을 생성한다.

7. **Higher-level Community Summaries (Bottom-up Recursion)**: 상위 커뮤니티는 (a) 하위 element 요약이 모두 토큰 한계에 맞으면 leaf와 동일하게 처리하고, (b) 초과하면 sub-community를 element summary token 크기 내림차순으로 정렬해 더 긴 element summary를 더 짧은 sub-community summary로 반복 치환하여 한계에 맞춘다.

8. **Global Query Answering - Prepare**: 사용자 쿼리가 들어오면 선택된 커뮤니티 레벨(C0~C3)의 요약들을 무작위로 셔플해 사전 지정된 토큰 크기의 청크로 분할한다. 셔플은 관련 정보가 한 컨텍스트 윈도우에 집중되어 lost되는 것을 방지한다.

9. **Map Step (Parallel Partial Answers)**: 각 청크에 대해 LLM이 병렬·독립적으로 중간 답변을 생성하며, 동시에 "이 답변이 질문에 얼마나 도움이 되는가"를 0~100 점수로 자기 평가(helpfulness score)한다. 점수 0인 답변은 필터링되어 reduce 단계에서 제외된다.

10. **Reduce Step (Final Global Answer)**: 중간 답변들을 helpfulness score 내림차순으로 정렬하여 새로운 컨텍스트 윈도우에 토큰 한계까지 순차 삽입한 뒤, 이 최종 컨텍스트로 사용자에게 반환할 글로벌 답변을 생성한다.

11. **Community Level Selection (C0~C3)**: C0=root-level(가장 적은 수, 가장 추상적), C1=high-level, C2=intermediate-level, C3=low-level(가장 많은 수, 가장 세부적). 하위 커뮤니티가 없으면 상위 커뮤니티를 projected downwards로 재사용한다.

12. **Adaptive Benchmark Question Generation**: 코퍼스 설명을 LLM에 제공해 K명의 가상 사용자 페르소나 → 각 사용자별 N개 태스크 → 각 (user, task)마다 M개의 고수준 질문을 생성한다. 본 실험은 K=M=N=5로 125개 질문을 생성한다.

13. **LLM-as-a-Judge Evaluation**: 두 시스템의 답변을 LLM 평가자가 head-to-head로 비교하여 승/패/무를 판정한다. 평가 기준: Comprehensiveness(포괄성), Diversity(다양성), Empowerment(독자 이해 지원), 그리고 control criterion인 Directness(직접성·간결성).

14. **Claim-based Validation (Experiment 2)**: Claimify(Metropolitansky & Larson 2025)로 각 답변에서 factual claim을 추출한다. Comprehensiveness는 답변당 평균 claim 수로, Diversity는 claim을 agglomerative clustering(complete linkage, distance=1−ROUGE-L)으로 군집화한 후 평균 클러스터 수로 측정한다.

15. **Pipeline Cost Profile**: 모든 LLM 호출(엔티티 추출·요약 생성·답변 생성)은 8k token 컨텍스트로 수행되며, 인덱싱은 gpt-4-turbo 기준 1M 토큰 Podcast 코퍼스에 281분 소요된다(16GB RAM, Xeon Platinum 8171M, 2M TPM / 10k RPM).

---

## Key Contribution

1. **Graph-Index + Community-Summary 기반 Global RAG의 체계화**: 엔티티 KG 구축 → Leiden 계층적 커뮤니티 탐지 → bottom-up 재귀 요약 → map-reduce 쿼리 처리라는 end-to-end 파이프라인을 최초로 정식화하여, "1M 토큰급 코퍼스에서의 global sensemaking"이라는 이전까지 RAG가 다루지 못한 문제 클래스를 풀어냈다.

2. **Pre-generated Community Summary로 확장성 확보**: 인덱싱 시점에 커뮤니티 요약을 사전 생성해두므로, 쿼리 시점에는 전체 그래프나 원문을 탐색하지 않고도 글로벌 답변이 가능하다. C0(root-level) 사용 시 TS(source text map-reduce) 대비 97% 이상 토큰을 절감하면서도 vector RAG 대비 comprehensiveness 72%, diversity 62% win rate를 유지한다.

3. **Adaptive Benchmark 평가 방법론 제안**: gold standard가 없는 global sensemaking 태스크를 평가하기 위해, LLM이 페르소나·태스크·질문을 자동 생성하고(K×N×M=125) LLM-as-a-judge로 head-to-head 승률을 측정하는 통계적 프레임워크를 제시했다. Directness를 control criterion으로 쓰는 발상이 방법론적 핵심이다.

4. **Claimify 기반 이중 검증(LLM 판정 ↔ Claim 통계)**: LLM 평가의 신뢰성을 검증하기 위해 답변에서 factual claim을 추출·클러스터링하여 comprehensiveness/diversity를 정량화한다. 두 지표의 majority vote 레이블이 78%(comp)·69~70%(div)에서 일치함을 보여 LLM-as-a-judge의 타당성을 확보했다.

5. **오픈소스 생태계 구축 및 산업 채택**: Microsoft GraphRAG로 공개(github.com/microsoft/graphrag)되어 LangChain, LlamaIndex, NebulaGraph, Neo4j 등 주요 RAG 프레임워크에 공식 확장으로 통합되었고, 이후 등장한 HippoRAG·LightRAG·Nano-GraphRAG 등 후속 연구의 베이스라인이 되었다.

6. **Tradeoff 투명화(Directness vs Comprehensiveness)**: Directness는 vector RAG가 일관되게 우위, Comprehensiveness/Diversity는 GraphRAG가 우위임을 정량적으로 보임으로써, 쿼리 유형(local fact retrieval vs global sensemaking)에 따른 방법 선택 가이드를 제공했다.

---

## Experiment

- **데이터셋 1 (Podcast Transcripts)**: Microsoft CTO Kevin Scott의 "Behind the Tech" 팟캐스트 공개 transcript, 1,669개 청크 × 600 token (100 token overlap), 약 1M 토큰 규모.
- **데이터셋 2 (News Articles)**: 2013.09~2023.12 기간의 엔터테인먼트·비즈니스·스포츠·기술·건강·과학 등 다분야 뉴스 (Tang & Yang 2024, MultiHop-RAG 출처), 3,197개 청크 × 600 token, 약 1.7M 토큰.
- **Graph Index 통계**: Podcast는 노드 8,564개·엣지 20,691개 / News는 노드 15,754개·엣지 19,520개.
- **커뮤니티 수 (Podcast / News)**: C0=34/55, C1=367/555, C2=969/1,797, C3=1,310/2,142, TS context units=1,669/3,197.
- **토큰 사용량 (Podcast 기준, per query max context)**: C0=26,657(2.6%), C1=225,756(22.2%), C2=565,720(55.8%), C3=746,100(73.5%), TS=1,014,611(100%). C0는 TS 대비 약 38배 토큰 절감, C3는 약 26~33% 절감.
- **Indexing Time**: Podcast 1M 토큰 기준 gpt-4-turbo로 281분 (VM: 16GB RAM, Intel Xeon Platinum 8171M @ 2.60GHz, 2M TPM / 10k RPM 한도).
- **질문 수**: 각 데이터셋당 125개 (K=M=N=5), 각 head-to-head 비교를 5회 반복 평균.
- **6개 조건**: C0, C1, C2, C3, TS(source text map-reduce), SS(vector RAG semantic search).

**Experiment 1 - LLM-as-a-Judge Win Rate**:
- *Comprehensiveness (Podcast)*: GraphRAG 전 조건이 SS 대비 72~83% 승률 (p<.001). C3가 SS에 79%, C0가 SS에 72%.
- *Comprehensiveness (News)*: GraphRAG 전 조건이 SS 대비 72~80% 승률 (p<.001).
- *Diversity (Podcast)*: GraphRAG 전 조건이 SS 대비 75~82% 승률 (p<.001).
- *Diversity (News)*: GraphRAG 전 조건이 SS 대비 62~71% 승률 (p<.01).
- *Directness*: SS(vector RAG)가 모든 조건에 승리(예상된 tradeoff, validity test 통과).
- *Empowerment*: GraphRAG vs SS 및 GraphRAG vs TS 모두 혼재된 결과, 구체적 인용·예시 포함 여부가 관건으로 분석됨.
- *GraphRAG vs TS*: Podcast C2가 TS에 comprehensiveness 57% 승률 (p<.001), diversity 57% (p=.036); News C3가 TS에 comprehensiveness 64% (p<.001), diversity 60% (p<.001).

**Experiment 2 - Claim-based Metrics**:
- 전체 47,075개 unique claim 추출, 답변당 평균 31개.
- *평균 claim 수 (News / Podcast)*: C0=34.18/32.21, C1=32.50/32.20, C2=31.62/32.46, C3=33.14/32.28, TS=32.89/31.39, SS=25.23/26.50. 모든 global 조건이 SS 대비 유의미하게 많음 (p<.05).
- *평균 cluster 수 (Podcast, distance 0.5)*: C0=23.16, C1=22.62, C2=22.52, C3=21.93, TS=21.14, SS=18.55. Podcast는 모든 threshold에서 global 조건 전부가 SS 대비 유의미 (p<.05).
- *News distance 0.5*: C0=23.42, C1=21.85, C2=21.90, C3=22.13, TS=21.80, SS=17.92. News는 C0만 모든 threshold에서 SS 대비 유의미.
- *LLM 라벨 vs Claim 라벨 일치율*: comprehensiveness 78%, diversity 69~70% (tie가 아닌 비교 중, 각각 전체의 33%·39%).

---

## Limitation

평가가 각각 약 1M 토큰 규모의 Podcast·News 두 코퍼스에 국한되어 있어, 법률·의료·과학 논문 등 다른 도메인과 훨씬 대규모(수억 토큰 이상) 코퍼스로의 일반화가 검증되지 않았다.
인덱싱 비용이 매우 높다: Podcast 1M 토큰 기준 gpt-4-turbo로 281분이 소요되며, 이는 엔티티·관계·클레임 추출과 모든 계층의 커뮤니티 요약 생성에 필요한 대규모 LLM 호출 때문이다.
로컬 질문(특정 엔티티에 대한 구체적 사실 질의)에서는 vector RAG가 더 효율적이며, Directness 기준에서는 모든 비교에서 vector RAG가 우위를 점해 GraphRAG는 본질적으로 global sensemaking에 편향된 방법이다.
Empowerment 기준에서는 GraphRAG vs vector RAG 및 GraphRAG vs TS 모두 혼재된 결과를 보였는데, 이는 커뮤니티 요약 과정에서 구체적 인용·예시·날짜 등 세부 증거가 소실되기 때문으로 분석되며 element extraction 프롬프트의 튜닝이 필요하다.
Leiden 커뮤니티 탐지의 resolution 파라미터, 청크 크기(600 token), 컨텍스트 윈도우(8k)에 따라 커뮤니티 계층과 요약 품질이 민감하게 변할 수 있으나 본 논문은 이 민감도 분석을 포함하지 않는다.
Entity matching에 exact string matching을 사용해 동일 실체의 다른 표기(e.g., "Microsoft" vs "MS Corp")가 별도 노드로 남을 수 있고, 이는 그래프 단편화로 이어질 수 있다.
증분 업데이트(incremental indexing) 메커니즘이 없어 코퍼스에 새 문서가 추가되면 원칙적으로 전체 재인덱싱이 필요하며, 이는 실사용 환경에서 운영 비용을 크게 증가시킨다.
Fabrication(환각) 비율에 대한 분석이 빠져 있어 SelfCheckGPT 등 환각 검증 도구와의 결합 평가가 후속 과제로 남아 있고, 평가 역시 LLM-as-a-judge에 의존해 판정 자체의 편향 가능성이 존재한다.

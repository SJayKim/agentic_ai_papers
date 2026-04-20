# Think-on-Graph 2.0: Deep and Faithful LLM Reasoning with KG-guided RAG

> **논문 정보**: Shengjie Ma, Chengjin Xu, Xuhui Jiang, Muzhi Li, Huaren Qu, Cehao Yang, Jiaxin Mao, Jian Guo (IDEA Research, RUC, CUHK, HKUST)
> **arXiv**: 2407.10805 (2024.07)
> **학회**: ICLR 2025
> **코드**: https://github.com/IDEA-FinAI/ToG-2

---

## Problem

기존 Retrieval-Augmented Generation(RAG) 시스템은 복잡한 다단계 추론에서 충분한 깊이와 완전성을 보장하지 못한다.
텍스트 기반 RAG는 벡터 임베딩을 통한 표층적 의미 유사도에 의존하므로, 서로 다른 텍스트 간의 지식 수준 연결(예: Global Financial Crisis ↔ The 2008 Recession, Harry Potter ↔ Fantastic Beasts)을 포착하지 못한다.
이 한계로 인해 logical link를 추적해야 하는 multi-hop 질문에서 정답 텍스트를 회수(recall)하더라도 단편 정보를 통합하지 못하는 실패가 반복된다.
반면 KG 기반 RAG는 엔티티 간 구조적 관계를 triple 형태로 제공하나, KG 내재적 불완전성(inner incompleteness)과 ontology 바깥의 디테일 부재로 인해 Lukas Verzbicas의 구체적 경기 기록 같은 세부 사실을 답하지 못한다.
텍스트와 KG를 aggregate만 하는 loose-coupling 하이브리드(CoK, HybridRAG)는 한 소스의 검색 결과가 다른 소스의 검색을 개선하지 못해, in-depth retrieval이 요구되는 복잡 질의에서 여전히 부족하다.
결과적으로 LLM이 인간의 reasoning trajectory처럼 단서를 축적하며 심화 탐색을 이어가는 행동을 구현하기가 어렵다.

---

## Motivation

사람은 복잡한 문제 해결 시 현재 단서를 검토하고 기존 지식 프레임워크 위에서 관련 엔티티를 연상하며, 답을 찾을 때까지 주제를 파고든다(Kahneman 2011).
저자들은 이 과정이 KG의 구조적 로드맵과 문서의 비구조 컨텍스트를 긴밀하게 교대(tight-coupling)시키는 것과 유사하다고 본다.
KG는 질문과 목표 정보 사이의 의미 공간상 먼 연결을 탐지할 수 있는 high-level guide를 제공하고, 문서는 엔티티의 미시적 디테일을 보완한다.
따라서 KG 탐색이 문서 검색 범위를 좁히는 방향타 역할을 하고, 문서 컨텍스트가 KG 엔티티 pruning의 판단 근거가 되는 상호 정교화(mutual refinement)가 가능하다.
Training-free로 다양한 LLM에 plug-and-play 적용될 수 있고, 문서만 있는 환경에서도 relation extraction 또는 co-occurrence로 KG를 구축해 범용 적용할 수 있어야 한다.
또한 faithful reasoning을 위해 각 단계의 heterogeneous knowledge를 LLM 추론의 근거로 명시적으로 투입하여 hallucination을 줄여야 한다.

---

## Method

1. **Initialization — NER & Entity Linking**: 질문 q에서 엔티티를 추출하고, Azure AI 등의 entity linking 도구 또는 LLM으로 KG 내 엔티티에 매핑한다.
2. **Topic Prune (TP)**: LLM이 질문과 연결된 엔티티들을 평가해 초기 topic entity 집합 E0_topic = {e1,...,eN}을 선정하며, N은 LLM이 결정한다.
3. **Pre-iteration DRM retrieval**: BGE 등 dense retrieval model이 E0_topic 관련 문서에서 top-k 청크를 뽑고, LLM이 이 정보만으로 답변 가능한지 판단해 가능하면 즉시 종료한다.
4. **Relation Discovery**: i번째 반복에서 Edge(e^i_j) = {(r^i_{j,m}, h_m)} 함수로 각 topic entity의 모든 양방향 관계를 수집한다.
5. **Relation Prune (RP)**: LLM이 q와의 관련성을 점수화해 관계를 가지치기한다. 두 가지 prompt 형식 — 엔티티별 개별 호출(Eq.2, 높은 정밀도) 또는 모든 topic entity를 한 번에 처리(Eq.3, 효율)을 선택 가능하며, 임계값 0.2 미만은 제거 후 top-W 유지.
6. **Entity Discovery**: Tail(e^i_j, (r^i_{j,m}, h_m)) = c^i_{j,m}로 선택된 관계를 통해 candidate entity를 발견한다(예: Crag Sandburg High School, Evan Jager).
7. **Entity-guided Context Retrieval**: 각 candidate entity c^i_{j,m}의 문서 풀을 형성하고, 현재 triple (e^i_j, r^i_{j,m})을 짧은 문장으로 변환해 청크 앞에 붙인 뒤 DRM으로 relevance score s^i_{j,m,z}를 계산한다. 엔티티-컨텍스트 연결을 보존하는 것이 핵심.
8. **Top-K Chunk Selection**: 전체 청크 중 top-K개를 Ctx_i로 채택해 reasoning 단계의 근거로 삼는다.
9. **Context-based Entity Prune**: score(c^i_{j,m}) = Σ_{k=1}^K s_k · w_k · I(top-k 청크가 c^i_{j,m} 소속)으로 순위를 계산하며, w_k = e^{-α·k}의 지수 감쇠 가중합을 사용한다. 상위 W개를 다음 반복의 E^{i+1}_topic으로 승격 — 문서 증거가 KG 탐색 방향을 역방향으로 정제.
10. **Reasoning with Hybrid Knowledge**: PROMPT_rs(q, P_i, Ctx_i, Clues_{i-1})로 LLM에 triple paths, top-K entity contexts, 이전 반복의 Clues를 함께 제시한다.
11. **Sufficiency Check & Clue Update**: 충분하면 답변 출력, 아니면 이번 라운드의 단서 Clues_i를 요약 생성해 최적화된 쿼리로 다음 iteration 진입.
12. **Termination**: 최대 깊이 D에 도달하거나 충분성 판단이 True일 때 종료. 하이퍼파라미터 W=3, D=3, K=10이 기본값.

---

## Key Contribution

1. **KG×Text Tight-coupling RAG paradigm**: KG 탐색과 문서 검색을 순차적으로 aggregate하는 loose-coupling을 넘어, 각 iteration에서 두 소스가 상호 정교화하는 최초의 긴밀 통합 프레임워크 제시.
2. **Context-enhanced Graph Search**: 문서 기반 엔티티 pruning 점수가 다음 round의 KG 탐색 topic entity를 결정함으로써, 문서 증거가 그래프 확장 방향을 역으로 안내.
3. **Knowledge-guided Context Retrieval**: Triple 문장을 쿼리에 prepend해 DRM이 엔티티-컨텍스트 정렬을 유지한 정밀 청크 검색 수행.
4. **Training-free, Plug-and-play**: 추가 학습 없이 GPT-3.5-turbo, GPT-4o, Llama-3-8B, Qwen2-7B 등 다양한 LLM에 즉시 적용 가능.
5. **6/7 SOTA on GPT-3.5**: WebQSP, AdvHotpotQA, QALD-10-en, Zero-Shot RE에서 SOTA, FEVER에서 경쟁적, Creak에서 ToG와 동등.
6. **Smaller LLM Elevation**: Llama2-13B 급 모델의 추론을 GPT-3.5 직접 추론 수준까지 끌어올려 knowledge bottleneck을 보완.
7. **Domain-specific ToG-FinQA 신규 벤치마크**: 2023년 중국어 재무제표 기반 97개 multi-hop 질문과 7종 관계 KG를 공개.

---

## Experiment

- **데이터셋**: WebQSP, QALD-10-en (multi-hop KBQA), AdvHotpotQA (multi-hop doc QA), Zero-Shot RE (slot filling), FEVER/Creak (fact verification), ToG-FinQA (도메인 특화).
- **지식 소스**: full Wikipedia + Wikidata(full Wiki setting) — distractor 설정보다 검색 난이도 높음.
- **백본 LLM**: GPT-3.5-turbo 주력, GPT-4o/Llama-3-8B/Qwen2-7B로 ablation. temperature=0, W=3, D=3, K=10, BGE-embedding 사용.
- **GPT-3.5 주요 결과 (EM/Acc.)**: ToG-2는 WebQSP 81.1% vs ToG 76.2% (+4.9%p), AdvHotpotQA 42.9% vs ToG 26.3% (+16.6%p), QALD-10-en 54.1% vs ToG 50.2% (+3.9%p), Zero-Shot RE 91.0% vs ToG 88.0% (+3.0%p), FEVER 63.1% vs ToG 52.7% (+10.4%p), Creak 93.5% vs ToG 93.8%.
- **Hybrid RAG 대비**: CoK 대비 AdvHotpotQA 42.9% vs 35.4% (+7.5%p), WebQSP 81.1% vs 77.6% (+3.5%p).
- **ToG-FinQA 도메인 특화**: ToG-2 34.0% vs ToG 14.0% vs GraphRAG 6.2% vs CoT 0% vs Vanilla RAG 0%, loose-coupling의 한계를 명확히 보여줌.
- **LLM별 상대 향상 (AdvHotpotQA Direct→ToG-2)**: Llama-3-8B 20.8→34.7 (+66.8%), Qwen2-7B 17.9→30.8 (+72.1%), GPT-3.5 23.1→42.9 (+85.7%), GPT-4o 47.7→53.3 (+11.3%).
- **FEVER LLM별 향상**: Llama-3-8B +49.0%, Qwen2-7B +38.1%, GPT-3.5 +21.8%, GPT-4o +5.9%.
- **Entity pruning tool ablation**: BGE-Reranker가 최고 성능, BM25도 resource-efficient한 대안. LLM ranker는 입력 길이 제약으로 DRM에 열세.
- **Width/Depth 분석**: W=2→3에서 성능 개선, W>3부터 marginal gain 감소. D>3에서 plateau — 무조건 넓은 탐색이 최선이 아님.
- **Runtime**: ToG-2의 entity pruning 단계가 ToG 대비 평균 68.7%로 감소 — DRM이 LLM 기반 pruning보다 더 많은 후보를 빠르게 처리.
- **LLM call 복잡도**: Eq.3 사용 시 최대 2D+(D-1)+1 호출, Eq.2 사용 시 WD+D+1 호출로 ToG의 2WD+D+1 대비 효율적.
- **Manual analysis (50 AdvHotpotQA cases)**: Doc-enhanced 41.94%, Both-enhanced 32.26%, Direct 16.13%, Triple-enhanced 9.68% — 문서 컨텍스트가 주된 정보원.
- **False negative 관찰**: EM 평가 시 alias/detail level 차이로 인한 오판이 다수 존재, 실제 성능은 수치보다 높을 가능성.

---

## Limitation

Wikidata의 부정확성·모순·누락과 Wikipedia 페이지의 key detail 결손 등 지식 소스 자체의 불완전성은 ToG-2가 해결하지 못하는 외재 제약이다.
BGE류 범용 DRM은 질문 유형별 특화 학습 없이 쓰이므로 특정 도메인/질문에서 recall이 불안정하며, one-size-fits-all 검색 모델의 bias가 bottleneck이 된다.
Entity linking 품질에 민감 — EL 오류는 초기 topic entity 선정을 오염시켜 이후 모든 iteration의 탐색 방향을 왜곡시킨다.
W, D, K의 자동 조정 메커니즘이 없어 질문 난이도에 따른 탐색 범위 조절을 사용자가 수동 설정해야 하며, 복잡 질의에 W=3/D=3이 충분치 않을 수 있다.
Creak 같은 단일-hop fact verification에서는 ToG 대비 이점이 사라지거나 미세하게 역전되며, 풍부한 entity 문서 정보가 오히려 "overcautiousness"(Case 2의 Quark 예시)나 출력 포맷 위반(Case 1)을 유발.
EM 기반 평가에서 alias 불일치 및 detail level 모호성으로 인한 false negative가 ToG-2 w/o SC 기준 38.7%에 달해, 평가 메트릭이 실제 성능을 과소평가.
ToG-FinQA 같은 도메인 특화 과제에서 weak LLM (Llama-3-8B 8.2%, Qwen2-7B 10.3%)의 성능이 여전히 낮아, 백본 LLM의 reasoning capacity가 여전히 상한을 규정.
KG 구축 비용 및 relation extraction/entity co-occurrence 기반 대체 KG 품질에 대한 정량 평가가 부재하다.

# HippoRAG 2: Towards Efficient and Robust Long-Term Memory for LLM Agents

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su (Ohio State University / UIUC)
> **arXiv**: 2502.14802 (2025.02) — ICML 2025
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Problem

LLM에 장기 기억 능력을 부여하는 주요 수단이 된 RAG는 단순한 벡터 검색에 의존하여, 인간 장기 기억의 동적이고 상호 연결된 특성을 모방하는 데 근본적 한계를 드러낸다.

표준 RAG는 패시지 단위의 독립적 검색만 수행하므로 여러 사실을 연결해야 하는 연상 기억(associativity, 멀티홉 추론)을 제대로 지원하지 못한다.

또한 큰 담화 전체를 통합해 의미를 만드는 의미 파악(sense-making) 작업에서도 서로 떨어진 패시지의 정보를 엮지 못해 성능이 제한된다.

이 공백을 메우기 위해 GraphRAG, LightRAG, RAPTOR 등 구조 보강 RAG가 제안되었지만, 이들은 연상 기억·의미 파악에서 일부 개선을 보이면서 오히려 단순 사실 QA에서는 표준 RAG보다 큰 성능 저하를 겪는 의도치 않은 부작용을 일으킨다.

구체적으로 LightRAG는 NQ F1이 16.6까지 떨어지고 RAPTOR는 NQ에서 50.7로 NV-Embed-v2 61.9에 현저히 못 미친다.

기존 HippoRAG 1.0은 PPR 기반 멀티홉 추론에는 강하지만 NER 중심의 엔티티 추출에 의존해 질의의 문맥적 신호를 놓치고, 대규모 담화 이해(NarrativeQA) 성능이 특히 열세를 보인다.

그 결과 사실 기억·연상 기억·의미 파악 세 축을 동시에 만족하는 RAG 시스템이 부재하며, 비파라메트릭 지속 학습의 진정한 장기 기억 역할을 수행하지 못한다.

---

## Motivation

인간의 장기 기억은 하나의 단일 능력이 아니라 사실 기억(개별 사실의 정확한 회상), 연상 기억(이질적 지식 간 다단계 연결), 의미 파악(복잡한 맥락 해석)이라는 세 가지 차원을 동시에 지원한다.

LLM 에이전트가 진정한 인간 수준의 지속 학습자가 되려면 비파라메트릭 RAG 시스템도 이 세 차원을 모두 표준 RAG 이상으로 충족해야 한다.

저자들은 기존 구조 보강 RAG가 단일 작업에 과도하게 최적화되어 다른 작업에서 성능이 무너지는 현상을 관찰하고, 서로 다른 메모리 차원에서 측정된 강점을 하나의 프레임워크로 통합하는 것이 필요하다고 본다.

뇌과학적으로는 해마가 sparse coding(적은 뉴런만 활성화)과 dense coding(풍부한 맥락 표현)을 통합하듯, KG에도 phrase 노드(sparse)와 passage 노드(dense)를 함께 도입하는 설계가 자연스러운 귀결이다.

인간 기억의 회상(recall)과 재인(recognition)이라는 이중 과정 역시 온라인 검색에서 임베딩 기반 후보 생성과 LLM 기반 재인 필터링이라는 두 단계로 모델링할 수 있다.

이러한 신경생물학적 영감을 통해 질의를 개별 엔티티가 아닌 트리플 전체와 매칭하면, KG 내 개념 간 관계를 활용해 질의 의도에 더 정합한 시드 노드를 얻을 수 있다.

궁극 목표는 파라미터 수정 없이 코퍼스 확장만으로 새로운 지식을 통합할 수 있는 비파라메트릭 지속 학습 시스템이며, HippoRAG 2는 이 방향의 구체적 실현물로 설계된다.

---

## Method

1. **오프라인 인덱싱 — OpenIE 트리플 추출**: Llama-3.3-70B-Instruct로 각 패시지에서 스키마 없는 (subject, relation, object) 트리플을 생성하고, subject/object phrase는 KG의 phrase 노드로, relation은 relation edge로 구성한다.

2. **Synonym Edge 추가**: NV-Embed-v2로 모든 phrase 노드 쌍의 벡터 유사도를 계산하여 사전 정의 임계값을 넘는 쌍에 synonym edge를 추가해, 서로 다른 패시지에서 등장한 동의어를 연결하고 신·구 지식 통합을 돕는다.

3. **Dense-Sparse Integration (§3.2)**: phrase 노드만 있던 HippoRAG 1.0 KG에, 각 패시지를 passage 노드로 추가하고 `contains` context edge로 해당 패시지에서 파생된 phrase 노드들과 연결하여 개념(sparse)과 문맥(dense)을 한 그래프에 통합한다.

4. **온라인 Query-to-Triple 링킹 (§3.3)**: 기존 NER-to-Node(쿼리에서 엔티티를 뽑아 노드 매칭)나 Query-to-Node 대신, 쿼리 전체를 임베딩하여 KG 내 트리플 전체와 직접 매칭함으로써 개념 간 관계까지 고려한 정렬을 수행한다.

5. **Recognition Memory — 트리플 필터링 (§3.4)**: 상위 k=5개 트리플을 검색한 뒤 Llama-3.3-70B-Instruct에 전달하여 질의와 무관한 트리플을 제거하고, 최종 T' ⊆ T를 얻는다(프롬프트는 DSPy MIPROv2로 튜닝, 최대 4개 사실 선택).

6. **시드 노드 선정**: 필터링된 트리플에서 등장하는 phrase 노드를 시드로 채택하되, 각 phrase 노드의 초기 순위 점수는 그것이 등장한 모든 필터 트리플의 평균 랭킹 점수로 결정한다.

7. **Passage Node 시드 동시 주입**: 모든 passage 노드도 시드로 포함시켜 broader activation을 유도하고, 각 passage 노드의 reset probability에는 weight factor 0.05를 곱해 phrase 노드와의 균형을 맞춘다(가중치는 {0.01, 0.05, 0.1, 0.3, 0.5} 중 검증 세트에서 선택).

8. **Fallback 경로**: 필터링 후 트리플이 하나도 남지 않으면 PPR을 건너뛰고 임베딩 모델이 직접 상위 패시지를 반환하는 경로로 폴백한다.

9. **Personalized PageRank 실행**: 시드 노드 분포를 reset 확률로 사용하여 KG 전체에 확률 질량을 전파하고, context edge를 통해 passage 노드도 자연스럽게 활성화되어 멀티홉 관련 패시지가 부상한다.

10. **QA 리딩**: PPR 결과 상위 5개 passage 노드를 컨텍스트로 Llama-3.3-70B-Instruct QA 리더에 입력하여 최종 토큰 기반 F1을 산출한다.

---

## Key Contribution

1. **사실·연상·의미 파악 세 축 동시 향상**: 단순 QA(NQ, PopQA), 멀티홉 QA(MuSiQue, 2Wiki, HotpotQA, LV-Eval), 담화 이해(NarrativeQA)의 7개 벤치마크에서 표준 RAG와 구조 보강 RAG 양쪽을 동시에 능가한 최초의 시스템이다.

2. **Dense-Sparse Integration**: phrase 노드(개념)와 passage 노드(맥락)를 context edge로 엮어, 기존 HippoRAG의 단순 score ensemble 대신 그래프 구조 내에서 두 표현을 통합한 새로운 KG 설계를 제시한다.

3. **Query-to-Triple 링킹**: NER 기반 엔티티 중심 매칭을 쿼리 전체와 트리플 전체 간 임베딩 매칭으로 대체하여, ablation에서 MuSiQue/2Wiki/HotpotQA 평균 Recall@5가 74.6에서 87.1로 12.5p 상승하는 효과를 확인했다.

4. **Recognition Memory**: 회상과 재인을 구분하는 인지심리학에서 영감을 얻어 임베딩 기반 후보 생성 후 LLM으로 불필요 트리플을 필터링하는 이중 과정을 구현했으며, DSPy MIPROv2로 프롬프트까지 최적화했다.

5. **비파라메트릭 지속 학습 실증**: 코퍼스를 4등분하여 점진적으로 주입하는 지속 학습 실험에서 HippoRAG 2의 NV-Embed-v2 대비 우위가 25%/50%/75%/100% 데이터 구간 전역에서 유지됨을 보였다.

6. **리트리버 독립성**: GTE-Qwen2-7B, GritLM-7B, NV-Embed-v2 세 가지 임베더 모두에서 MuSiQue Recall@5가 각각 +5.2p/+5.6p/+5.0p 상승해 프레임워크가 특정 인코더에 종속되지 않음을 입증했다.

---

## Experiment

**구성**: QA 리더와 OpenIE/필터 LLM 모두 Llama-3.3-70B-Instruct, 리트리버는 NV-Embed-v2(7B)를 사용한다.

**벤치마크 규모**: NQ/PopQA/MuSiQue/2Wiki/HotpotQA 각 1,000 쿼리, LV-Eval 124 쿼리, NarrativeQA 293 쿼리(문서 10편), 패시지 수는 4,111~22,849 범위.

**QA F1 평균**: HippoRAG 2 **59.8**로 최강 벤치마크인 NV-Embed-v2(7B) 57.0보다 **+2.8p**, HippoRAG 1.0 53.1 대비 **+6.7p**, LightRAG 6.6을 크게 상회한다.

**세부 QA F1**: NQ 63.3(vs NV-Embed 61.9), PopQA 56.2, MuSiQue **48.6**, 2Wiki **71.0**(NV-Embed 61.5 대비 +9.5p), HotpotQA 75.5, LV-Eval **12.9**(NV-Embed 9.8 대비 +3.1p), NarrativeQA 25.9 — 7개 중 5개에서 최고 성능.

**검색 Recall@5 평균**: HippoRAG 2 **78.2** vs NV-Embed-v2 73.4(+4.8p), BM25 55.1, Contriever 55.4, GTR 60.7.

**데이터셋별 Recall@5**: NQ 78.0, PopQA 51.7, MuSiQue 74.7(+5.0p vs NV-Embed 69.7), 2Wiki **90.4**(+13.9p vs NV-Embed 76.5), HotpotQA **96.3**(+1.8p vs 94.5).

**Ablation (MuSiQue/2Wiki/HotpotQA Recall@5 평균)**: Full 87.1 → NER-to-Node 74.6(-12.5p), Query-to-Node 59.6(-27.5p), Passage Node 제거 81.0(-6.1p), Filter 제거 86.4(-0.7p) — 링킹 방식이 가장 큰 기여.

**Reset Weight 민감도**: passage 노드 가중치 0.05에서 MuSiQue Recall@5 80.5, NQ 76.9로 최적이며, 0.5로 올리면 MuSiQue가 77.9까지 하락한다.

**지속 학습 실험**: NQ와 MuSiQue를 4개 세그먼트로 분할하여 순차 주입했을 때 HippoRAG 2의 NV-Embed-v2 대비 F1 우위가 25%/50%/75%/100% 구간 모두에서 유지된다.

**리트리버 교체 (MuSiQue Recall@5)**: GTE-Qwen2-7B 63.6→68.8, GritLM-7B 66.0→71.6, NV-Embed-v2 69.7→74.7로 일관된 +5p 개선.

**에러 분석**: Recall@5<1.0인 100개 샘플 중 2-hop 26%, 3-hop 41%, 4-hop 33%이며, 7%는 필터 전에 이미 지지 패시지 phrase가 미매칭, 26%는 필터 후 미매칭, 18%는 필터 후 트리플 zero.

---

## Limitation

PPR 기반 그래프 탐색은 매우 복잡한 다단계 추론 체인(4-hop 이상)에서 탐색 커버리지가 부족할 수 있으며, 에러 분석에서도 4-hop 질문이 실패 샘플의 33%를 차지한다.

온라인 트리플 필터링에 LLM을 호출하므로 검색 지연이 추가되고, 쿼리당 한 번 이상의 70B 모델 호출이 필요해 실시간 응용에 비용 부담이 크다.

지속 학습 실험에서 코퍼스가 확장될 때 단순 QA는 두 방법 모두 성능이 유지되지만 멀티홉 QA는 HippoRAG 2와 NV-Embed-v2가 유사하게 저하되어, 장기 지속 학습의 스케일링 한계는 해소되지 않았다.

트리플 필터링 단계에서 18% 샘플은 모든 트리플이 제거되어 PPR 폴백(dense-only)으로 퇴행하며, 이 때는 본 프레임워크의 그래프 이점이 사라진다.

7% 샘플은 필터 이전에 이미 query-to-triple 단계에서 지지 문서 phrase를 전혀 매칭하지 못해, 임베딩 매칭 자체의 실패 모드가 여전히 존재한다.

평가가 주로 위키피디아 기반 벤치마크에 집중되어 있어 도메인 특화 코퍼스(의료, 법률 등)나 대화형 에피소딕 메모리, 256k 초장문 컨텍스트 등에 대한 일반화 검증은 부족하다.

LV-Eval에서도 F1이 12.9로 절대 성능이 낮아, 지식 누수를 방지한 키워드 치환 벤치마크에서 RAG의 근본적 한계가 여전히 드러난다.

NER-to-Node로 ablation하면 2Wiki Recall@5가 91.2로 오히려 Full 90.4보다 소폭 높아, 링킹 방식의 최적 선택이 데이터셋 특성에 따라 달라질 가능성을 시사한다.

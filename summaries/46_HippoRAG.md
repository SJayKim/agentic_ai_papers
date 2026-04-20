# HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su (Ohio State University, Stanford University)
> **arXiv**: 2405.14831 (2024.05, NeurIPS 2024)
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Problem

RAG는 LLM의 장기 기억으로 사실상 표준이 되었지만, 현재 방법들은 각 패시지를 독립된 벡터로 인코딩한다.
이 isolated encoding 방식은 **패시지 경계를 넘어 지식을 통합(knowledge integration)해야 하는 태스크**에서 근본적 한계를 갖는다.
예를 들어 "알츠하이머 연구를 하는 Stanford 교수는 누구인가?" 같은 질문은, 두 속성이 한 패시지에 동시에 언급되지 않으면 표준 RAG가 절대 찾지 못한다.
Multi-hop QA 역시 동일한 문제를 갖는다: 서로 다른 패시지의 단서를 이어야 정답에 도달하지만, dense retriever는 개별 패시지의 쿼리 유사도만 고려한다.
현재의 해결책은 IRCoT처럼 반복적 검색·생성을 수행하는 것이지만, 이는 **LLM 호출이 수 배로 늘어 비용·지연이 폭증**하며, 근본적으로 해결하지 못하는 케이스가 존재한다.
저자들이 "path-finding multi-hop question"이라 부르는 부류는, 따라야 할 경로가 사전에 정해지지 않고 **여러 가능한 경로 중 하나를 탐색해 찾아내야** 하므로 반복 검색으로도 풀리지 않는다.
또한 RAPTOR·GraphRAG처럼 오프라인에서 요약 계층을 만드는 방법은 지식이 새로 추가될 때마다 요약을 재생성해야 하여 **지속 업데이트(continual integration)에 부적합**하다.
결국 기존 시스템은 "저장", "업데이트", "통합" 세 축을 동시에 만족하는 long-term memory를 제공하지 못한다.

---

## Motivation

포유류 뇌는 수백만 년의 진화를 통해 **방대한 지식을 저장하면서 새 경험을 끊임없이 통합하는 장기 기억 시스템**을 발달시켰다.
인지신경과학의 대표적 이론인 **해마 기억 인덱싱 이론(Teyler & Discenna, hippocampal memory indexing theory)** 은 이를 세 컴포넌트의 상호작용으로 설명한다.
**신피질(neocortex)** 은 지각 입력을 고수준 표현으로 가공하고 실제 기억 내용을 저장하며, **방해마 영역(parahippocampal regions, PHR)** 은 신피질과 해마 간 신호를 라우팅하고, **해마(hippocampus)** 는 CA3의 조밀한 뉴런 네트워크를 통해 기억 단위 간의 연관을 저장하는 인덱스로 작동한다.
이 인덱스 덕분에 뇌는 **부분 단서만 주어져도 연관된 전체 기억을 빠르게 완성(pattern completion)** 할 수 있고, 새 정보가 들어오면 신피질 표현 전체를 바꾸지 않고 인덱스에 엣지만 추가함으로써 **catastrophic forgetting 없이** 통합한다.
또한 인지과학 연구는 인간의 단어 회상 순서가 **PageRank의 출력과 강한 상관**을 보인다는 증거를 제시하여, 연상 인덱스 위에서 확률적 그래프 탐색을 수행한다는 가설을 뒷받침한다.
저자들은 LLM(신피질 역할)이 개념을 추출·처리하는 능력과, KG+PageRank(해마 역할)가 연관 인덱스를 저장·탐색하는 능력을 결합하면, **단일 검색 단계에서 multi-hop 연관 추론이 가능**할 것이라 예측했다.
즉, isolated passage encoding을 버리고 **명시적 개념 노드와 그 연관 엣지 위의 그래프 탐색**으로 장기 기억을 구현하자는 것이 핵심 동기다.

---

## Method

HippoRAG는 LLM L, 검색 인코더 M, KG+Personalized PageRank라는 세 컴포넌트를 **뇌의 신피질·PHR·해마에 각각 대응**시키는 프레임워크다.

1. **오프라인 인덱싱 — OpenIE로 스키마리스 KG 구축**: 코퍼스 P의 각 패시지에 대해 강력한 instruction-tuned LLM(기본 GPT-3.5-turbo-1106, temperature 0)을 1-shot 프롬프트로 호출해 **명사구 노드 N과 관계 엣지 E**를 담은 트리플을 추출한다.

2. **2단계 프롬프트 설계**: 먼저 named entity를 추출하고, 그 다음에 해당 엔티티들을 OpenIE 프롬프트의 컨텍스트로 넣어 **최종 트리플을 생성**한다. 이 구조가 "named entity 편향"과 "일반 개념 포함" 사이의 적절한 균형을 유지함을 저자들이 관찰했다.

3. **동의어 엣지 추가(PHR 역할)**: 검색 인코더 M(Contriever 또는 ColBERTv2)으로 KG 내 모든 명사구 쌍의 코사인 유사도를 계산해, 임계값 **τ=0.8 이상이면 synonymy edge E′ 를 추가**한다. 이는 완전 동일하지 않지만 의미상 같은 개념 간 pattern completion을 도와준다.

4. **Passage-Node 매트릭스 P 생성**: 인덱싱 과정에서 |N|×|P| 크기의 행렬 P를 만들어 **각 명사구가 어느 패시지에 몇 번 등장했는지 저장**한다. 이 행렬이 나중에 PPR 확률을 passage 점수로 매핑하는 다리 역할을 한다.

5. **Node Specificity 계산**: 각 노드 i에 대해 sᵢ = |Pᵢ|⁻¹ (노드가 추출된 패시지 수의 역수)를 정의한다. IDF와 유사한 신호지만, **글로벌 집계 없이 각 노드가 국소적으로 보유하는 정보만으로 계산**되어 신경생물학적으로 타당하다. 많은 패시지에 퍼진 일반 노드일수록 가중치가 낮아진다.

6. **온라인 검색 — 쿼리 엔티티 추출**: 쿼리 q가 들어오면 같은 LLM에 1-shot NER 프롬프트를 주어 **query named entities Cq = {c₁,...,cₙ}** 을 추출한다 (예: "Stanford", "Alzheimer's").

7. **Query Node 매핑**: 추출된 엔티티 Cq를 검색 인코더 M으로 인코딩하고, **KG 내 모든 명사구와 코사인 유사도를 비교**해 최대 유사도를 갖는 노드를 query node Rq로 선택한다.

8. **Personalized PageRank 실행**: KG(|N| 노드, |E|+|E′| 엣지) 위에서 PPR을 돌리되, **personalized probability distribution n⃗**을 query node에 동등 확률을 주고 나머지는 0으로 세팅한다. 각 query node 확률은 사전에 **node specificity sᵢ를 곱해 modulate**한 뒤 주입된다.

9. **PPR 파라미터**: **damping factor(restart 확률) = 0.5**로 고정하여, 랜덤 워크가 query node에서 재시작할 확률과 주변으로 확산될 확률의 균형을 맞춘다.

10. **확률 전파**: PPR이 수렴하면 업데이트된 분포 n⃗′ 를 얻는데, 이 분포는 query node의 **공동 이웃(joint neighborhood)에 확률 질량이 집중**되어 있다. 여러 query node를 동시에 연결하는 매개 노드(예: Prof. Thomas)가 자연스럽게 부상한다.

11. **Passage 스코어링**: 최종 passage 점수 벡터 p⃗ = n⃗′ᵀ · P 로 계산한다. 즉 **각 패시지의 점수는 그 패시지에 등장한 노드들의 PPR 확률 합**이며, 상위-k 패시지가 반환된다.

12. **Single-Step Multi-Hop**: 이 전체 과정은 **검색 단계를 한 번만 수행**하면서도 KG 구조 덕에 multi-hop 경로를 암묵적으로 탐색한다. IRCoT와 달리 LLM reasoning loop가 불필요하다.

13. **IRCoT와의 결합**: HippoRAG를 IRCoT의 retriever로 꽂아 넣는 것도 가능해, **상호 보완적 성능 향상**이 가능하다 (반복 검색의 각 step마다 HippoRAG가 더 정확한 후보를 공급).

14. **하이퍼파라미터 튜닝**: MuSiQue 학습셋 100개 예제만으로 τ=0.8, damping=0.5를 고정했으며, 다른 데이터셋에도 그대로 전이된다 (robustness 확인).

---

## Key Contribution

1. **해마 기억 인덱싱 이론의 RAG 적용**: 신피질(LLM OpenIE) + PHR(retrieval encoder 동의어 매칭) + 해마(KG+PPR)의 3-컴포넌트 구조로 인간 장기 기억 메커니즘을 RAG에 최초 이식. 각 컴포넌트가 이론의 pattern separation·completion 기능에 대응한다.

2. **Single-Step Multi-Hop 검색 달성**: MuSiQue·2WikiMultiHopQA에서 반복 검색 없이 **R@5 기준 최대 20%p 성능 향상**. 특히 2Wiki의 AR@5(전체 supporting passages 동시 검색률)가 ColBERTv2의 37.1%에서 75.7%로 **두 배 이상** 상승.

3. **10~30배 저렴, 6~13배 빠른 온라인 검색**: IRCoT 대비 LLM 호출이 쿼리당 1회(엔티티 추출)로 줄어 비용·지연이 급감하면서도 동등 이상 성능 유지. 이는 실제 서빙에서 결정적 이점.

4. **Path-Finding Multi-Hop QA에서 유일하게 성공**: "알츠하이머 신경과학을 하는 Stanford 교수" 유형처럼 다수 경로 중 하나를 찾아내야 하는 질문에서 ColBERTv2·IRCoT 모두 실패, HippoRAG만 정답 패시지(Thomas Südhof) 검색 성공.

5. **Continual Knowledge Integration**: RAPTOR·GraphRAG처럼 요약 계층을 재구축할 필요 없이, **새 지식은 KG에 트리플 엣지만 추가**하면 되어 지속 업데이트가 자연스럽다. 이는 long-term memory의 필수 요건.

6. **Node Specificity라는 neurobiologically plausible IDF**: 글로벌 집계 없이 각 노드의 로컬 카운트만으로 IDF 효과를 내는 메커니즘을 설계, MuSiQue R@2에서 +3.3%p 기여.

7. **IRCoT와의 직교적 결합성**: HippoRAG를 IRCoT의 retriever로 사용하면 단독보다 **R@5 추가 +4%(MuSiQue), +18%(2Wiki)** 향상. 구조적 retrieval과 iterative reasoning이 상호 보완함을 실증.

---

## Experiment

- **벤치마크**: MuSiQue (1,000 dev), 2WikiMultiHopQA (1,000 dev), HotpotQA (1,000 dev).
- **코퍼스 규모**: MuSiQue 11,656 패시지 / KG 91,729 고유 노드 / 107,448 트리플, 2Wiki 6,119 패시지 / 42,694 노드 / 50,671 트리플, HotpotQA 9,221 패시지 / 82,157 노드 / 98,709 트리플.
- **동의어 엣지 수**: ColBERTv2 기반으로 MuSiQue 191,636 / 2Wiki 82,526 / HotpotQA 171,856개 추가.
- **Baseline**: BM25, Contriever, GTR, ColBERTv2, Propositionizer, RAPTOR (+ColBERTv2 변종), IRCoT (iterative).
- **Metric**: R@2, R@5 (retrieval), EM/F1 (QA), AR@2/AR@5 (all-recall, 모든 supporting passage가 retrieval 되었는지).

**Single-Step Retrieval (R@2 / R@5)**:
- MuSiQue: HippoRAG(ColBERTv2) 40.9 / 51.9 vs ColBERTv2 37.9 / 49.2.
- 2WikiMultiHopQA: HippoRAG 70.7 / 89.1 vs ColBERTv2 59.2 / 68.2 (**+11.5%p R@2, +20.9%p R@5**).
- HotpotQA: HippoRAG 60.5 / 77.7 vs ColBERTv2 64.7 / 79.3 (경쟁적, 소폭 하락).
- 평균 R@5: HippoRAG(ColBERTv2) 72.9 vs ColBERTv2 65.6 (+7.3%p).

**IRCoT 결합 Multi-Step Retrieval (R@5)**:
- MuSiQue: IRCoT+HippoRAG 57.6 vs IRCoT+ColBERTv2 53.7 (+3.9%p).
- 2Wiki: IRCoT+HippoRAG 93.9 vs IRCoT+ColBERTv2 74.4 (**+19.5%p**).
- HotpotQA: IRCoT+HippoRAG 83.0 vs IRCoT+ColBERTv2 82.0 (+1.0%p).

**All-Recall (AR@5, 모든 supporting passage 검색률)**:
- MuSiQue: HippoRAG 22.4% vs ColBERTv2 16.1% (+6.3%p).
- 2Wiki: HippoRAG 75.7% vs ColBERTv2 37.1% (**+38.6%p, 두 배 이상**).
- HotpotQA: 57.9 vs 59.0 (거의 동일).

**QA Performance (EM / F1)**:
- MuSiQue: HippoRAG 19.2 / 29.8 vs ColBERTv2 15.5 / 26.4 (+3.7 EM / +3.4 F1).
- 2Wiki: HippoRAG 46.6 / 59.5 vs ColBERTv2 33.4 / 43.3 (**+13.2 EM / +16.2 F1**).
- IRCoT+HippoRAG 전체 평균 EM 38.4 / F1 51.7.

**OpenIE 대체 실험 (MuSiQue R@2 / 평균 R@5)**:
- REBEL (전용 OpenIE 모델): 31.7 / 58.4 (**-9.2%p 대폭 하락** — GPT-3.5가 REBEL보다 트리플 수 2배, 일반 개념 포함 능력 우위).
- Llama-3.1-8B-Instruct: 40.8 / 67.8 (GPT-3.5와 거의 동등, 8B 오픈모델로 대체 가능성 입증).
- Llama-3.1-70B-Instruct: 41.8 / 72.5 (GPT-3.5 상회).

**PPR 대체 실험 (MuSiQue R@2 / 평균 R@5)**:
- Rq Nodes Only (PPR 제거, 쿼리 노드만): 37.1 / 56.2 (**PPR이 평균 R@5에서 +16.7%p 기여**).
- Rq + 1-hop Neighbors: 25.4 / 59.2 (단순 이웃 확장이 오히려 성능 악화, PPR의 확률 가중 필요성 입증).

**Ablation (평균 R@5)**:
- w/o Node Specificity: 70.9 (-2.0%p, 특히 MuSiQue에서 -3.3%p / HotpotQA에서 -4.0%p).
- w/o Synonymy Edges: 70.5 (-2.4%p, 특히 2Wiki에서 -3.5%p로 named-entity 중심 데이터에 큰 영향).

**효율성**: IRCoT 대비 online retrieval **10~30배 저렴, 6~13배 빠름** (Appendix G).

---

## Limitation

저자 언급:
- 모든 컴포넌트(LLM, retriever, PPR)가 **off-the-shelf**이며 특화 fine-tuning 없음 → 컴포넌트별 맞춤 학습 시 추가 향상 여지.
- 에러 분석(Appendix F)에서 **NER 및 OpenIE 단계가 전체 에러의 대부분**을 차지 → 이 단계의 fine-tuning이 가장 큰 지렛대.
- PPR이 모든 엣지를 **동등 가중으로** 다루므로 relation type을 탐색에 반영하는 개선 필요 (예: 특정 관계에 따른 전이 확률 가중).
- **긴 문서에서 OpenIE 일관성 저하** (Appendix F.4): 짧은 패시지 대비 트리플 추출이 불안정 → 청크 분할 전략 개선 필요.
- **스케일러빌리티 미검증**: 본 실험 최대 11,656 패시지이며, **수백만 수준 코퍼스에서의 KG 크기·PPR 수렴 시간·인덱싱 비용이 실증되지 않음**.

독자 관점 추가 한계:
- KG 품질이 LLM OpenIE에 결정적으로 의존(REBEL로 대체 시 -9.2%p) → **지식 인덱싱 비용이 패시지당 LLM 호출 비용에 비례**, 대규모 코퍼스에서 초기 비용 큼.
- 동의어 엣지가 τ=0.8 고정 임계값에 민감 → 도메인별(법률·의료) 유사도 분포 차이로 재튜닝 필요할 수 있음.
- HotpotQA에서 ColBERTv2에 소폭 뒤지는 결과(R@2 60.5 vs 64.7) → **knowledge integration 요구가 낮은 데이터에서는 concept-based retrieval이 context-based retrieval 대비 손해**일 수 있음(concept-context tradeoff).
- **동적 업데이트 시나리오의 일관성 유지** 방법이 미제시: 새 트리플 추가 시 기존 synonymy edge·node specificity를 어떻게 갱신할지 알고리즘 레벨에서 불명확.
- PPR 확률 계산이 KG 크기에 따라 스케일 → **추론 latency 분석이 제한적**이며 수백만 노드에서의 수렴 시간 미보고.
- Path-finding 케이스의 성공이 **정성적 예시 수준**에 머물러, 정량 벤치마크화가 없어 일반화 수준 판단이 어려움.

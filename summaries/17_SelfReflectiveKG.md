# Self-Reflective Planning with Knowledge Graphs: Enhancing LLM Reasoning Reliability for QA

> **논문 정보**: Jiajun Zhu, Ye Liu, Meikai Bao, Kai Zhang, Yanghai Zhang, Qi Liu (University of Science and Technology of China, State Key Laboratory of Cognitive Intelligence)
> **arXiv**: 2505.19410v1 (2025.05) | **학회**: -
> **코드**: https://anonymous.4open.science/r/SRP-E06C

---

## Problem

LLM은 사전학습 시점의 내부 지식 범위를 벗어나는 질문에 대해 hallucination을 일으키기 쉽고, 최신·희소 사실을 정확히 재현하지 못한다.

Knowledge Graph(KG)와 결합하면 구조화된 검증 가능한 사실 정보를 활용할 수 있지만, 기존 접근법은 불완전하거나 사실과 불일치하는 reasoning path를 생성한다.

Fine-tuning 기반 방법(TransferNet, SR+NSM+E2E 등)은 대규모 고품질 주석 데이터가 필요하고, 새 도메인 적응이 어려우며 막대한 연산 자원을 소모한다.

Prompt 기반 방법(KB-BINDER, StructGPT, ToG, Readi 등)은 reasoning path의 "계획(planning)"에만 집중하고, 검색된 triplet이 실제 질문에 부합하는지 "반영(reflection)"하지 못한다.

예를 들어, "Profiles in Courage의 저자가 어디서 자랐는가"라는 질문에 대해 기존 모델은 `people.person.place_of_birth` 대신 `people.place_lived.location`을 따라가 "Washington, D.C."라는 오답을 반환한다 — 정답 "Brookline"을 놓치는 것이다.

이는 검색 결과의 사실적 일관성을 판단하고 잘못된 reasoning path를 수정하는 자기 반성 메커니즘이 부재하기 때문이다.

첫 번째 관계(1-hop relation) 선택이 잘못되면 그 이후의 모든 검색이 오염되지만, 기존 방법은 출발 관계를 KG의 실제 구조와 정렬하는 사전 검증 단계를 갖추지 않는다.

결과적으로 multi-hop KGQA에서 "searching success rate"와 "reliable answering rate"(triplet에 실제로 뒷받침되는 정답 비율)가 낮은 상태로 머문다.

---

## Motivation

KG의 구조적·검증 가능한 정보를 LLM의 자연어 추론 능력과 결합하되, 검색 결과를 반복적으로 검증·수정하는 피드백 루프를 도입해야 한다.

인간이 문제를 풀 때 답을 도출한 후 다시 검토하고 수정하는 것처럼, LLM도 reasoning path에 대한 반성 과정을 갖추어야 신뢰성이 높아진다.

Self-Refine, Reflexion 등 self-correction 연구에서 영감을 받아, KG 검색 결과에 대한 판단(judge)과 경로 편집(edit)을 반복하는 구조를 KGQA에 이식한다.

유사 질문-추론경로-정답 트리플을 reference로 검색하여 계획과 반성 과정의 가이드로 활용하면, LLM이 KG의 관계 명칭 체계를 더 정확히 예측할 수 있다.

특히 첫 번째 관계(1-hop relation)를 사전 점검함으로써 reasoning path의 출발점을 KG의 실제 구조에 정렬시킬 수 있고, 그 이후 단계의 오류 전파를 줄인다.

Fine-tuning 없이 prompt만으로 reliable한 planning과 reflection을 가능하게 하여, 도메인 적응 비용을 최소화하면서도 SOTA 성능을 달성하는 것이 목표이다.

---

## Method

SRP(Self-Reflective Planning)는 4개 모듈로 구성된 iterative 프레임워크로, fine-tuning 없이 prompt 기반으로 동작한다.

1. **Reference Searching — Base 구축**: 학습 데이터에서 (질문, reasoning path, 정답) 트리플을 추출하여 reference base를 만든다. 각 질문을 all-MiniLM-L6-v2(sentence-transformers)로 dense 벡터화하고, K-Means 클러스터링 후 각 클러스터에서 동일 개수 샘플링하여 총 100개 reference를 저장한다.

2. **Reference Searching — Top-k 검색**: 추론 시 입력 질문을 같은 인코더로 임베딩하고, KNN으로 reference base에서 Top-k(k=4)를 검색하여 계획·반성 모듈에 컨텍스트로 주입한다.

3. **Path Planning — Relation Check**: 주제 엔티티 e_q의 1-hop 관계 집합 R_a를 KG에서 가져온 뒤, LLM이 reference를 참고하여 각 관계의 질문 관련도를 0~1 점수로 산정(합=1)하고 상위 K개(예: 3개)를 초기 관계 R_0으로 선정한다.

4. **Path Planning — Path Generation**: 질문 q, 초기 관계 R_0, 주제 엔티티 e_q, 그리고 참고 reference를 입력으로 LLM이 전체 reasoning path p = e_0 → r̂_0 → r̂_1 → … → r̂_l 을 few-shot 프롬프트로 생성한다(WebQSP 3-shot, CWQ/GrailQA 4-shot).

5. **Knowledge Retrieval — 관계 매칭**: 생성된 path의 각 예측 관계 r̂_d에 대해, Pyserini 기반 하이브리드 검색(BM25 + Contriever)으로 KG 내 의미적으로 유사한 관계 top-5를 얻어 후보 집합 R_d^s를 구성한다.

6. **Knowledge Retrieval — Triplet 인스턴스화**: 시작 엔티티 e_0부터 순차적으로, 현재 엔티티의 1-hop 관계 중 후보 집합에 포함된 것이 있으면 해당 triplet (e_d, r_d, e_{d+1})을 회수하여 triplet sequence S를 누적한다. 매칭 실패 시 그 단계에서 중단한다.

7. **Reflection — Sequence Judge**: LLM이 triplet sequence S를 평가하여 (a) 답변 포함 여부(<HAVE_ANSWER>/<NO_ANSWER>), (b) 불필요 subsequence를 식별한다. 연속된 유효 부분만 pruned sequence S'로 남기고, thinking process를 judge message로 기록한다.

8. **Reflection — Path Edit**: 답이 부족하면, pruned sequence의 tail entity에 연결된 1-hop 관계를 후보로 가져와 judge message와 reference를 참고하여 reasoning path를 수정한다. 예: `performance.actor` → `performance.film`으로 교체.

9. **Iterative Loop**: 수정된 path는 Knowledge Retrieval(5~6)로 돌아가 재검색되고 다시 Judge → Edit를 반복한다. 답 확보 또는 편집 상한(최대 반복 횟수) 도달 시 종료한다.

10. **Answering**: Judge가 "have answer"로 판정하면, pruned sequence S'를 CoT 프롬프트에 넣어 최종 답을 생성한다(WebQSP/CWQ/GrailQA 모두 5-shot).

11. **프롬프트 구성**: Relation Check 1-shot, Sequence Judge 2-shot, Path Edit 4~5-shot, Answering 5-shot의 few-shot 데모를 사용한다.

12. **백본·하이퍼파라미터**: LLM은 GPT-3.5-turbo와 GPT-4.1-mini 두 종류, 모든 모듈 temperature 0.3, 각 관계에 대해 top-5 유사 관계 검색, KG는 Virtuoso 서버에 배포된 Freebase.

---

## Key Contribution

1. **Self-Reflective Planning 프레임워크**: LLM이 KG 검색 결과를 반복적으로 judge·edit하는 iterative reflection 메커니즘을 KGQA에 체계화하여, prompt만으로 reliable reasoning path를 생성한다.

2. **Reference-guided dual-stage 설계**: K-Means 클러스터 기반 reference base와 KNN 검색을 통해, 유사 사례를 planning과 reflection 양쪽에 가이드로 동시 주입하는 구조를 제안한다.

3. **Relation Check 모듈**: 첫 번째 관계를 LLM 점수화로 사전 검증하여 reasoning path의 출발점을 KG의 실제 구조에 정렬함으로써 이후 단계의 오류 전파를 차단한다.

4. **Fine-tuning 없이 SOTA**: prompt 기반만으로 fine-tuned 모델(TIARA, TransferNet, SR+NSM+E2E, Flexkbqa)을 능가하는 성능을 입증하여, 저비용 KG-LLM 통합의 가능성을 보인다.

5. **신뢰성 정량 지표 제시**: searching success rate와 reliable answering rate라는 두 메트릭을 도입해 단순 Hits@1을 넘어 "정답이 KG triplet에 실제로 근거하는 비율"을 측정한다.

6. **Path Edit 기반 오류 복구**: judge message + pruned sequence + reference를 동시에 활용하여 잘못된 관계 예측을 정확한 관계로 교체하는 명시적 편집 전략을 설계한다.

7. **3개 benchmark 일반화 검증**: WebQSP, CWQ, GrailQA(I.I.D./Compositional/Zero-shot)에서 일관된 성능 향상을 확인하여 zero-shot 설정까지 견고함을 보인다.

---

## Experiment

**데이터셋**: WebQSP(train 3,098 / test 1,628, max hop 2), CWQ(27,639 / 3,531, max 4), GrailQA(44,337 / 1,000, max 4). 모두 Freebase 기반이며 Hits@1을 주 지표로 사용한다.

**주 성능 (SRP-GPT4.1-mini)**: WebQSP **83.6%**, CWQ **69.0%**, GrailQA overall **78.8%** (I.I.D. 75.8%, Compositional 62.6%, Zero-shot 85.8%).

**주 성능 (SRP-GPT3.5)**: WebQSP 78.6%, CWQ 58.7%, GrailQA 71.2%로 동일 백본의 Readi-GPT3.5(74.5% / 56.7% / 67.0%)를 모두 상회한다.

**vs Readi (동일 백본)**: SRP-GPT4.1-mini는 Readi-GPT4.1-mini(80.9% / 60.2% / 71.7%) 대비 WebQSP +2.7%p, CWQ **+8.8%p**, GrailQA **+7.1%p** 우세하다.

**vs Fine-tuned**: TIARA(WebQSP 75.2%, GrailQA 73.0%), TransferNet(WebQSP 71.4%, CWQ 48.6%), Flexkbqa(WebQSP 60.6%, GrailQA 62.8%)를 모두 능가한다.

**vs LLM-only**: GPT-4.1-mini 단독(WebQSP 64.2% / CWQ 52.4% / GrailQA 36.5%) 대비 GrailQA에서 +42.3%p의 거대한 격차가 발생해 KG 통합 효과를 확증한다.

**vs ToG**: Table 5에서 SRP-GPT4.1-mini(83.6 / 69.7 / 78.8)는 ToG-GPT4(82.6 / 67.6 / 81.4)와 WebQSP·CWQ에서 우위, GrailQA에서만 소폭 열세 — 파라미터 수 차이를 고려하면 경쟁력 있다.

**Ablation (Table 3, WebQSP/CWQ/GrailQA)**: Full SRP 78.5 / 58.7 / 71.2.

- w/o relation check: 76.9 / 56.7 / 62.9 — GrailQA **-8.3%p**로 최대 손실.
- w/o self-reflection: 76.9 / 55.5 / 68.7 — CWQ -3.2%p로 multi-hop 질문에서 반성 효과 큼.
- w/o reference: 75.7 / 57.6 / 69.8 — WebQSP -2.8%p.
- w/ random reference: 77.0 / 58.2 / 70.9 — 유사도 기반 검색이 무작위 대비 우수함을 확인.

**Searching Success Rate (Table 4)**: SRP-GPT4.1-mini WebQSP **85.3%**, CWQ **70.3%**, GrailQA **85.0%** vs Readi-GPT4.1-mini 64.3% / 41.6% / 74.2% — CWQ에서 **+28.7%p**의 극적 격차.

**Reliable Answering Rate**: WebQSP에서 SRP-GPT4.1-mini **92.2%** vs Readi-GPT4.1-mini 70.5%로 **+21.7%p**. GrailQA에서는 SRP가 **95% 이상** 유지.

**Case Study**: Question 1("Romney가 사는 주") — Readi는 `place_of_birth`에서 막히지만 SRP는 `places_lived` → `people.place_lived.location`으로 편집하여 "Massachusetts" 도출. Question 2(Dominican Republic + UTC-05:00) — Readi는 `base.locations.countries.continent`에서 실패하고 지식 기반 추측("North America")으로 오답, SRP는 `location.location.containedby`로 수정하여 "Greater Antilles" 정답 도출.

**구현 세부**: reference base 크기 100, Top-k=4, temperature 0.3, BM25+Contriever top-5 관계 검색.

---

## Limitation

반복적 reflection 과정에서 Judge–Edit–Retrieval 루프가 수회 도는 동안 LLM 호출 횟수가 증가하여, single-pass 방법 대비 추론 비용과 latency가 증가한다.

저자들은 이를 future work로 "reliable하면서도 효율적인 반성 메커니즘 탐색"으로 남기고 있으며, 실제 edit 반복 상한과 평균 호출 수에 대한 정량 분석은 보고되지 않았다.

Reference Searching 성능은 학습 세트에서 추출한 reference 품질에 의존하며, 도메인 shift 시(예: 새로운 KG 스키마, 다른 언어) reference의 유용성이 저하될 수 있다.

저자 본인들도 "dynamic reference adaptation과 lightweight verification"을 향후 과제로 명시한다.

Freebase 단일 KG에서만 검증되었고, Wikidata·DBpedia·도메인 특화 KG 등 관계 명칭 체계가 크게 다른 환경에 대한 일반화는 실험되지 않았다.

Reflection 반복 횟수에 상한이 있어 매우 깊은 multi-hop(4 hop 이상) 또는 관계 명칭이 모호한 질문에서는 수렴하지 못하고 "편집 실패"로 종료될 가능성이 존재한다(Case Study Question 2에서 Readi의 Edit Fail 사례가 시사).

GPT-3.5와 GPT-4.1-mini 두 가지 proprietary 백본만 실험하여, LLaMA·Mistral·Qwen 등 오픈소스 LLM이나 7B 이하 소형 모델에서의 재현성과 효과는 미확인이다.

GrailQA Compositional split(62.6%)에서는 여전히 Readi-GPT4.1-mini(60.1%) 대비 소폭 우위에 그쳐, 복잡한 구성적 일반화에서의 절대 성능은 개선 여지가 크다.

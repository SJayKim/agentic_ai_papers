# Self-Reflective Planning with Knowledge Graphs: Enhancing LLM Reasoning Reliability for QA

> **논문 정보**: Jiajun Zhu, Ye Liu, Meikai Bao, Kai Zhang, Yanghai Zhang, Qi Liu (University of Science and Technology of China)
> **arXiv**: 2505.19410v1 (2025.05) | **학회**: -
> **코드**: https://anonymous.4open.science/r/SRP-E06C

---

## Problem

LLM은 내부 지식 범위를 벗어나는 질문에 대해 hallucination을 일으키기 쉬우며, 사전학습 시점의 지식에만 의존하는 한계가 있다. Knowledge Graph(KG)와 결합하면 구조화된 사실 정보를 활용할 수 있지만, 기존 접근법은 불완전하거나 사실과 불일치하는 reasoning path를 생성하는 문제를 안고 있다. Fine-tuning 기반 방법은 대규모 고품질 데이터가 필요하고, 새 도메인 적응이 어려우며 막대한 연산 자원을 소모한다. Prompt 기반 방법은 계획(planning)에만 집중하고, 검색된 정보가 실제 질문에 부합하는지 반영(reflection)하지 못한다. 예를 들어, "Profiles in Courage의 저자가 어디서 자랐는가"라는 질문에 대해 기존 모델은 `place_of_birth` 대신 `place_lived.location`을 따라가 오답을 반환한다. 검색 결과의 사실적 일관성을 판단하고, 잘못된 reasoning path를 수정하는 자기 반성 메커니즘이 부재하다.

---

## Motivation

KG의 구조적 정보를 LLM의 추론 능력과 결합하되, 검색 결과를 반복적으로 검증·수정하는 피드백 루프가 필요하다. 인간이 문제를 풀 때 답을 도출한 후 다시 검토하고 수정하는 것처럼, LLM도 reasoning path에 대한 반성 과정을 갖추어야 신뢰성이 높아진다. 유사 질문-답변 쌍(reference)을 검색하여 계획과 반성 과정의 가이드로 활용하면, LLM이 KG의 관계 구조를 더 정확히 예측할 수 있다. 첫 번째 관계(1-hop relation)를 사전 점검함으로써, reasoning path의 출발점을 KG의 실제 구조에 정렬시킬 수 있다. Self-correction 연구(Reflexion, Self-Refine 등)에서 영감을 받아, KG 검색 결과에 대한 판단(judge)과 경로 편집(edit)을 반복하는 구조를 설계한다.

---

## Method

SRP(Self-Reflective Planning)는 4개 모듈로 구성된 iterative 프레임워크이다.

1. **Reference Searching**: 학습 데이터에서 질문-reasoning path-정답 트리플을 추출하여 reference base를 구축. 각 질문을 all-MiniLM-L6-v2로 인코딩, K-Means 클러스터링 후 균등 샘플링하여 저장. 추론 시 KNN으로 Top-k(k=4) reference 검색.

2. **Path Planning — Relation Check**: 주제 엔티티의 1-hop 관계를 KG에서 가져온 뒤, LLM이 reference를 참고하여 각 관계의 질문 관련도를 점수화. 상위 K개를 초기 관계 R₀로 선정.

3. **Path Planning — Path Generation**: 질문, 초기 관계, 주제 엔티티를 입력으로 LLM이 전체 reasoning path를 생성.

4. **Knowledge Retrieval**: 생성된 path의 각 예측 관계에 대해 BM25 + Contriever로 유사한 관계 top-5를 검색하고, 실제 KG에서 1-hop 관계와 매칭하여 triplet sequence를 구성. 매칭 실패 시 해당 단계에서 중단.

5. **Reflection — Sequence Judge**: LLM이 검색된 triplet sequence를 평가하여 (a) 답변 포함 여부, (b) 불필요 triplet 여부를 판단. 관련 부분만 pruned sequence로 남기고 판단 근거를 기록.

6. **Reflection — Path Edit**: 답변이 부족하면, pruned sequence의 마지막 엔티티에 연결된 1-hop 관계를 후보로 가져와 reasoning path를 수정. 수정된 path는 Knowledge Retrieval로 돌아가 재검색.

7. **Judge → Edit → Retrieval 루프**: 답변 확보 또는 편집 한도 도달까지 반복.

8. **Answering**: 답변 있음 판단 시, pruned sequence를 바탕으로 CoT 추론으로 최종 답변 생성. 전체 프레임워크는 fine-tuning 없이 prompt만으로 동작.

---

## Key Contribution

1. **Self-Reflective Planning 프레임워크**: LLM이 KG 검색 결과를 반복적으로 판단·수정하는 iterative reflection 메커니즘을 최초로 체계화.
2. **Reference-guided reasoning**: 유사 사례를 검색하여 계획과 반성 양쪽에 가이드로 활용하는 구조 설계.
3. **Relation Check 모듈**: 첫 번째 관계를 사전 검증하여 reasoning path의 출발점을 KG 구조에 정렬.
4. **Fine-tuning 없이 SOTA**: prompt 기반만으로 fine-tuned 모델(TIARA, Flexkbqa 등)을 능가.
5. **Searching success rate와 reliable answering rate**: 추론 경로의 신뢰성을 정량적으로 검증.

---

## Experiment & Results

- **데이터셋**: WebQSP(3,098/1,628), CWQ(27,639/3,531), GrailQA(44,337/1,000). Freebase 기반, Hits@1.
- **SRP-GPT4.1-mini**: WebQSP **83.6%**, CWQ **69.0%**, GrailQA overall **78.8%** (I.I.D. 75.8%, Compositional 62.6%, Zero-shot 85.8%).
- SRP-GPT3.5: WebQSP 78.6%, CWQ 58.7%, GrailQA 71.2% — Readi-GPT3.5(74.5%, 56.7%, 67.0%) 대비 일관되게 상회.
- SRP-GPT4.1-mini vs Readi-GPT4.1-mini: WebQSP +2.7%p, CWQ **+8.8%p**, GrailQA **+7.1%p**.
- Fine-tuned 모델 대비: TIARA(WebQSP 75.2%), TransferNet(71.4%), Flexkbqa(60.6%) 모두 능가.
- **Ablation**: Relation Check 제거 시 GrailQA 71.2→62.9% (-8.3%p). Self-reflection 제거 시 CWQ 58.7→55.5% (-3.2%p). Reference 제거 시 WebQSP 78.5→75.7% (-2.8%p).
- **Searching Success Rate**: SRP-GPT4.1-mini — WebQSP **85.3%**, CWQ **70.3%**, GrailQA **85.0%** vs Readi(64.3%, 41.6%, 74.2%).
- **Reliable Answering Rate**: WebQSP에서 **92.2%** vs Readi 70.5% (+21.7%p).

---

## Limitation

- 반복적 reflection에서 LLM 호출 횟수가 증가하여 single-pass 대비 추론 비용이 높다.
- Reference 품질이 학습 데이터의 품질과 도메인에 의존하며, 도메인 shift 시 유용성이 저하될 수 있다.
- Freebase 단일 KG에서만 검증되었으며, Wikidata 등 다른 KG에 대한 일반화는 미검증.
- Reflection 반복 횟수에 상한이 있어 매우 복잡한 multi-hop 질문에서 수렴하지 못할 가능성이 존재.
- GPT-3.5와 GPT-4.1-mini 두 가지 백본만 실험하여, 오픈소스 LLM이나 소형 모델에서의 효과는 미확인.

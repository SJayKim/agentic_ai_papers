# Plan-on-Graph: Self-Correcting Adaptive Planning of LLM on Knowledge Graphs

> **논문 정보**: Liyi Chen, Panrong Tong, Zhongming Jin, Ying Sun, Jieping Ye, Hui Xiong (USTC, Alibaba Cloud, HKUST-GZ)
> **arXiv**: 2410.23875 (2024.10)
> **학회**: NeurIPS 2024
> **코드**: N/A

---

## Problem

LLM은 out-of-date knowledge, hallucination, opaque decision-making이라는 고질적 한계를 가지며, 이를 보완하기 위해 Knowledge Graph(KG)를 통합하는 KG-augmented LLM 패러다임이 등장했다.
그러나 StructGPT, ToG와 같은 기존 프롬프팅 기반 KG-augmented LLM은 탐색 너비(breadth)를 사람이 수동으로 사전 고정해야 하며, 고정된 너비가 질문 의미와 맞지 않을 경우 올바른 엔티티를 모두 놓치게 된다.
또한 경로 탐색이 단방향(unidirectional)으로만 진행되어 잘못된 경로에 진입해도 되돌아올 수 없으며, 일단 오류 경로에 들어서면 오류가 누적되어 추론이 실패로 귀결된다.
복잡한 질문에서 LLM이 질문의 일부 조건(partial conditions)을 망각하여 여러 조건을 동시에 만족하는 답을 생성하지 못하는 현상도 발생한다.
예를 들어 "Taylor Swift의 곡 중 AMA를 수상한 곡"이라는 질문에서, 고정 너비(≤3) 제약으로 정답 "Blank Space"를 후보에서 제외하고 오답 경로를 계속 확장한 뒤 AMA 조건을 잊어버리고 "Love Story"를 답하는 실패 사례가 관찰된다.
결과적으로 기존 패러다임은 질문 의미에 기반한 적응적 탐색(adaptive exploration)과 자가 교정(self-correction)을 지원하지 못해, 효율과 정확도 양쪽에서 bottleneck을 갖는다.

---

## Motivation

KG-augmented LLM이 복잡한 다중 조건 질문을 안정적으로 풀려면, (i) 탐색 너비를 질문 의미에 따라 유연하게 조정하고 (ii) 잘못된 경로를 감지·역추적하는 능력이 동시에 필요하다.
저자들은 인간의 문제 해결 과정을 모방하여, 먼저 질문을 서브 목표(sub-objectives)로 분해하고 각 서브 목표를 탐색의 안내(Guidance)로 사용하면 관련 경로 식별이 쉬워진다고 가정한다.
LLM의 추론 능력만으로는 모든 경로 선택이 옳다고 보장할 수 없으므로, 과거 탐색 정보를 메모리에 저장하고 이를 근거로 반성(Reflection)을 수행해야 오류 경로를 교정할 수 있다.
특히 서브 목표별 상태(sub-objective status)를 명시적으로 관리하면 긴 추론 체인에서 조건 망각을 완화할 수 있다.
또한 고정 너비 대신 LLM이 상황에 맞게 소수의 관련 관계·엔티티만 선택하는 적응적 너비(adaptive breadth)를 쓰면 불필요한 경로 확장을 줄여 효율을 동시에 높일 수 있다.
따라서 Guidance + Memory + Reflection의 세 메커니즘을 결합한 self-correcting adaptive planning 패러다임이 기존 ToG류의 한계를 돌파하는 자연스러운 설계 방향이 된다.

---

## Method

PoG는 Task Decomposition → Path Exploration → Memory Updating → Evaluation(Reflection) 루프를 반복 수행하는 training-free 프롬프팅 프레임워크이다.

1. **Task Decomposition (Guidance)**: LLM이 질문 q를 서브 목표 리스트 O = {o1, o2, o3, ...}로 분해하며, 이후 전 과정의 탐색 방향을 안내한다. 서브 목표는 서로 의존 관계를 가질 수 있다.
2. **Topic Entity 초기화**: 질문의 topic entity Tq(데이터셋에서 사전 링크됨)를 초기 엔티티 집합 E0으로 설정하여 경로 탐색을 시작한다.
3. **Relation Exploration**: D번째 반복에서 E^(D-1)의 tail 엔티티와 연결된 모든 관계를 후보 집합 R_cand^D로 수집한 뒤, LLM이 q와 서브 목표 O를 근거로 flexible한 수의 relation을 선택한다(고정 breadth 없음).
4. **Entity Exploration**: 선택된 관계 R^D에 대해 (e^(D-1), r^D, ?) 또는 (?, r^D, e^(D-1)) 쿼리로 후보 엔티티 E_cand^D를 조회한다. 후보가 많으면 경량 DistilBERT로 질문과의 유사도 기반 recall을 수행한 뒤, LLM이 최종 엔티티를 flexible하게 선택한다.
5. **Memory Updating - Subgraph**: 검색된 관계·엔티티 전체를 누적한 G_Sub를 유지하며, reflection에서 어느 엔티티로 backtrack할지 결정하는 근거로 쓰인다.
6. **Memory Updating - Reasoning Paths**: 엔티티 간 관계 구조를 보존하는 경로 집합 P를 갱신하여, LLM이 의미 구조를 이해하고 경로 교정을 수행할 수 있게 한다.
7. **Memory Updating - Sub-Objective Status**: 각 서브 목표의 현재까지 알려진 정보 요약 S를 LLM이 갱신하여, 조건 망각을 방지하고 reflection에서 부족한 조건을 식별하게 한다.
8. **Evaluation**: LLM이 현재 정보로 질문에 답할 수 있는지 판단한다. 충분하면 reasoning paths + sub-objective status + LLM 내부 지식을 통합하여 최종 답을 생성한다.
9. **Reflection (Self-Correction 판정)**: 정보가 불충분하면 q, S, P, 다음 탐색 예정 엔티티 E^D를 입력으로 LLM이 "현재 경로를 그대로 확장할지" vs "다른 엔티티로 backtrack할지"를 결정하고 그 이유를 함께 출력한다.
10. **Backtrack 엔티티 결정**: self-correction이 필요하면 누적 후보 E_cand = E_cand^1 ∪ ... ∪ E_cand^D 중에서 S와 reflection 이유를 근거로 되돌아갈 엔티티 E_add^D를 선택한다.
11. **경로 재시작**: E^D = E^D ∪ E_add^D로 다음 탐색 엔티티 집합을 확장하여 새로운 방향으로 경로 탐색을 재개한다.
12. **반복 및 종료**: 위 3~11단계를 정보가 충분하다고 판단될 때까지 반복하며, 종료 시 통합 추론으로 최종 답변을 출력한다.

---

## Key Contribution

1. **최초의 KG 반성 메커니즘**: KG-augmented LLM에 self-correction과 adaptive exploration을 동시에 통합한 최초의 연구로, reflection 기반 경로 역추적을 KG 추론에 도입했다.
2. **Guidance·Memory·Reflection 3중 메커니즘**: 서브 목표 분해(Guidance), 3종 구성요소(subgraph·reasoning paths·sub-objective status)의 Memory, 그리고 Reflection을 협력적으로 설계해 adaptive breadth를 보장한다.
3. **Adaptive Breadth**: 사전 정의된 고정 너비를 제거하고, LLM이 질문·서브 목표에 따라 관련 관계·엔티티를 flexible한 수로 선택하도록 하여 불필요한 경로 확장을 억제한다.
4. **Training-free SOTA**: 파인튜닝 없이 프롬프팅만으로 CWQ·WebQSP·GrailQA의 fine-tuned KG-augmented LLM 기법들(GAIN, RoG 등)을 능가한다.
5. **효율성 이득**: ToG 대비 LLM 호출 수·토큰 소비·소요 시간을 전 데이터셋에서 대폭 감소시켜, 정확도와 효율을 동시에 확보한다.
6. **Zero-shot 강건성**: GrailQA의 zero-shot 서브셋에서 GPT-3.5만으로도 모든 fine-tuned 기법을 큰 폭으로 능가하여, reflection이 분포 외 질문 처리에 특히 유효함을 보인다.

---

## Experiment

- **데이터셋**: CWQ, WebQSP, GrailQA (모두 Freebase 기반 multi-hop KGQA). GrailQA는 ToG와 동일한 테스트 샘플 사용. 평가지표는 Hits@1(exact match accuracy).
- **백본 LLM**: GPT-3.5 / GPT-4 두 설정에서 평가, baseline도 동일 조건 매칭.

**CWQ Hits@1**: IO Prompt 37.6, CoT 38.8, SC 45.4, StructGPT 54.3, ToG(GPT-3.5) 57.1, **PoG(GPT-3.5) 63.2**, ToG(GPT-4) 67.6, **PoG(GPT-4) 75.0** — GPT-4 기준 ToG 대비 +7.4%p.

**WebQSP Hits@1**: RoG 85.7(fine-tuned), ToG(GPT-3.5) 76.2, **PoG(GPT-3.5) 82.0**, ToG(GPT-4) 82.6, **PoG(GPT-4) 87.3** — fine-tuned RoG도 능가.

**GrailQA Overall/I.I.D./Compositional/Zero-shot**: GAIN(fine-tuned) 76.3/88.5/73.7/71.8, ToG(GPT-3.5) 68.7/70.1/56.1/72.7, **PoG(GPT-3.5) 76.5/76.3/62.1/81.7**, ToG(GPT-4) 81.4/79.4/67.3/86.5, **PoG(GPT-4) 84.7/87.9/69.7/88.6** — zero-shot에서 GPT-3.5로도 fine-tuned GAIN(+9.9%p) 능가.

**효율성 (GPT-3.5, 평균/질문)**: CWQ LLM 호출 ToG 22.6 → PoG 13.3 (-41%), 총 토큰 9669.4 → 8156.2, 출력 토큰 1486.4 → 353.2 (-76.2%), 시간 96.5s → 23.3s (4배 이상 speedup). WebQSP 호출 15.9 → 9.0, 시간 63.1s → 16.8s. GrailQA 호출 11.1 → 6.5, 시간 50.2s → 11.5s.

**Ablation (CWQ / WebQSP / GrailQA)**: PoG 전체 63.2 / 82.0 / 76.5 기준, w/o Memory 58.9 / 77.5 / 69.3 (-4.3/-4.5/-7.2%p, 최대 하락), w/o Reflection 59.4 / 78.1 / 70.5, w/o Guidance 60.1 / 80.3 / 72.4, w/o Adaptive Breadth 61.3 / 80.2 / 73.8.

**Case Study (CWQ)**: "Who is in control of the place where 'The Naked and the Dead' takes place?"에서 CoT는 답변 거부, ToG는 KG 탐색 실패 후 환각 답변(US Army), PoG는 최초 Panama 도달 후 정보 부족을 감지하고 reflection으로 "President of Panama" 관계를 재탐색해 정답 Juan Carlos Varela를 복구.

---

## Limitation

서브 목표 분해 품질이 전적으로 LLM의 의미 분석 능력에 의존하므로, 약한 LLM에서는 잘못된 분해가 이후 전 과정 탐색 실패를 유발할 위험이 크다.
Reflection 단계가 매 iteration마다 추가 LLM 호출을 유발하며, 간단한 질문에서는 불필요한 오버헤드가 될 수 있다.
서브그래프·추론 경로·서브 목표 상태를 모두 메모리에 누적하므로, 매우 긴 추론 체인이나 밀도 높은 KG에서는 컨텍스트 길이 제약에 근접할 수 있다.
Topic entity가 데이터셋 단계에서 사전 linking되어 있다는 가정을 공유하여, real-world에서 entity linking이 누락되거나 모호한 경우 성능이 저하될 수 있다.
평가가 Freebase 기반 KGQA 세 데이터셋에 한정되어, 스키마가 다른 KG(위키데이터·도메인 KG)나 동적·이질적 KG로의 일반화가 검증되지 않았다.
Adaptive breadth가 LLM의 선택에 의존하므로, LLM이 과소·과대 선택하는 편향을 가질 경우 reflection이 늦게 발동되어 교정 지연이 발생할 수 있다.

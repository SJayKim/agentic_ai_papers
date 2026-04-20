# AvaTaR: Optimizing LLM Agents for Tool-Augmented Reasoning via Contrastive Reasoning

> **논문 정보**: Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Kaidi Cao, Vassilis N. Ioannidis, Karthik Subbian, Jure Leskovec, James Zou (Stanford University / Amazon)
> **arXiv**: 2406.11200 (2024.06, NeurIPS 2024)
> **코드**: https://github.com/zou-group/avatar

---

## Problem

LLM 에이전트는 외부 도구와 지식을 활용하여 정확도를 높이고 환각(hallucination)을 줄이는 데 뛰어난 능력을 보여주었다.
그러나 에이전트가 도구를 효과적으로 사용하도록 안내하는 프롬프트 엔지니어링은 여전히 휴리스틱하고 노동 집약적인 작업으로 남아 있다.
실제 문제 해결은 (1) 복잡한 질문을 실행 가능한 계획으로 분해, (2) 제공된 도구를 전략적으로 사용하여 관련 정보를 수집, (3) 중간 결과를 합성하여 정확한 응답을 생성하는 다단계 절차를 요구한다.
각 단계마다 수동으로 프롬프트를 조정해야 하며, 수많은 시행착오를 거쳐야 한다.
기존의 "mega-prompt" 방식은 세심한 수작업을 필요로 하면서도 취약한 구현을 만들어내며, 예를 들어 ReAct 에이전트는 "TUSA swim fins with split fin design" 같은 질의에 대해 브랜드 정보를 무시하거나 문자열 매칭 점수가 모두 0이 되는 trivial solution으로 빠진다.
또한 self-reflection, self-refine 같은 기존 자동 프롬프트 최적화 기법은 단일 인스턴스 기반 피드백에 집중하여 다단계 도구 사용에서 발생하는 시스템적 오류를 포착하지 못한다.
더욱이 이러한 인스턴스 수준 최적화는 특정 샘플에 과적합되어, 도구 선택과 문제 분해 같은 여러 요소가 상호작용하는 복잡한 태스크에 일반화되지 못한다.

---

## Motivation

저자들은 "학습 경사(gradient)"라는 개념을 LLM 프롬프트 최적화에 적용하되, 단일 샘플이 아닌 배치 단위 대조적 추론(contrastive reasoning)을 통해 더 견고한 신호를 추출할 수 있다는 직관에서 출발한다.
성공(positive) 궤적과 실패(negative) 궤적을 배치로 묶어 비교하면, 특정 케이스에 과적합되지 않는 시스템적이고 범용적인 도구 사용 전략을 자동으로 식별할 수 있다.
이는 인간이 의사결정 시 현재 상황을 과거 경험과 대조하여 판단하는 과정에서 영감을 받았으며, Reflexion의 episodic memory 개념을 확장한다.
또한 파인튜닝 없이 도구 설명과 소규모 훈련 데이터(~100개)만으로 에이전트를 최적화함으로써, 계산 비용이 낮고 적응성이 높은 프레임워크를 제공할 수 있다.
기존 방법들과 달리 Self-Improvement, Memory, Generalization, Holistic Prompt Generation 네 가지 속성을 모두 충족하는 통합 프레임워크의 필요성도 동기를 부여한다.
Comparator가 생성하는 지시문은 문제 분해 전략, 도구 선택, 점수 합성 방식까지 포괄적으로 다루어 다단계 태스크 전반의 결함을 동시에 교정할 수 있다.
이러한 holistic 접근은 특히 지식 그래프 검색처럼 멀티모달 정보를 수반하는 복잡한 실세계 태스크에 효과적일 것으로 가정된다.

---

## Method

AvaTaR는 Actor LLM과 Comparator LLM 두 컴포넌트로 구성되며, 최적화 단계(optimization phase)와 배포 단계(deployment phase)로 나뉜다.

**1. Actor 구성**
Actor 에이전트는 초기 지시문/프롬프트를 기반으로 초기 action을 생성하고, 업데이트된 지시문에 따라 action을 조정하는 역할을 한다.
초기 지시문에는 태스크 설명과 사용 가능한 도구 정보(Python 등 프로그래밍 언어로 제공)가 포함된다.
Actor는 도구 호출 시퀀스를 Python 코드와 자연어 설명이 결합된 형태로 출력한다.

**2. Positive/Negative 쿼리 분류 (Step 1)**
Comparator는 (question, answer) 쌍으로 이루어진 훈련 데이터에 현재 action sequence를 적용하여 성능 평가 후, 두 개의 임계값 ℓ과 h (0 < h ≤ ℓ < 1)를 사용해 쿼리를 분류한다.
Recall 같은 평가 지표가 ℓ 이상인 쿼리는 positive, h 이하인 쿼리는 negative로 분류된다.
훈련 동역학에 따라 lower bound를 조정하여 충분한 negative 샘플을 확보할 수 있다.
분류 후 랜덤 샘플링으로 b개의 미니배치를 구성하되, positive와 negative를 각 b/2씩 동일하게 배분한다.

**3. 대조적 추론 기반 지시문 생성 (Step 2)**
Comparator는 두 그룹의 쿼리를 주요 특성에 따라 대조하고, 성능 격차를 구체적 도구 사용 결함에 귀속시킨 뒤, 전체적(holistic) 개선 방안을 제안한다.
예를 들어 positive 쿼리는 명사 개념("woman", "man")을 많이 포함하는 반면 negative 쿼리는 동작("ride", "cook")과 속성("blue", "light")처럼 더 넓은 범위를 다룬다는 패턴을 발견하고, 형용사/복합명사/동사구에 대한 별도 추출 로직을 추가하라는 지시를 생성한다.
배치 단위 대조를 통해 per-sample 지시문이 야기하는 과적합을 방지하고 robust "gradient"를 추출한다.

**4. Logistic Instructions**
Comparator의 태스크 성능 지시문과 직교하는 두 종류의 보조 지시문을 병행한다.
Validity Check는 각 action 실행 시 함수 호출의 올바름(예: 인자 타입, 반환 값 형식)을 내부적으로 검증한다.
Timeout Error는 비효율적 action sequence가 교착 상태에 빠지는 것을 방지하며, 임계값을 초과하면 오류를 발생시켜 Actor가 중복 연산을 제거하도록 유도한다.

**5. Memory Bank**
Reflexion에서 영감을 받아, 과거 action sequence, Comparator 지시문, 훈련 서브셋 성능의 튜플을 저장한다.
Context 크기 관리를 위해 상위 5개 최고 성능 action sequence만 유지하며, Actor가 즉각적 지시와 과거 결과를 모두 학습하도록 한다.

**6. 배포 단계**
최적화가 끝난 후 최고 성능 프롬프트나 action sequence를 테스트 인스턴스에 적용한다.
검색 태스크에서는 최적화된 action sequence를 직접 배포하고, QA 태스크에서는 최적화된 instruction을 사용해 Actor가 새 쿼리에 대한 action sequence를 생성한다.

**7. Emerging Behavior**
최적화 과정에서 Actor는 ParseAttributeFromQuery로 brand/type/material/features를 분해하고, ComputeEmbeddingSimilarity로 type 필터링 후 GetTopk로 상위 20개 후보 추출, TokenMatchScore로 브랜드 매칭, GetSatisfactionScoreByLLM으로 LLM 검증 후 WeightedSum(coefficients=(0.43, 0.37, 0.20))으로 종합 점수를 합성하는 정교한 다단계 파이프라인을 스스로 구축한다.
IDF 기반 재가중치 같은 고수준 도구를 Actor가 자체 개발하는 현상도 관찰된다.

**8. 하이퍼파라미터와 훈련 설정**
모든 데이터셋에 대해 동일한 초기 프롬프트 구조를 사용하며, Recall@20 또는 Accuracy를 positive/negative 분류 지표로 사용한다.
하이퍼파라미터는 ℓ = h = 0.5, b = 20으로 통일한다.
지식 검색 태스크용 함수 라이브러리는 28개 함수로 구성되며, QA 태스크는 Google, Arxiv 검색 API를 제공한다.

---

## Key Contribution

1. **Comparator 기반 대조적 추론 프롬프트 최적화**: positive/negative 배치를 대조하여 시스템적 도구 사용 결함을 식별하고 holistic instruction을 자동 생성하는 모듈을 최초로 제안하여 특정 샘플 과적합 문제를 회피한다.
2. **네 가지 속성 통합 프레임워크**: Self-Improvement, Memory, Generalization, Holistic Prompt Generation을 모두 지원하는 유일한 에이전트 최적화 프레임워크로, 기존 ReAct/Self-Refine/Reflexion 대비 우위를 증명한다.
3. **7개 벤치마크 전역 SOTA**: 4개 검색 태스크(STARK-AMAZON/MAG/PRIME, FLICKR30K)에서 Hit@1 평균 +14%, 3개 QA 태스크(HotpotQA, ArxivQA, ToolQA)에서 평균 +13% 향상을 달성한다.
4. **강력한 일반화 능력**: STARK 벤치마크의 human-generated leave-out 쿼리에서 Hit@1 평균 +20.9% 향상으로, 학습 분포와 다른 실세계 쿼리에도 견고함을 보인다.
5. **Emerging Tool Development**: 최적화 과정에서 Actor가 IDF 기반 재가중치, 학습된 계수 기반 WeightedSum 등 고수준 도구와 전략을 자체 개발하는 창발적 행동을 관찰하며, 동적 도구 라이브러리의 가능성을 시사한다.
6. **파인튜닝 없이 저자원 최적화**: 25 iterations만으로 FLICKR30K Hit@1을 5.1% → 28.6%로, STARK-PRIME Recall@20을 30.3% → 39.3%로 개선하여 경량 최적화 가능성을 증명한다.

---

## Experiment

**벤치마크**: 검색 4개 (STARK-AMAZON, STARK-MAG, STARK-PRIME, FLICKR30K-Entities), QA 3개 (HotpotQA, ArxivQA, ToolQA의 SciREX/Agenda 서브태스크).
QA에서 훈련/테스트 쿼리 수는 HotpotQA 100/100, ArxivQA 100/100, ToolQA 40/60이다.

**베이스라인**: DPR, QAGNN, ada-002, multi-ada-002, ReAct, Reflexion, ExpeL, Retroformer, CoT, 그리고 Comparator를 제거한 ablation AvaTaR-C.

**STARK 검색 주요 수치**:
- AMAZON: Hit@1 49.87% (Reflexion 42.79% 대비 +16.6% 상대), Hit@5 69.16%, Recall@20 60.57%, MRR 58.70%.
- MAG: Hit@1 44.36% (Reflexion 40.71% 대비 +9.6%), Hit@5 59.66%, MRR 51.15%.
- PRIME: Hit@1 18.44% (Reflexion 14.28% 대비 +20.7%), Hit@5 36.73%, Recall@20 39.31%, MRR 26.73%.
- 세 데이터셋 평균 Hit@1 +15.6%, MRR +9.5% 개선.

**FLICKR30K-Entities (claude3)**: Hit@1 42.4% (clip-vit-large 37.2, ReAct 38.8, Reflexion 28.4 대비), Hit@5 63.0%, Recall@20 79.2%, MRR 52.3%.
25 iterations만으로 초기 Hit@1 5.1%에서 28.6%까지 상승.

**QA 태스크 (EM/LLM judge)**:
- HotpotQA: 53.0% (ReAct 40.0, Reflexion 46.0, Retroformer 51.0 대비).
- ArxivQA: 84.0% (Reflexion 77.0 대비).
- ToolQA SciREX-Easy: 37.5%, SciREX-Hard: 23.3% (ReAct 17.5 대비 +33.1% 상대).
- ToolQA Agenda-Easy: 60.0%, Agenda-Hard: 4.17%.

**최적화 다이나믹스**: STARK 검증 성능이 AMAZON 35% → 75%, MAG 20% → 78%로 대폭 상승하며 Comparator 지시문의 효과를 뒷받침한다.
Memory Bank가 과거 최고 성능 action을 저장하여 수렴을 가속한다.

**Ablation (AvaTaR-C)**: Comparator 제거 시 STARK-PRIME Hit@1이 18.44% → 8.82%, STARK-MAG Hit@1이 44.36% → 33.25%로 급락하며 대부분 태스크에서 ReAct 수준으로 회귀 — Comparator가 핵심 기여 요소임을 확인.

**일반화 평가**: STARK human-generated leave-out 쿼리에서 Hit@1 평균 +20.9% 향상으로 학습 분포 외 쿼리에도 견고.

**Emerging Behavior 분석 (FLICKR30K 25 iterations)**: Improved Divide-and-Conquer 4회, Sensible Tool Differentiation 16회, Numerical Parameter Learning 5회의 지시문 유형 분포가 관찰되며, visual_weight를 0.5 → 0.6으로 조정하거나 VqaByLLM을 GetVisualAttributesByLLM + TokenMatchScore로 교체하는 구체적 개선이 이뤄진다.

---

## Limitation

(저자 언급) 최적화 수렴 속도가 태스크 복잡도에 비례하며, 각 iteration마다 batch 크기 b=20의 쿼리에 대해 Actor와 Comparator가 LLM 호출을 반복하므로 고비용 LLM 호출이 다수 필요하다.
(저자 언급) ExpeL과 같이 경험을 수집하는 방식은 대규모 검색 태스크에서 비용이 과도하여 샘플링된 STARK-MAG 테스트셋에서만 비교를 수행했으며, 이는 본 프레임워크도 대규모 적용 시 비용 문제가 있음을 시사한다.
(독자 관점) 도구 수와 도구 간 상호작용이 증가할 때 배치 대조의 효과가 유지될지에 대한 확장성 검증이 부족하다 — 28개 함수 라이브러리는 복잡하지만 수백~수천 개 API를 다루는 ToolLLM 같은 설정은 다루지 않는다.
(독자 관점) 훈련 샘플 수(100개 내외, ToolQA는 40개)가 충분한지에 대한 일반화 근거가 약하며, 샘플 수 민감도 실험이 제한적이다.
(독자 관점) ℓ, h, b 외의 하이퍼파라미터 민감도(예: Memory Bank top-k=5, timeout 임계값)에 대한 체계적 분석이 부재하다.
(독자 관점) LLM 호출 횟수, 토큰 비용 대비 성능 이득의 정량적 비교가 없어 비용 효율성을 다른 프롬프트 최적화 기법과 직접 비교하기 어렵다.
(독자 관점) AGENDA-HARD 같은 태스크에서 절대 성능이 4.17%로 여전히 낮아, 최적화 프레임워크가 모든 태스크 유형에 균일하게 작동하지는 않음을 시사한다.
(독자 관점) Actor와 Comparator에 동일한 강력한 LLM(GPT-4/Claude-3)을 사용하는데, 소형 모델에서도 대조적 추론이 효과적일지 불분명하다.

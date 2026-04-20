# Large Language Models Cannot Self-Correct Reasoning Yet

> **논문 정보**: Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou (Google DeepMind, UIUC)
> **arXiv**: 2310.01798 (2023.10, ICLR 2024)
> **코드**: N/A

---

## Problem

"Self-correction"은 LLM의 부정확성과 추론 오류를 교정하기 위한 유망한 후처리 기법으로 제시되어 왔다.
RCI, Reflexion, Self-Refine 등의 선행 연구는 자기 교정이 추론 성능을 크게 향상시킨다고 주장했다.
그러나 이러한 성능 향상이 모델의 내재적 교정 능력에서 비롯된 것인지, 아니면 외부 피드백(오라클 레이블, 도구 결과)에 의존한 것인지 불분명한 상태이다.
본 논문은 외부 피드백 없이 모델 자체 능력만으로 추론을 교정하는 "내재적 자기 교정(intrinsic self-correction)"의 실제 효과를 비판적으로 검증한다.
핵심 역설은 다음과 같다: LLM이 스스로 자기 응답의 오류를 식별하고 교정할 수 있다면, 왜 처음부터 올바른 답을 생성하지 않는가?
추론 태스크에서 오라클 레이블(정답 여부)을 사용하지 않고도 자기 교정이 실질적 성능 향상을 가져오는지가 본 연구의 중심 질문이다.
또한 multi-agent debate나 Self-Refine 같은 기존 방법들이 공정한 baseline과 비교되었는지도 함께 재검토되어야 한다.

---

## Motivation

선행 연구들(Kim et al., 2023; Shinn et al., 2023)이 GSM8K에서 약 7%, CommonSenseQA에서 약 15%의 성능 향상을 보고했으나, 이 결과들은 오라클 정답 레이블에 의존하여 "틀렸을 때만" 교정 루프를 종료하는 비현실적 설정에 기반한다.
실제 응용에서는 정답 레이블이 제공되지 않으므로, 이러한 설정은 자기 교정의 진정한 능력을 반영하지 못한다.
self-correction은 본질적으로 다수의 LLM 호출을 소비하므로, 공정한 비교를 위해서는 동일한 추론 비용을 가진 baseline(예: self-consistency)과 대조되어야 한다.
Multi-agent debate(Du et al., 2023)는 다수 에이전트 간 비판·토론을 통한 개선을 주장하지만, 동일 호출 수의 self-consistency와 공정 비교되지 않았다.
또한 Self-Refine(Madaan et al., 2023) 같은 연구는 초기 응답 프롬프트를 일부러 약하게 설계하고, 피드백 프롬프트에 핵심 제약 정보를 몰아넣어 개선 효과를 과대평가했을 가능성이 있다.
만약 초기 프롬프트에 동일한 제약을 명시하기만 해도 self-correction이 필요 없다면, 관찰된 개선은 자기 교정 능력이 아닌 프롬프트 설계 불균형에서 기인한 것이다.
이러한 문제들을 체계적으로 검증하지 않고서는 "LLM이 자기 교정을 할 수 있다"는 주장은 방법론적으로 지지될 수 없다.

---

## Method

1. **Intrinsic Self-Correction 정의**: 외부 피드백(오라클 레이블, 도구 실행 결과, 다른 모델의 평가) 없이 LLM이 자신의 초기 응답을 자체 내재 능력만으로 검토·수정하는 설정으로 정의한다.

2. **3단계 프롬프팅 프로토콜**: (1) 초기 응답 생성 (Standard Prompting 역할도 겸함) → (2) 모델에게 자신의 이전 응답을 검토하고 피드백을 생성하도록 지시 → (3) 피드백을 바탕으로 원 질문에 재응답하도록 지시한다.

3. **최대 2라운드 교정**: 각 모델에 대해 최대 2회의 self-correction 라운드를 적용하며, 라운드 1(3 calls)과 라운드 2(5 calls) 각각의 정확도를 기록한다.

4. **오라클 vs. 비오라클 대조 실험**: 동일 벤치마크·모델에서 (a) 정답 레이블로 교정 중단을 제어한 오라클 설정과 (b) 모델이 자체 판단으로 교정을 계속·중단하는 비오라클 설정을 병렬로 평가한다.

5. **다양한 피드백 프롬프트 실험**: "Assume this answer could be either correct or incorrect...", "Review your previous answer and determine whether it's correct...", "Verify whether your answer is correct..." 등 3종 이상의 피드백 프롬프트를 비교하여, 프롬프트 선택이 결과를 뒤집는지 확인한다.

6. **Multi-Agent Debate 재실험**: Du et al. (2023)의 원 프롬프트를 그대로 사용하여 gpt-3.5-turbo-0301에 3 agents × 2 rounds debate를 적용하고, 전체 GSM8K 테스트셋(1,319 문제)에서 self-consistency와 동일 응답 수(3, 6, 9)로 공정 비교한다.

7. **Self-Refine 재실험 (Constrained Generation)**: Madaan et al. (2023)의 CommonGen-Hard 태스크에서, 원 프롬프트에 "Write a reasonable paragraph that includes *ALL* of the above concepts" 제약을 추가한 강화 프롬프트(Standard Prompting (ours))를 설계하고 self-correction 없이도 더 높은 coverage를 달성하는지 검증한다.

8. **답변 변화 분류 분석**: 두 라운드 교정 후 각 샘플의 결과를 No Change / Correct⇒Incorrect / Incorrect⇒Correct / Incorrect⇒Incorrect 4개 범주로 분류하여 교정 방향의 편향을 정량화한다.

9. **모델 다양화**: GPT-3.5-Turbo(gpt-3.5-turbo-0613), GPT-4(2023/08/29 접속), GPT-4-Turbo(gpt-4-1106-preview), Llama-2-70b-chat의 4개 모델로 교차 검증하며, GPT-3.5/GPT-4는 temperature 1, GPT-4-Turbo/Llama-2는 temperature 0으로 설정하여 디코딩 알고리즘 간 차이를 포착한다.

---

## Key Contribution

1. **내재적 자기 교정 성능 하락의 실증**: 외부 피드백 없이 프롬프트만으로 자기 교정을 수행하면 GPT-3.5, GPT-4, GPT-4-Turbo, Llama-2 모든 모델에서, GSM8K·CommonSenseQA·HotpotQA 모든 벤치마크에서 정확도가 일관되게 하락함을 보여주었다.

2. **오라클 레이블 의존성 폭로**: RCI와 Reflexion의 성능 향상이 오라클 정답에 기반한 루프 종료 조건에서 비롯된 것이며, 오라클을 제거하면 개선이 소멸 또는 역전됨을 체계적으로 입증하였다.

3. **Multi-Agent Debate의 본질 재해석**: multi-agent debate가 "debate"나 "critique"가 아닌 사실상 self-consistency의 일종이며, 동일 호출 수의 simple majority voting에 오히려 열세임을 수치(GSM8K 6 calls: 83.2% vs 85.3%, 9 calls: 83.0% vs 88.2%)로 증명하였다.

4. **프롬프트 설계 불균형 문제 제기**: Self-Refine의 개선 주장이 초기 프롬프트에 정보가 빠져 있고 피드백 프롬프트에만 완전한 지시가 포함된 불균형에서 기인했음을 CommonGen-Hard 재실험(강화 Standard 81.8% vs 원본 Self-Correct 67.0%)으로 입증하였다.

5. **후속 연구를 위한 가이드라인 제시**: (a) 외부 피드백 활용(코드 실행기, verifier, 도구 등)의 중요성, (b) self-consistency 같은 동일 비용 baseline과의 비교 필수, (c) 초기·교정 프롬프트 설계의 동등한 노력 투입이라는 3대 원칙을 자기 교정 연구의 평가 기준으로 정립하였다.

6. **응답 변화의 편향 특성 규명**: GPT-3.5가 교정을 수행할 때 Correct⇒Incorrect(8.8%)가 Incorrect⇒Correct(7.6%)보다 빈번하고, CommonSenseQA에서는 그 격차가 Correct⇒Incorrect 39.8% vs Incorrect⇒Correct 11.6%로 극단적임을 드러내어, LLM이 자신의 추론 정확성을 적절히 판단하지 못함을 직접적으로 증거하였다.

---

## Experiment & Results

- **데이터셋**: GSM8K(1,319 문제, 수학), CommonSenseQA(1,221 문제 dev set, 다지선다 상식 추론), HotpotQA(100 문제, open-domain multi-hop QA, exact match).
- **모델**: GPT-3.5-Turbo, GPT-4, GPT-4-Turbo(GSM8K/CommonSenseQA 각 200 샘플링), Llama-2-70b-chat(200 샘플링).

**오라클 레이블 사용 시 (Table 2, 기존 연구 재현)**:
- GPT-3.5 GSM8K: 75.9% → 84.3% (+8.4%p)
- GPT-3.5 CommonSenseQA: 75.8% → 89.7% (+13.9%p)
- GPT-3.5 HotpotQA: 26.0% → 29.0% (+3.0%p)
- GPT-4 GSM8K: 95.5% → 97.5%, GPT-4 CommonSenseQA: 82.0% → 85.5%, GPT-4 HotpotQA: 49.0% → 59.0%
- 그러나 오라클은 "정답이면 교정 중단"이므로 실세계 비적용 설정.

**Intrinsic Self-Correction (Table 3, 오라클 제거)**:
- GPT-3.5 GSM8K: 75.9% → 75.1%(R1) → 74.7%(R2), **-1.2%p**
- GPT-3.5 CommonSenseQA: 75.8% → 38.1%(R1) → 41.8%(R2), **-34.0%p** (극적 하락)
- GPT-3.5 HotpotQA: 26.0% → 25.0% → 25.0%
- GPT-4 GSM8K: 95.5% → 91.5% → 89.0%, **-6.5%p**
- GPT-4 CommonSenseQA: 82.0% → 79.5% → 80.0%
- GPT-4 HotpotQA: 49.0% → 49.0% → 43.0%, **-6.0%p**

**GPT-4-Turbo / Llama-2 (Table 4)**:
- GPT-4-Turbo GSM8K: 91.5% → 88.0% → 90.0%; CommonSenseQA: 84.0% → 81.5% → 83.0%.
- Llama-2 GSM8K: 62.0% → 43.5% → 36.5% (**-25.5%p**); CommonSenseQA: 64.0% → 37.5% → 36.5% (**-27.5%p**).
- 피드백 프롬프트 3종 전수 실험(Tables 5, 6): 프롬프트와 무관하게 대부분 하락, 예: Llama-2 GSM8K "Verify..." 프롬프트 62.0% → 58.0% → 41.5%.

**Multi-Agent Debate vs Self-Consistency (Table 7, GSM8K)**:
- Standard 1 call: 76.7%
- Debate R1 (6 responses): 83.2% vs Self-Consistency 6: **85.3%**
- Debate R2 (9 responses): 83.0% vs Self-Consistency 9: **88.2%**
- 동일 호출 수에서 self-consistency 우세 → debate의 개선은 consistency 효과.

**Self-Refine 재검증 (Table 8, CommonGen-Hard)**:
- 원논문 Standard 44.0% → Self-Correct 67.0%
- 저자 재현 Standard 53.0% → Self-Correct 61.1%
- **"ALL concepts 포함하라" 추가한 Standard Prompting (ours): 81.8%**, 이후 self-correct 적용 시 오히려 75.1%로 감소.

**답변 변화 분류(Figure 1)**:
- GSM8K GPT-3.5: No Change 74.7%, C⇒I 8.8%, I⇒C 7.6%, I⇒I 8.9% → 교정이 해로운 방향 우세.
- CommonSenseQA GPT-3.5: No Change 42.8%, C⇒I 39.8%, I⇒C 11.6% → 오답 선택지의 표면적 관련성으로 모델이 오답으로 유도됨.
- GPT-4/GPT-4-Turbo는 No Change 비율이 90% 이상으로 높아, 교정 프롬프트가 주는 편향에 더 강건.
- Llama-2 GSM8K: No Change 40.0%, C⇒I 23.5%로 편향 심각.

**질적 예시(Figures 3, 4)**: GPT-3.5가 초기 정답 $75.00(yogurt 문제)을 리뷰 단계에서 잘못 "수정"하여 $37.50(오답)으로 변경하는 실패 케이스와, 초기 오답 $18(gift bag)을 정답 $24로 수정하는 성공 케이스가 공존하나 통계적으로는 실패 쪽이 우세.

---

## Limitation

저자가 명시한 한계는 본 분석이 추론 태스크(수학, 상식 QA, multi-hop QA)에 한정된다는 점이며, 스타일 변경이나 안전성 정렬 같은 다른 도메인에서는 자기 교정이 효과적일 수 있다고 인정하고 있다.
HotpotQA 샘플이 100개로 작아 통계적 신뢰성이 낮으며, 이 때문에 답변 변화 분류 분석에서 제외되었다.
GPT-4-Turbo와 Llama-2는 각 벤치마크에서 200문제만 샘플링했으므로 전수 평가 대비 variance가 존재한다.
독자 관점의 한계로는, 본 실험이 2023년 8~11월 당시 모델(GPT-3.5-turbo-0613, GPT-4 2023/08/29, GPT-4-1106-preview)을 기준으로 하므로, o1·o3 같은 추론 특화 모델이나 최신 Chain-of-Verification 기법에서의 유효성은 재검증이 필요하다.
외부 피드백의 범주(코드 실행기, verifier, 검색 도구, human-in-the-loop 등)에 대한 체계적 taxonomy 제공이 부족하여, 어떤 유형의 외부 피드백이 어떤 도메인에서 가장 효과적인지에 대한 실무적 가이드가 아직 제시되지 않았다.
제안된 "동등한 노력의 프롬프트 설계" 원칙은 방향은 옳지만, 초기 프롬프트와 피드백 프롬프트의 정보량을 정량적으로 비교할 표준 메트릭이 없어 실천 기준이 모호하다.
마지막으로, self-consistency가 debate보다 우세하다는 결과가 GSM8K 외 다른 태스크(특히 생성형 open-ended 태스크)에도 일반화되는지는 별도 검증이 필요하다.

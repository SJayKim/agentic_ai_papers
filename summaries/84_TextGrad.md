# 84. TextGrad: Automatic "Differentiation" via Text

> 📄 **저자**: Mert Yuksekgonul, Federico Bianchi, Joseph Boen, Sheng Liu, Zhi Huang, Carlos Guestrin, James Zou
> 📚 **학회/발표 기관**: Nature 2025 (preprint arXiv 2024.06)
> 📅 **발표 날짜**: 2024.06
> 🔗 **arXiv**: https://arxiv.org/abs/2406.07496
> 💻 **코드**: https://github.com/zou-group/textgrad

---

## Problem

최근의 AI 시스템은 단일 모델 학습에서 벗어나, 여러 LLM과 도구(검색 엔진, 코드 인터프리터, 시뮬레이터, 수치 솔버)가 협업하는 compound AI system 형태로 진화하고 있다.
이런 시스템에서 어떤 component(프롬프트, 코드, 분자 구조, 가중치)를 어떻게 수정해야 성능이 개선되는지 결정하는 것이 핵심 병목이다.
기존 prompt optimization 기법(OPRO, EvoPrompt 등)은 단일 scalar reward나 accuracy 점수만을 신호로 사용하기 때문에 "왜 틀렸는지", "무엇을 바꿔야 하는지"에 대한 정보가 빈약하다.
ProTeGi[25]가 prompt에 대한 textual feedback이라는 아이디어를 도입했지만 단일 변수(prompt)에 국한되었고, DSPy[10]는 demonstration 선택과 BFS 기반 탐색을 다루지만 instance(코드, 분자 같은 답 자체)의 최적화는 지원하지 않는다.
백색상자 prompt-tuning 기법은 closed-source 모델(GPT-4o 등)에서는 사용할 수 없다.
결과적으로 다단계 LLM 그래프에서 chain-rule처럼 신호를 상류로 전파해 각 변수를 국소적으로 업데이트할 수 있는, 영역-독립적이고 일반적인 최적화 프레임워크가 부재하다.

---

## Motivation

신경망의 폭발적 발전은 backpropagation과 자동 미분 프레임워크(PyTorch, TensorFlow)가 "어떤 그래프든 손실에 대한 각 파라미터의 그래디언트를 자동으로 계산해준다"는 turn-key 도구를 제공한 데서 비롯됐다.
저자들은 compound LLM 시스템도 동일한 패러다임 전환이 필요하다고 본다 — 변수, forward, backward, optimizer 추상화를 그대로 가져오되, 수치 그래디언트 자리에 LLM이 생성하는 "비판/제안 텍스트"를 대입하자는 것이다.
핵심 직관은 LLM이 임의 도메인(코드, 분자 SMILES, 치료 계획 하이퍼파라미터, 프롬프트)에 대해 "이 답의 결함은 X이고, Y처럼 바꾸면 좋다"라는 자연어 비판을 제공할 수 있다는 관찰이다.
이 비판은 scalar reward보다 정보량이 압도적으로 많고, 변수가 어떤 문맥에서 사용되었는지까지 반영하기 때문에 다단계 시스템에서도 책임 할당(credit assignment)이 자연스럽게 이루어진다.
PyTorch와 동일한 syntax(Variable, BlackboxLLM, TextLoss, TGD optimizer, loss.backward(), optimizer.step())를 채택하면 ML 커뮤니티의 지식이 즉시 이식되어 사용성이 극대화된다.

---

## Method

TEXTGRAD는 LLM 시스템을 변수와 함수의 계산 그래프로 보고, "textual gradient"를 backprop하여 각 변수를 최적화하는 프레임워크다.

1. **계산 그래프 구성 (Forward Pass)**
   - 각 변수 v는 LLM 호출, 도구 호출, 시뮬레이터 등 임의 함수 f_v의 출력으로 정의: v = f_v(PredecessorsOf(v)).
   - 변수 값은 비정형 데이터(자연어 텍스트, 코드 스니펫, SMILES 문자열, 이미지 등) 모두 가능.
   - Forward pass에서 시스템 출력과 함께 손실 변수 L을 계산.

2. **손실 함수 (Loss)**
   - L은 미분 불가능한 함수일 수 있음 — LLM 평가자, 코드 인터프리터의 유닛 테스트 결과, AutoDock Vina docking 점수, matRad 수치 솔버 출력 등.
   - `tg.TextLoss("Rate the summary.")`처럼 자연어 평가 지시로 정의하거나, 외부 도구의 수치 출력을 텍스트로 표현.

3. **Backward Pass — ∇LLM 그래디언트 연산자**
   - 각 edge에 대해 LLM-as-grad operator가 호출되어 자연어 비판을 생성: `∂L/∂x = ∇LLM(x, y, ∂L/∂y)`.
   - 구체적으로 LLM에 "{x|y} 대화, {y}에 대한 비판 ∂L/∂y가 주어졌을 때 {x}를 어떻게 개선할지 설명하라"는 프롬프트를 던져 비판 텍스트를 회수.
   - 변수 v가 여러 successor에서 사용되었으면, 각 문맥의 비판을 모두 모아 union으로 집계 (식 11). 이는 다중 경로의 그래디언트를 더하는 backprop와 정확히 대응.

4. **변수 업데이트 — TGD (Textual Gradient Descent)**
   - 옵티마이저는 현재 변수와 textual gradient를 LLM에 입력하여 새 값을 생성: `x_new = LLM("Below are criticisms on {x}: ∂L/∂x. Incorporate and produce a new variable.")`.
   - 식 7의 `θ - η·∂L/∂θ`에 대응. 도메인 비의존적이며 모든 변수 타입에 동일 operator 사용.

5. **PyTorch-style API 추상화**
   - Variable, BlackboxLLM(모델), TextLoss(손실), TextualGradientDescent(옵티마이저)가 PyTorch의 Tensor, ResNet50, CrossEntropyLoss, SGD에 정확히 매핑.
   - 사용자는 `loss.backward(); optimizer.step()` 만 호출하면 됨.

6. **두 가지 최적화 모드**
   - **Instance optimization**: 답 자체(코드, 분자, 치료 계획)를 변수로 두고 test-time에 단일 인스턴스를 정제.
   - **Prompt optimization**: 시스템 프롬프트를 변수로 두고 mini-batch SGD로 학습 — 12 iteration × batch size 3 등.

7. **고급 최적화 기법**: tg.sum으로 mini-batch 손실 합산(addition 노드처럼 그래디언트 분배), natural language 제약조건(constrained opt), momentum(이전 iteration 값을 context에 포함). n edge 그래프에서 1회 iteration당 최대 n번의 LLM 호출.

---

## Key Contribution

1. **자동 미분 메타포의 일반화**: ProTeGi의 textual gradient를 단일 프롬프트에서 임의 계산 그래프(코드, 분자, 하이퍼파라미터 등 비정형 변수 포함)로 확장한 최초의 프레임워크.
2. **PyTorch와 동형의 API**: Variable / BlackboxLLM / TextLoss / TGD 추상화로 ML 엔지니어 진입 장벽을 제거 — 사용자는 objective만 정의하면 됨.
3. **Instance vs. Prompt 통합**: 같은 엔진이 test-time에 답을 직접 다듬는 instance optimization과, 학습 데이터로 프롬프트를 학습하는 prompt optimization을 모두 지원.
4. **도메인 일반성 입증**: 코딩, PhD-level QA, 산수 추론, 신약 분자 설계, 방사선 치료 계획 등 5개 이질적 도메인에서 단일 프레임워크가 SOTA 달성.
5. **오픈소스**: github.com/zou-group/textgrad로 공개되어 후속 연구의 토대 제공.

---

## Experiment & Results

저자들은 5개 도메인에서 zero-shot 설정으로 TEXTGRAD를 검증했으며, 모든 도메인에서 baseline 대비 명확한 향상을 보였다.

1. **LeetCode Hard 코드 최적화 (gpt-4o)**: zero-shot 26%, Reflexion(1-shot, 5 iter) 31% ±0.012 → **TEXTGRAD(0-shot, 5 iter) 36% ±0.018** (Completion Rate, 5 seed 평균). 상대 +20% 성능 향상. 참고로 GPT-4 zero-shot은 7%, GPT-4 + Reflexion은 15%로 모델 자체 업그레이드와 결합 시 더욱 향상.

2. **GPQA (Google-Proof QA, gpt-4o, 3-iter test-time 정제 + majority voting)**: CoT 51.0% → **55.0%** (저자 발표 기준 SOTA, 이전 best 53.6% 대비 +1.4pp). 전문가 정답률 81%, 비전문가 22%인 PhD 수준 벤치마크.

3. **MMLU 어려운 서브셋 (gpt-4o)**: Machine Learning 85.7% → **88.4%** (+2.7pp), College Physics 91.2% → **95.1%** (+3.9pp).

4. **Big-Bench Hard + GSM8k 프롬프트 최적화 (gpt-3.5-turbo-0125 forward, gpt-4o gradient engine, batch 3 × 12 iter = 36 sample)**: Object Counting CoT 77.8% / DSPy(BFSR, 8-shot) 84.9% → **TEXTGRAD(0-shot) 91.9%** (DSPy 대비 +7pp). Word Sorting CoT 76.7% / DSPy 79.8% → TEXTGRAD 79.8% (동률). GSM8k CoT 72.9% / DSPy 81.1% → TEXTGRAD 81.1% (동률, 그러나 8-shot 비용 없음). DSPy demo + TEXTGRAD 프롬프트 결합 시 GSM8k 82.1%까지 상승.

5. **분자 최적화 (DOCKSTRING 58 단백질 타깃, 3 fragment × 10 iter)**: SMILES를 변수로, Vina docking score와 QED druglikeness를 multi-objective loss로. 임상 승인 약물이 존재하는 29 타깃에서 Vina/QED 모두 임상 약물과 경쟁 가능한 분자를 생성 — 예: PPARA 타깃에서 Vina -4.2 → -7.5 kcal/mol, QED 0.44 → 0.79. 사전 학습 데이터 없이 SOTA-급 결과 + 의사결정의 자연어 설명 가능.

6. **방사선 치료 계획 (5명 전립선암 환자, matRad 솔버, gpt-4o)**: PTV/방광/직장/대퇴골/체부 가중치를 변수로 outer-loop 최적화. PTV 평균 dose, D95 모두 임상의가 만든 계획을 능가, OAR(방광·직장) 평균 dose도 더 낮음(예: 방광 22.39 → 17.18 Gy).

---

## Limitation

저자들은 본 연구가 "첫걸음"임을 명시하며 몇 가지 한계를 밝힌다.
첫째, 분자 설계와 치료 계획은 in silico 검증(Vina, matRad)에 그쳤고 실제 실험·임상 검증은 범위 밖이므로, 실제 약효·환자 결과는 알 수 없다 — 이는 시뮬레이터 한계(docking score는 실제 binding과 상관관계가 제한적)와 결합되어 결과 신뢰도를 제한한다.
둘째, 본 프레임워크의 forward/backward 호출이 LLM-call 그래프 edge 수에 비례하므로, 큰 그래프(다단계 RAG, tool use)로 확장 시 호출 비용이 빠르게 증가하며 저자도 RAG·tool-use 통합을 future work로 남겼다.
셋째, 자연어 그래디언트의 분산이 수치 그래디언트보다 크고, momentum/배치 외에 variance reduction이나 adaptive gradient에 해당하는 안정화 기법이 아직 미흡 — Word Sorting/GSM8k에서 DSPy 대비 추가 향상이 없는 점이 이를 시사한다.
넷째 (독자 관점), 그래디언트 생성·업데이트 모두 강한 LLM(gpt-4o)을 사용하므로 약한 모델에서는 비판 품질이 떨어져 발산하거나 진동할 위험이 있고, 평가도 동일 LLM 계열로 이루어져 자기 평가 편향 가능성이 있다.
다섯째 (독자 관점), constraint를 자연어로 명시하는 방식은 instruction-tuned 모델의 따르기 능력에 의존해 제약이 늘어나면 신뢰성이 떨어진다는 점을 저자도 인정하고 있어, 안전성이 중요한 도메인(의료, 약학)에서 production 적용은 추가 검증이 필요하다.

# 82. DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

> 📄 **저자**: Omar Khattab, Arnav Singhvi, Paridhi Maheshwari, Zhiyuan Zhang, Keshav Santhanam, Sri Vardhamanan, Saiful Haq, Ashutosh Sharma, Thomas T. Joshi, Hanna Moazam, Heather Miller, Matei Zaharia, Christopher Potts
> 📚 **학회/발표 기관**: ICLR 2024
> 📅 **발표 날짜**: 2023.10
> 🔗 **arXiv**: https://arxiv.org/abs/2310.03714
> 💻 **코드**: https://github.com/stanfordnlp/dspy

---

## Problem

LLM 파이프라인을 구축하는 현재의 표준 관행은 hand-crafted "prompt template" — 즉 수동 시행착오를 거쳐 발견된 긴 instruction과 demonstration 문자열을 직접 작성하는 것이다.
이러한 방식은 fragile하고 비확장적이며, 마치 분류기의 weight를 수동으로 튜닝하는 것과 개념적으로 동등하다.
하나의 prompt 문자열은 다른 LLM, 다른 데이터 도메인, 다른 파이프라인 단계, 심지어 동일 태스크의 다른 입력에 대해서도 일반화되지 않는다.
LangChain, LlamaIndex, Semantic Kernel 같은 인기 프레임워크 역시 hand-written prompt template으로 task-specific 동작을 표현하기 때문에 동일한 prompt engineering 부담을 그대로 떠안고 있다.
다단계(multi-stage) 파이프라인에서는 여러 LLM 호출이 서로 효과적으로 상호작용해야 하므로, 단일 prompt의 fragility가 단계마다 누적되어 시스템 전체의 신뢰성이 더욱 악화된다.
또한 prompt 최적화 연구(APE, OPRO 등)는 대부분 단일 LLM 호출에 국한되어 있어, 임의의 다단계 파이프라인에 일반화되는 통합 최적화 프레임워크가 부재하다.
결과적으로 새로운 태스크나 새로운 LLM으로 옮길 때마다 막대한 수동 prompt engineering이 필요하며, 작은 모델로 큰 모델을 대체하는 효율화 시도도 prompt가 모델에 강하게 결합되어 있어 어렵다.

---

## Motivation

저자들은 deep learning에서 Torch/Theano/PyTorch가 가져왔던 추상화 혁명 — 즉 (1) 범용 layer를 모듈로 조합하고 (2) weight를 손으로 튜닝하지 않고 optimizer로 학습한다 — 을 LLM 파이프라인에도 동일하게 적용할 수 있다고 본다.
핵심 직관은 prompt 문자열을 직접 다루는 대신, **모듈 간 통신을 자연어 시그니처(natural-language signature)로 추상화하고, prompt 자체는 컴파일러가 자동 생성/최적화**하도록 하는 것이다.
PyTorch에서 `Linear(in_features, out_features)`라는 선언만으로 weight 초기화·forward·backward가 자동화되듯, DSPy에서는 `dspy.Predict("question -> answer")`라는 선언만으로 prompt 구성·few-shot demo 선택·파싱이 자동화된다.
또한 LLM은 그 자체로 매우 불안정한 호출 단위지만, 잘 분해된 다단계 프로그램에서는 LLM 스스로 "올바른 다단계 trace를 생성할 수 있는 입력 케이스"를 충분히 찾아낼 수 있다는 관찰을 활용한다.
즉 metric을 통과한 trace를 자동 수집(bootstrapping)하면, 인간이 직접 작성한 demonstration 없이도 파이프라인 각 단계의 우수한 few-shot 예제를 얻을 수 있다.
이로써 prompt engineering이라는 "예술"을 모듈 + 옵티마이저로 구성된 체계적 프로그래밍 패러다임으로 전환할 수 있다는 것이 DSPy의 핵심 주장이다.

---

## Method

DSPy 프로그래밍 모델은 세 가지 핵심 추상화 — Signature, Module, Teleprompter — 위에 구축된다.

1. **Signature (자연어 타입 선언)**
   - 함수의 입출력 필드를 자연어로 선언한다. 예: `"question -> answer"`, `"context, question -> answer"`, `"english document -> french translation"`.
   - field 이름이 곧 LLM에게 전달될 의미적 역할이 되며, DSPy 컴파일러는 in-context learning을 통해 각 필드를 다르게 해석한다.
   - 자유 형식 prompt 문자열 대신 함수 시그니처로 표현되므로, 같은 시그니처를 다른 LLM·다른 prompt 전략으로 재컴파일 가능하다.

2. **Module (Parameterized 프롬프트 전략)**
   - `Predict`: 가장 기본. 시그니처·선택적 LLM·demonstration 리스트를 내부에 저장하고, 호출 시 prompt를 조립·LLM 호출·출력 파싱을 수행한다. compile 모드에서는 input/output trace를 추적해 teleprompter에 제공한다.
   - `ChainOfThought`: 시그니처에 `rationale` 필드를 자동 prepend하여 "Reasoning: Let's think step by step." 형태의 추론을 유도한다. 단 몇 줄의 코드로 구현됨.
   - `ReAct`, `ProgramOfThought`, `MultiChainComparison` 등도 동일 패턴으로 임의의 시그니처에 일반화된다.
   - `dspy.Retrieve` 모듈은 ColBERTv2/Pyserini/Pinecone 같은 retriever를 도구로 호출한다.
   - 모듈은 PyTorch처럼 `__init__`에서 선언 후 `forward` 메서드에서 임의의 Python 제어 흐름(if/for/exception)으로 조합되는 define-by-run 그래프를 형성한다.

3. **Teleprompter (컴파일러 / 옵티마이저)**
   - 입력: DSPy 프로그램 + 소량의 training input (라벨은 최종 출력에만 선택적으로 필요) + validation metric.
   - **3-stage 컴파일**:
     - **Stage 1 — Candidate Generation**: 프로그램 내 모든 `Predict` 모듈을 재귀적으로 찾고, 각 predictor에 대한 instruction/demonstration 후보를 생성한다.
     - **Stage 2 — Parameter Optimization**: random search, Tree-structured Parzen Estimators(HyperOpt/Optuna), 또는 finetuning으로 최적 후보를 선택한다.
     - **Stage 3 — Higher-Order Optimization**: ensemble, majority voting 등 제어 흐름 자체를 수정한다.

4. **BootstrapFewShot의 동작 방식 (핵심)**
   - teacher 프로그램(미지정 시 zero-shot 버전)을 training input에 대해 시뮬레이션 실행한다. 고온(high temperature) 샘플링으로 여러 번 실행 가능.
   - compile 모드에서 thread-safe하게 **다단계 trace**(각 모듈의 input/output 쌍 시퀀스)를 추적한다.
   - **metric을 통과한 trace만 demo로 채택**하고 실패한 trace는 폐기한다(rejection sampling 유사). 통과한 trace에서 각 시그니처에 대응되는 (input, output) 쌍을 demo로 추출.
   - 이 demo들이 컴파일된 프로그램의 각 모듈에 few-shot prompt로 주입되어 self-improving 파이프라인이 완성된다.
   - 확장형으로 `BootstrapFewShotWithRandomSearch`는 어떤 demo 부분집합을 사용할지를 random search로 최적화하고, `BootstrapFinetune`은 demo로 small LLM의 weight를 직접 finetune한다.
   - teacher composition도 지원되어, 큰 LLM(Llama2-13b)으로 컴파일된 RAG 프로그램을 teacher로 두고 Flan-T5-large로 더 저렴한 student 프로그램을 finetune 가능하다.

---

## Key Contribution

1. **선언적 모듈 추상화의 최초 제안**: prompt 문자열 조작을 자연어 시그니처와 parameterized 모듈로 대체하는 LLM 프로그래밍 모델을 처음으로 정식화하여, "foundation model programming"의 PyTorch 격을 제공한다.
2. **임의 파이프라인을 위한 범용 컴파일러**: Teleprompter라는 일반 최적화 인터페이스를 통해 단일 LLM 호출 prompt 최적화 연구를 **다단계 임의 파이프라인**으로 일반화했다.
3. **BootstrapFewShot 알고리즘**: metric을 통과한 다단계 trace에서 demonstration을 자동 수집하는 self-bootstrapping 메커니즘으로, 중간 단계 라벨이 없는 상황에서도 multi-stage 파이프라인을 자가 개선시킨다.
4. **소형 모델 경쟁력 입증**: hand-crafted prompt 없이도 Llama2-13b-chat과 T5-Large(770M)가 GPT-3.5 expert prompt 기반 시스템과 경쟁 가능함을 실증하여, 모델 의존도를 낮추는 실용적 경로를 제시했다.

---

## Experiment & Results

**Case Study 1 — GSM8K (math word problems)**
- 데이터: 공식 trainset에서 200/300 샘플(train/dev), 공식 test 1.3k 사용. 최종 숫자값 매칭으로 정확도 평가.
- 프로그램: `vanilla`(Predict), `CoT`(ChainOfThought), `reflection`(ThoughtReflection — 5개 reasoning chain 샘플링 후 MultiChainComparison으로 비교).
- baseline: zero-shot, `LabeledFewShot`(k=8 무작위 demo), expert human CoT.
- 핵심 수치(GPT-3.5 dev): `vanilla` zero-shot 24.0% → `vanilla + bootstrap×2` 64.7% → `CoT + bootstrap + ensemble` **88.3%** (test 81.6%). `CoT + humanCoT` 78.6% 대비 bootstrap이 80.3%로 인간 작성 reasoning을 초과.
- Llama2-13b-chat dev: `vanilla` 7.0% → `reflection + bootstrap + ensemble` **49.0%** (test 46.9%). 13b 모델이 Touvron et al.의 34b 모델 결과(42.2%)를 hand-crafted CoT 없이 능가.
- 컴파일된 모듈은 LLM별로 4–20% → 49–88% 범위의 향상을 가져옴.

**Case Study 2 — HotPotQA (multi-hop QA, fullwiki)**
- 데이터: 200/300 train/dev (hard 라벨만), 1000 test. ColBERTv2 retriever 사용. Answer EM과 Passage retrieval accuracy 측정.
- 프로그램: `vanilla`, `CoTRAG`(RAG with CoT), `react`(dspy.ReAct + Retrieve), `multihop`(BasicMultiHop — 2 hop, generate_query → retrieve 반복).
- 핵심 수치(GPT-3.5 dev): `vanilla fewshot` 34.3 → `multihop bootstrap` 48.7 (Psg 47.0) → `multihop ensemble` **54.7** (test 45.6, Psg 43.8).
- Llama2-13b-chat dev: `vanilla fewshot` 27.5 → `multihop ensemble` **50.0** (test 41.0). 13b 모델이 GPT-3.5 multihop bootstrap(48.7)을 초과.
- `react`에서 bootstrap×2가 39.0%로 expert human reasoning(+human_r, 33.0%)을 +6%p 초과.
- **finetuning**: BootstrapFinetune으로 multihop을 T5-Large(770M)로 컴파일 → 답변 EM **39.3%**, passage acc **46.0%** (200 labeled + 800 unlabeled). GPT-3.5 대비 inference 비용이 자릿수 단위로 저렴.

전반적으로 hand-crafted prompt 대비 GPT-3.5는 일반적으로 +25% 이상, Llama2-13b-chat은 +65% 이상의 개선, expert demonstration 대비 각각 +5–46%, +16–40%의 개선을 달성.

---

## Limitation

저자가 명시한 한계로는, 본 논문이 두 개 case study(GSM8K, HotPotQA)에 집중되어 있어 정보 추출·합성 데이터 생성 등 다른 태스크에서의 통제된 평가는 후속 작업으로 미뤘다는 점이 있다.
독자 관점에서 추가로, BootstrapFewShot은 zero-shot 프로그램이 training input의 일부에서라도 metric을 통과해야 demo를 수집할 수 있는데, 매우 어려운 태스크에서 zero-shot 정확도가 0에 가까우면 bootstrap이 거의 무의미해진다.
컴파일은 수 분~수십 분이 소요되며 수천 번의 LLM 호출을 요구하므로, 큰 validation set이나 expensive teacher 모델 사용 시 API 비용이 상당히 발생할 수 있다.
metric을 직접 정의해야 하므로 EM/F1처럼 자동화하기 쉬운 태스크 외에는 metric 설계 자체가 prompt engineering을 다른 형태로 옮긴 것에 불과할 수 있다.
또한 본 논문 시점의 DSPy는 demonstration 최적화에 집중하며 instruction text 자체의 자동 최적화는 부수적으로만 다뤄, 후속 MIPRO 등에서 다시 본격적으로 해결되었다.
프로그램 구조(어떤 모듈을 어떻게 조합할지) 자체는 여전히 개발자의 설계에 의존하며, 자동 architecture search는 제공되지 않는다.
실제 적용 시 이는 "프롬프트 작성"이 "모듈 조합 + metric 설계"라는 새로운 종류의 엔지니어링으로 이동했음을 의미하며, 진입 장벽이 완전히 사라지지는 않는다.

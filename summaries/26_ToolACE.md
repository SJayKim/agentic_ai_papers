# ToolACE: Winning the Points of LLM Function Calling

> **논문 정보**: Weiwen Liu, Xu Huang, Xingshan Zeng 외 다수 (Huawei Noah's Ark Lab, SJTU, USTC, Tsinghua, CUHK)
> **arXiv**: ICLR 2025 (arXiv:2409.00920v2, 25 Jul 2025)
> **코드/모델**: https://huggingface.co/Team-ACE

---

## Problem

LLM의 function calling 능력을 확장하려면 정확하고 다양하며 복잡한 학습 데이터가 필수적이다.
그러나 실세계 function-calling 데이터를 수집하고 주석하는 일은 비용과 난이도가 매우 높다.
기존 합성 데이터 파이프라인(Gorilla 1,645 API, ToolLLM 16,464 API, xLAM 3,673 API 등)은 API 커버리지가 좁고 도메인 수가 제한적(3~50개 수준)이다.
또한 이들은 단일 턴 단순 호출에 편향되어 있어, 병렬(parallel)·의존적(dependent)·다중 턴(multi-turn)·중첩 파라미터(nested) 같은 복잡 시나리오를 충분히 다루지 못한다.
실제 API는 빈번히 업데이트되므로 zero-shot 일반화가 필수이지만, 기존 데이터는 이러한 요구를 충족하기 어렵다.
파라미터 포맷·타입·제약 조건의 엄격한 일치가 요구됨에도, 단순 파이프라인으로 생성된 데이터는 정확성 검증이 부실하다.
결과적으로 오픈소스 function-calling 모델은 GPT-4 계열 API-based 모델과 큰 성능 격차를 보인다.
특히 모델 크기에 맞춘 복잡도 조절이 없어, 0.5B 모델은 어려워하고 70B 모델은 지나치게 쉬운 데이터를 학습하는 비효율이 발생한다.

---

## Motivation

실세계 function calling은 다양한 API 도메인, 중첩 파라미터, 병렬/의존적 호출, 멀티턴 대화 등 복잡한 패턴을 포함한다.
따라서 데이터 합성 파이프라인은 단순 단일 턴을 넘어 포괄적인 유형을 커버해야 한다.
사전학습 코퍼스는 인간 지식의 가장 다양한 집합이므로, 여기서 API 도메인과 기능을 추출하면 광범위한 커버리지를 얻을 수 있다.
Du et al. (2023)의 연구에 따르면 LLM은 자신의 현재 능력을 "약간 상회"하는 복잡도의 데이터로부터 가장 효과적으로 학습한다.
따라서 모델이 스스로 자신에게 적합한 난이도를 평가·조정할 수 있는 self-guided 메커니즘이 필요하다.
function calling은 일반 QA와 달리 API 정의와의 형식 일치 여부로 검증 가능하므로, 규칙 기반 자동 검증이 강력히 작동할 수 있다.
동시에 규칙으로 잡지 못하는 hallucination·의미적 일관성은 LLM 기반 검증으로 보완해야 한다.
이러한 세 축(다양성·복잡도·정확성)을 통합하면 8B 규모의 오픈소스 모델로도 GPT-4급 function calling을 달성할 수 있다는 가설을 세울 수 있다.

---

## Method

ToolACE는 Tool Self-Evolution Synthesis (TSS), Self-Guided Dialog Generation (SDG), Dual-Layer Validation (DLV)의 3모듈로 구성된 자동화 데이터 합성 파이프라인이다.

1. **TSS – Speciation 단계**: 사전학습 코퍼스의 API 관련 문서(기술 매뉴얼, API 문서, 제품 사양서, 사용자 가이드, 튜토리얼)에서 frontier LLM 에이전트가 도메인과 기능을 추출하여 계층적 API Context Tree를 구축한다.
2. **TSS – Adaptation 단계**: 구축된 컨텍스트 트리에서 서브트리를 샘플링해 각 API의 도메인·다양성 수준을 지정하며, 많은 노드를 커버하는 API는 도메인 특화 기능, 단일 노드 API는 단순 기능으로 차별화한다.
3. **TSS – Evolution 단계**: 샘플 서브트리와 기존 API 예시를 기반으로 LLM이 새 API를 합성하고, 새 기능/파라미터 추가, 제약 조건 추가, 파라미터 타입 변이, 반환 결과 업데이트 등 다양성 지표를 적용한 뒤, API 예시 버퍼를 유지하며 반복적으로 진화시켜 총 26,507개 API / 390개 도메인을 확보한다(중첩 파라미터 지원).
4. **SDG – Multi-Agent Generator**: User·Assistant·Tool 3개 LLM 에이전트 역할극으로 Single / Parallel / Dependent / Non-tool-use 4가지 유형 대화를 생성하며, Assistant는 API 호출·정보 요청·결과 요약·비도구 응답의 행동 공간을 갖고, 동일 행동을 여러 번 생성해 일관 결정만 채택한다.
5. **SDG – Complexity Evaluator**: 학습 대상 LLM M 자체가 데이터 샘플 (x,y)의 loss를 복잡도 대리지표로 사용하며, (1) 후보 API 수, (2) 사용 API 수, (3) user query와 API 설명 간 dissimilarity가 loss와 양의 상관관계를 보이는 것이 실증된다.
6. **SDG – 복잡도 범위 설정**: 소규모 prior 데이터셋으로 하한(모델이 이미 맞추는 샘플의 loss)과 상한(파인튜닝 후에도 높은 loss를 유지하는 샘플)을 측정해 적정 복잡도 범위를 정의한다.
7. **SDG – Self-Guided Complication**: 현재 샘플이 너무 쉬우면 User 에이전트가 더 많은 API 요구·설명과 먼 쿼리를 생성, 너무 어려우면 단순 쿼리로 동적 조정하여 모델 수준에 맞춘 데이터를 지속 생성한다.
8. **DLV – Rule Checker**: (a) API 정의 명확성(JSON Schema 준수, 필수 필드), (b) 호출 실행 가능성(API명 매칭, 필수 파라미터, 정규식 기반 포맷/패턴 검증), (c) 대화 정확성(언어 혼합, 무효 문자, 완결성), (d) 샘플 일관성(API명·포맷·역할 순서)의 4측면을 규칙으로 필터링한다.
9. **DLV – Model Checker**: LLM 검증을 Hallucination Detection(파라미터 값이 쿼리·시스템 프롬프트에 존재하는지), Consistency Validation(응답이 태스크 완수 및 제약 준수 여부), Tool Response Check(시뮬레이션된 툴 응답이 API 정의와 정합하는지)의 3개 세부 태스크로 분해하여 각각 전문 에이전트가 수행한다.
10. **DLV – 인간 감독**: 규칙 및 모델 검증 결과를 인간 전문가가 추가로 감수하여 반복적·무의미한 응답을 제거한다.
11. **학습 설정**: LLaMA3.1-8B-Instruct를 LoRA(rank=16, alpha=32, learning rate 10⁻⁴, warmup 0.1, cosine scheduler, batch 48, 3 epochs)로 SFT하여 ToolACE-8B를 생성한다.

---

## Key Contribution

1. **자기 진화 API 풀**: 사전학습 데이터에서 시작해 26,507개 API와 390개 도메인을 자동 합성하는 TSS 모듈을 제안, 기존 최대(ToolLLM 16,464 API / 49 도메인) 대비 API 60%↑·도메인 8배↑ 확장.
2. **모델 인식 복잡도 조절**: 학습 대상 LLM 자체를 Complexity Evaluator로 활용해 loss 기반 복잡도 범위를 산출하고 User 에이전트를 self-guided complication으로 구동하는 첫 프레임워크.
3. **포괄적 function-calling 유형 커버리지**: Nested 파라미터, Parallel·Dependent 호출, Multi-type(도구/비도구) 대화를 모두 지원하는 유일한 합성 파이프라인(Table 1 기준 6개 기존 시스템 중 ToolACE만 4축 전부 지원).
4. **이중 계층 검증**: 규칙 체커와 모델 체커를 분업·병렬 배치하여 실행 가능성·의미 일관성·hallucination을 동시에 억제하는 DLV 설계.
5. **8B 모델로 SOTA급 성능**: ToolACE-8B가 BFCL-v3 리더보드에서 Overall 59.22%로 3위, GPT-4-turbo(59.49%)·GPT-4o(59.29%)에 근접.
6. **일반 능력 보존**: function calling 특화 학습이 MMLU·GSM8K·HumanEval·CommonSenseQA 등 일반 벤치마크 성능을 크게 훼손하지 않음을 실증.
7. **공개 리소스**: 모델과 데이터 서브셋을 Hugging Face Team-ACE로 공개하여 후속 연구를 가능케 함.

---

## Experiment

**벤치마크**: BFCL-v3 (4,951 케이스: 3,951 single-turn + 1,000 multi-turn) 및 API-Bank(314 대화, 753 API 호출, 363 single + 122 multiple).
**백본**: LLaMA3.1-8B-Instruct 주 실험, 추가로 Qwen1.5-7B-Chat, LLaMA-3-8B-Instruct, Qwen 0.5B/1.8B/4B/7B 계열로 스케일링 분석.

**BFCL-v3 리더보드 (2024-09-20 기준)**:
- 1위 GPT-4-turbo-2024-04-09 (FC) **59.49%**, 2위 GPT-4o-2024-08-06 (FC) **59.29%**, **3위 ToolACE-8B (FC) 59.22%**.
- ToolACE-8B 세부: Non-live AST **89.27%**, Non-live Exec **90.07%**, Live AST **73.21%**, Multi-turn **14.37%**, Relevance **85.37%**, Irrelevance **83.81%**.
- 유사 규모 xLAM-7b-fc-r(51.45%)·Gorilla-OpenFunctions-v2(51.01%) 대비 +7~8%p 우위.

**API-Bank**:
- ToolACE-8B Call **75.94%**, Retrieval+Call **47.41%** — gpt-4-0613(75.94%)과 동률, 모든 오픈소스 모델(LLaMA-3.1-8B-Instruct 71.18%, xLAM-7b-fc-r 32.83%, Lynx-7B 49.87%) 초과.

**Ablation – Accuracy (DLV, Figure 3)**:
- w.o. dual → w.o. model → Final 순으로 AST/Exec/Irrelevance/Overall 모두 상승.
- Final Overall **91.81%**, Exec **92.79%**, Irrelevance **91.90%** 수준.
- Model checker 제거 시 AST·Overall에서 명확한 하락, Rule checker의 독립적 기여도 확인.

**Ablation – Complexity (Figure 4)**:
- 데이터 전체를 복잡도로 정렬해 상/중/하 각 60,000개 샘플링.
- Medium이 Tool-use 90.71%, Overall **90.80%**로 Easy(90.47%)·Hard(89.65%) 초과 — 중간 복잡도가 최적.

**Ablation – Diversity (Figure 5)**:
- API를 30개 클러스터로 분할 후 6/14/30 클러스터에서 각 ~30,000 인스턴스 샘플링.
- High diversity Overall **88.41%**, Medium 88.24%, Low 88.18% — 다양성과 성능의 양의 상관, Irrelevance detection에서 특히 개선.

**모델 크기 스케일링 (Qwen1.5 시리즈, Figure 6)**:
- Overall 기준 Raw 대비 파인튜닝 후 0.5B 14.12→61.41%, 1.8B 17.18→73.00%, 4B 41.35→82.94%, 7B 49.12→**85.24%**.
- AST 7B 58.95→85.69%, Exec 7B 55.10→84.58%로 모델 크기에 따른 지속 향상.

**백본 다양성 (Figure 7)**: Qwen1.5-7B Raw 49.12→ToolACE 86.47%, LLaMA-3-8B 53.25→89.29%, LLaMA-3.1-8B 75.06→**91.41%**.

**일반 능력 보존 (Figure 8)**: MMLU·GSM8K·HumanEval·CommonSenseQA·BFCL 5축 비교에서 ToolACE-8B가 xLAM-7B-fc-r을 MMLU·GSM8K·CSQA에서 큰 폭으로 상회, raw LLaMA-3.1-8B-Instruct 대비 일반 능력 저하 미미.

---

## Limitation

Self-evolution으로 생성된 합성 API는 실제 서비스 API와 동작 시맨틱이 다를 수 있어, 실행 환경 이질성이 존재한다.
데이터 생성·검증에 frontier LLM(GPT-4급)을 광범위하게 사용하므로 합성 비용이 상당히 크다.
주 실험이 LLaMA3.1-8B 단일 규모에 집중되어, 70B 이상 대형 모델에서의 확장성은 Qwen 1.5 시리즈 부분 검증에 그친다.
Multi-turn 카테고리 점수는 14.37%로 GPT-4o-mini-Prompt(25.75%) 등 일부 모델보다 낮아 장기 대화 능력은 상대적 약점이다.
DLV의 Rule Checker는 사전 정의된 규칙 집합에 의존하므로, 예상치 못한 오류 유형이나 의미적 뉘앙스는 포착하지 못할 수 있다.
Complexity Evaluator가 loss 기반 대리지표를 사용하지만, loss는 복잡도의 불완전한 추정치이므로 질적으로 이질적인 복잡도를 구분하기 어렵다.
GPT-4 대비 추론·이해(MMLU, CommonSenseQA)에서 여전히 명확한 격차가 있어, function calling 특화와 범용 능력을 동시에 끌어올리는 과제는 미해결이다.
API Context Tree 구축이 pretraining 데이터 품질과 frontier LLM의 추출 능력에 의존하여, 저자원 도메인에서는 커버리지가 제한될 수 있다.

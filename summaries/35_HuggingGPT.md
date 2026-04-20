# HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face

> **논문 정보**: Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, Yueting Zhuang (Zhejiang University, Microsoft Research Asia), NeurIPS 2023, arXiv:2303.17580 (2023.03), 코드: https://github.com/microsoft/JARVIS

---

## Problem

복잡한 AI 태스크는 언어·비전·음성 등 여러 도메인과 모달리티를 가로지르며, 단일 모델로 자율적으로 해결하기가 어렵다.

현재의 대규모 언어 모델(LLM)은 텍스트 생성이라는 입출력 형태에 제한되어 있어 비전·음성 같은 복잡한 정보를 직접 처리하지 못한다.

실세계의 복잡한 요청은 다수의 하위 태스크로 구성되어 여러 모델의 스케줄링과 협업을 요구하지만, LLM 단독으로는 이런 오케스트레이션 능력이 부족하다.

특정 난제에서는 LLM이 zero-shot/few-shot으로 좋은 성능을 내지만, 여전히 fine-tuned 특화 모델(expert)보다 약한 경우가 많다.

결과적으로 LLM이 AGI로 가는 길목에서 다양한 전문 AI 모델을 효과적으로 "활용"하지 못한다는 근본 한계가 존재한다.

따라서 LLM을 단일 해결자가 아닌 "컨트롤러"로 재정의하여 외부 전문 모델과 협업시키는 방법론이 필요하다.

ML 커뮤니티에는 수많은 전문 모델과 모델 설명이 존재하지만, 이들을 LLM과 연결하는 범용 인터페이스가 부재했다.

본 논문은 이 괴리를 메우기 위한 시스템 설계를 목표로 한다.

---

## Motivation

각 AI 모델은 자신의 기능을 자연어로 요약한 "모델 설명(model description)"을 가지고 있으므로, 언어가 LLM과 외부 모델을 잇는 범용 인터페이스가 될 수 있다.

Hugging Face 같은 공개 ML 커뮤니티는 언어·비전·음성 등 도메인별로 잘 정의된 모델 설명을 이미 제공하고 있어, 별도 프롬프트 엔지니어링 비용을 크게 줄일 수 있다.

LLM은 언어 이해·계획·추론 능력이 뛰어나기 때문에, 사용자 요청을 분해하고 모델 설명과 매칭하여 적절한 모델을 호출하는 "두뇌" 역할을 수행할 수 있다.

이렇게 LLM을 컨트롤러, 전문 모델들을 실행자로 배치하면 멀티모달·멀티도메인의 복잡한 태스크를 하나의 파이프라인으로 자동 해결 가능하다.

또한 이 구조는 모델을 추가할 때 프롬프트 구조를 바꿀 필요 없이 설명만 제공하면 되므로, 확장성과 개방성이 뛰어나다.

저자들은 이 아이디어가 "Language as a generic interface for LLMs to collaborate with AI models"라는 일반 원칙으로 확장되어 AGI에 한 걸음 다가간다고 주장한다.

---

## Method

1. **전체 워크플로우 4단계**: Task Planning → Model Selection → Task Execution → Response Generation 순으로 구성되며, ChatGPT가 모든 단계의 컨트롤러 역할을 수행한다.

2. **Stage 1 — Task Planning (프롬프트 슬롯 필링)**: 사용자 요청을 받으면 LLM이 `[{"task", "id", "dep", "args"}]` 형식의 구조화된 태스크 리스트로 파싱하며, "dep"으로 선행 태스크 의존성을, `<resource>-task_id` 태그로 리소스 참조를 지정한다.

3. **지원 태스크 카테고리**: 총 24개 AI 태스크(언어·비전·음성·비디오·크로스모달 포함)가 사전 정의된 태스크 리스트에서 선택되며, LLM은 이 리스트에 등록된 태스크 이름만 생성해야 한다.

4. **Demonstration-based Parsing**: 프롬프트 안에 다중 시연(demonstration)을 포함하여 각 예시가 "사용자 요청 → 기대되는 파싱 결과"를 보여주도록 설계, 의존성과 실행 순서를 학습시킨다. 다중 턴 대화를 위해 `{{ Chat Logs }}` 슬롯도 삽입한다.

5. **Stage 2 — Model Selection (in-context task-model assignment)**: 각 태스크에 대해 Hugging Face의 후보 모델들을 단일-선택(single-choice) 문제로 제시, LLM이 적합한 model_id와 선택 이유(JSON)를 출력한다.

6. **후보 모델 필터링 전략**: 컨텍스트 길이 제한 때문에 모든 모델을 담을 수 없으므로, (a) 태스크 타입이 일치하는 모델만 먼저 필터링하고, (b) Hugging Face 다운로드 수로 랭킹한 뒤, (c) 상위 K개를 후보로 프롬프트에 제공한다.

7. **Stage 3 — Task Execution**: 선택된 전문 모델에 태스크의 args를 주입해 추론하며, 태스크 의존성 그래프의 위상 정렬에 따라 선행 태스크 완료 후 실행, 독립 태스크는 병렬 실행하여 효율을 높인다.

8. **Resource Dependency 관리**: `<resource>` 기호로 선행 태스크의 출력을 후속 태스크의 입력으로 동적으로 연결하며, 실행 시점에 실제 값(이미지 경로, 텍스트 등)으로 해석(resolve)한다.

9. **Hybrid Endpoints 배포**: 로컬 인퍼런스 엔드포인트(빠르지만 커버리지 작음)와 Hugging Face 클라우드 엔드포인트(커버리지 크지만 느림)를 혼합 사용하며, 로컬에 있으면 로컬을 우선한다.

10. **Stage 4 — Response Generation**: 모든 단계 로그(플랜·선택 모델·추론 결과)를 구조화된 포맷으로 수집하고, LLM이 이를 일인칭 자연어로 사용자에게 요약·설명하며 파일 경로와 신뢰도 정보를 함께 제공한다.

11. **디코딩 설정**: LLM은 `temperature=0`, 포맷 강제용 `logit_bias=0.2`를 `{`, `}` 등 토큰에 부여하여 JSON 출력 안정성을 확보한다.

12. **프롬프트 슬롯 구조**: 각 단계 프롬프트는 `{{ Available Task List }}`, `{{ Demonstrations }}`, `{{ Candidate Models }}`, `{{ Predictions }}` 등의 주입 슬롯을 가지며, 런타임에 텍스트로 치환된 뒤 LLM에 전달된다.

---

## Key Contribution

1. **LLM-as-Controller 패러다임 정립**: ChatGPT를 컨트롤러로, Hugging Face의 전문 모델들을 실행자로 배치하여 멀티모달·멀티도메인 태스크를 자율 해결하는 협력형 시스템 HuggingGPT를 최초 제안했다.

2. **Language as a Generic Interface**: 모델 기능을 자연어 설명으로 추상화하고 LLM이 이를 기반으로 계획·선택·호출한다는 일반 원칙을 정립, 새 모델 추가 시 프롬프트 수정이 필요 없는 개방형 확장성을 확보했다.

3. **4단계 워크플로우 형식화**: Task Planning → Model Selection → Task Execution → Response Generation의 명확한 파이프라인과 각 단계별 프롬프트 템플릿, 슬롯 구조(`task/id/dep/args`)를 제공했다.

4. **태스크 계획 평가 프레임워크 제안**: Single/Sequential/Graph 세 유형으로 태스크를 분류하고 각각 F1/Edit Distance/GPT-4 Score를 정의, 다양한 LLM의 계획 능력을 정량 비교할 수 있는 실험적 기반을 마련했다.

5. **데이터셋 공개**: 3,497개 사용자 요청에 대한 GPT-4 자동 라벨링 데이터셋(Single 1,450 / Sequential 1,917 / Graph 130)과 46개의 휴먼 어노테이션 데이터셋(Sequential 24, Graph 22)을 구축하였다.

6. **Hybrid Endpoints·Resource Dependency 엔지니어링**: 로컬·클라우드 하이브리드 배포와 `<resource>` 태그 기반 동적 자원 바인딩 등 대규모 멀티모달 에이전트 시스템을 안정적으로 운용하는 실용적 구현 기술을 제시했다.

---

## Experiment & Results

- **백본 LLM**: `gpt-3.5-turbo`, `text-davinci-003`, `gpt-4`, Alpaca-7b/13b, Vicuna-7b/13b 등 비교.

- **지원 태스크**: 총 24개(언어·비전·음성·크로스모달)로 image-classification, object-detection, image-captioning, pose-detection, pose-to-image, ASR, TTS, VQA 등 포함.

- **평가 데이터셋**: GPT-4 auto-labeled 3,497건(Single 1,450 / Sequential 1,917 / Graph 130) + 휴먼 어노테이션 46건.

- **Single Task 계획 정확도 (Table 3)**: Alpaca-7b Acc 6.48 / F1 4.88, Vicuna-7b 23.86 / 29.44, GPT-3.5 52.62 / 54.45로 GPT-3.5가 압도적.

- **Sequential Task (Table 4)**: GPT-3.5 ED 0.54 / Pre 61.09 / Recall 45.15 / F1 51.92로 Alpaca-7b(ED 0.83, F1 22.80), Vicuna-7b(ED 0.80, F1 22.89) 대비 크게 우수.

- **Graph Task (Table 5)**: GPT-4 Score 기준 Alpaca-7b 13.14, Vicuna-7b 19.17, GPT-3.5 50.48. F1 기준 51.91로 GPT-3.5 최고.

- **Human-annotated Dataset (Table 6)**: GPT-4가 Sequential Acc 41.36 / ED 0.61 / Graph Acc 58.33 / F1 49.28로 GPT-3.5(18.18 / 0.76 / 20.83 / 16.45)를 크게 앞섬. 다만 휴먼 어노테이션 대비 여전히 상당한 격차 존재.

- **Demonstration Variety (Table 7)**: 시연 태스크 타입 수를 2→6→10으로 늘릴수록 Single Acc가 GPT-3.5 기준 43.31→51.31→52.83, GPT-4 기준 65.59→66.83→67.52로 증가.

- **Shot 수 효과 (Figure 3)**: 0~5 shot 증가 시 성능이 향상되나 4-shot 이후 증분이 포화되는 경향.

- **Human Evaluation (Table 8)**: 130개 요청에 대한 전문가 평가에서 GPT-3.5가 Task Planning Passing Rate 91.22%, Rationality 78.47%, Model Selection Passing 93.89%, Rationality 84.29%, 최종 Success Rate 63.08%로 Vicuna-13b(79.41/58.41/-/-/15.64), Alpaca-13b(51.04/32.17/-/-/6.92) 대비 큰 격차.

- **정성적 사례**: 이미지 분류+객체탐지+캡셔닝 통합 요청을 google/vit, nlpconnet/vit-gpt2-image-captioning, facebook/detr-resnet-101로 orchestration; pose-detection→pose-to-image(lllyasviel/sd-controlnet-openpose)→object-detection→image-classification→image-captioning→text-to-speech(facebook/fastspeech2-en-ljspeech)로 이어지는 6-태스크 DAG 체인 성공 실행.

- **핵심 관찰**: 태스크 계획 품질이 전체 시스템 성공률과 강한 상관관계를 보이며, 더 강력한 LLM(GPT-4)일수록 복잡한 Graph Task에서 이득이 커짐.

---

## Limitation

저자 언급 첫째 — **플래닝 의존성**: 전체 워크플로우가 LLM의 계획 능력에 과도하게 의존하기 때문에 생성된 플랜이 항상 실행 가능하거나 최적이라는 보장이 없다.

저자 언급 둘째 — **효율성(지연)**: Task Planning, Model Selection, Response Generation 단계마다 LLM을 호출하므로 응답 시간이 길어지고 실시간 응용에 부적합하다.

저자 언급 셋째 — **토큰 길이 제약**: 후보 모델 설명을 모두 담기에는 컨텍스트 길이가 부족하여 현재는 top-K 필터링에 의존하며, 32K 컨텍스트로도 수천 개 모델을 동시에 고려하기 어렵다.

저자 언급 넷째 — **Instability**: LLM 출력이 불확실하여 지시를 따르지 않거나 잘못된 JSON을 내는 경우가 있어 파이프라인 예외가 발생한다.

독자 관점 — **단일 장애점(SPOF)**: 전 단계가 ChatGPT 한 모델에 의존하므로 API 장애·버전 변화 시 전체 시스템이 중단되며, 초기 Task Planning 오류가 후속 단계로 그대로 전파된다.

독자 관점 — **모델 선택의 얕은 신호**: Hugging Face 다운로드 수와 텍스트 설명 매칭에 의존하므로 실제 태스크 성능(정확도·강건성)과 괴리될 수 있고, 악성/저품질 모델 필터링 장치가 부족하다.

독자 관점 — **평가 데이터셋 규모**: 휴먼 어노테이션이 46개에 불과해 통계적 신뢰도가 제한적이며, GPT-4 자동 라벨은 GPT-4 자신의 편향을 그대로 반영한다.

독자 관점 — **비용·재현성**: GPT-4를 평가자이자 백본으로 함께 사용하는 구조라 재현·비교 비용이 높고, 모델 허브의 동적 변화로 시간이 지나면 동일 실험 재현이 어렵다.

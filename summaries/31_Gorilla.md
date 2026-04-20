# Gorilla: Large Language Model Connected with Massive APIs

> **논문 정보**: Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez (UC Berkeley, Microsoft Research)
> **arXiv**: 2305.15334 (2023.05)
> **코드**: https://gorilla.cs.berkeley.edu

---

## Problem

LLM이 API 호출을 수행할 때 두 가지 치명적 실패가 발생한다: 존재하지 않는 API를 환각(hallucinate)하거나, 존재하는 API를 잘못된 인자와 함께 호출하는 것이다.

GPT-4조차 TorchHub에서 zero-shot으로 API를 생성하면 36.55%의 환각 오류율을 보이며, TensorFlow Hub에서는 무려 78.65%에 달한다.

Claude는 TorchHub에서 65.59%, TensorFlow Hub에서 88.46%의 환각률을 기록하며 더 심각한 실패를 보인다.

웹 스케일의 수백만 개에 이르는 API를 단일 프롬프트 컨텍스트에 모두 주입하는 것은 불가능하고, 기능이 중복되는 API들이 미묘한 제약 조건 차이로 구분되기 때문에 단순 프롬프팅으로는 해결되지 않는다.

또한 API 문서는 모델 재학습 주기보다 훨씬 빠르게 갱신되므로, 파라미터에 지식을 고정하는 접근법은 시간이 지나면 신뢰성이 붕괴된다.

기존 연구들은 소수의 잘 문서화된 하드코딩 도구 집합(Toolformer, HuggingGPT 등)에만 집중했고, 대규모 변화하는 API 생태계에 대한 체계적인 학습·평가 파이프라인이 부재했다.

AST 매칭 같은 기능적 등가성 평가 체계가 없으면 단위 테스트로는 "ResNet-50 vs DenseNet-121처럼 둘 다 이미지 분류에 맞는가"를 판단할 수 없어, 벤치마크 자체가 성립하지 않는다.

---

## Motivation

LLM이 자연어 쿼리를 받아 적절한 API 호출을 생성할 수 있게 되면, 여행 예약부터 컨퍼런스 운영까지 웹의 모든 컴퓨팅 인프라를 음성·텍스트 인터페이스로 통합할 수 있다.

소수 도구 집합에서 대규모 API 생태계로의 전환은 단순 프롬프트 확장이 아니라 retrieval과 fine-tuning을 결합하는 근본적으로 새로운 패러다임을 요구한다.

저자들의 통찰은 "LLM에 검색된 API 문서를 단순히 붙이는 것"보다 "검색 결과가 포함된 입력 형식으로 학습시키는 것"이 훨씬 효과적이라는 것이다 — 이를 retriever-aware training이라 부른다.

Retriever-aware training은 모델이 검색된 JSON 문서를 파싱하고 필요한 필드를 추출해 API 호출로 변환하는 능력 자체를 학습하게 만든다.

또한 ML API 도메인은 기능 중복·세밀한 성능 제약(정확도, 파라미터 수, FLOPs)·프레임워크 다양성이 풍부하여, RESTful API 등 일반 도메인으로 일반화 가능한 도전적 벤치마크를 구성하기에 이상적이다.

ML 모델 카드는 {domain, framework, api_call, arguments, performance, description}의 구조화된 메타데이터를 제공하므로, 이를 JSON으로 표준화하면 합성 지시문 생성과 AST 매칭 평가가 자연스럽게 가능해진다.

최종 목표는 API 문서 변경에 자동 적응하고, 환각 없이 제약 조건을 만족하는 호출을 생성하는 범용 도구 사용 LLM을 구축하는 것이다.

---

## Method

1. **APIBench 데이터셋 구축**: TorchHub 94개(전수), TensorFlow Hub 696개(전수), HuggingFace 925개(도메인별 top-20 다운로드 모델) — 총 1,645개 API를 수집.

2. **API 메타데이터 표준화**: 각 모델 카드를 JSON 객체로 변환, 필드는 {domain, framework, functionality, api_name, api_call, api_arguments, environment_requirements, example_code, performance, description}으로 ML을 넘어 RESTful API 일반화를 고려해 설계.

3. **Self-Instruct 지시문 생성**: GPT-4를 활용, 각 모델 허브별로 단 6개의 수작업 예시(총 18개)만 in-context 시드로 제공하고 각 API마다 10개 자연어 지시문을 합성해 총 16,450개 {instruction, API} 쌍을 생성.

4. **지시문 생성 제약**: 모델이 API 이름이나 힌트를 지시문에 포함하지 않도록 명시적으로 지시해, 현실적인 사용자 쿼리 분포를 모사.

5. **Gorilla 모델 학습**: LLaMA-7B를 베이스로, {instruction, API} 쌍을 user-agent chat 형식 대화(각 1턴)로 변환하여 standard instruction fine-tuning 수행.

6. **Zero-shot 모드**: 사용자 프롬프트만으로 API 호출을 직접 생성하도록 학습.

7. **Retriever-Aware 학습**: 학습 시 프롬프트 뒤에 "Use this API documentation for reference: <retrieved_API_doc_JSON>" 문자열과 실제 검색된 문서를 붙여 학습시킴 — 모델이 문서를 파싱해 호출을 만드는 법 자체를 학습.

8. **Retriever 종류**: BM25(각 API를 하나의 document로 인덱싱 후 top-1 검색), GPT-Index(text-davinci-003 임베딩 기반), Oracle(정답 문서를 반환하는 상한선).

9. **제약 인식 API 호출**: "10M 미만 파라미터, ImageNet top-1 70% 이상"과 같은 정량적 제약 조건을 포함한 지시문을 추가하여, 모델이 기능뿐 아니라 정확도·파라미터·FLOPs 등 trade-off를 이해하도록 학습.

10. **AST Sub-Tree Matching 평가**: 생성된 코드를 AST로 파싱 후, 타깃 API 호출(예: torch.hub.load)을 루트로 하는 서브트리를 참조 API 데이터셋과 매칭. 선택적 인자(예: pretrained=True)는 무시 가능하도록 유연하게 매칭.

11. **환각 vs 에러 구분**: AST 서브트리가 데이터셋의 어떤 API와도 매칭되지 않으면 '환각(hallucination)', 매칭되나 잘못된 API이면 '에러(error)'로 분리 정의.

12. **학습 하이퍼파라미터**: 학습률 2e-5 cosine decay, 배치 64, 5 epochs, warmup ratio 0.03, max seq 2048, 8×A100 40GB에서 수행.

13. **데이터 분할**: HuggingFace 90/10, TorchHub/TensorHub 80/20 train/test 분할.

14. **추론 파이프라인**: zero-shot은 프롬프트 그대로 입력. Retrieval 모드는 BM25 또는 GPT-Index로 최신 API 문서 검색 → 프롬프트에 concat → Gorilla가 API 호출 반환. 별도 프롬프트 튜닝 없음.

15. **Test-time 문서 변경 대응**: 학습된 Gorilla는 검색 문서만 교체하면 ResNet-50→ResNet-101 백본 업그레이드, pytorch/vision→NVIDIA/DeepLearningExamples 레포 이전 같은 API 변경을 재학습 없이 반영 가능.

---

## Key Contribution

1. **APIBench 공개**: TorchHub·TensorFlow Hub·HuggingFace 3개 허브에서 1,645개 API와 16,450개 instruction 쌍을 포함한 최초의 대규모 ML API 벤치마크를 구축·공개해 ML 도구 사용 연구의 표준 벤치마크를 제공.

2. **Retriever-Aware Fine-tuning 패러다임**: 학습 시점부터 retriever 출력을 입력 형식에 포함시키는 최초의 시도로, 모델이 검색 문서를 파싱·활용하는 능력을 내재화시킴 — 논문에서 "to the best of our knowledge, a first"로 명시.

3. **GPT-4 능가하는 7B 오픈모델**: LLaMA-7B 파인튜닝만으로 zero-shot TorchHub에서 GPT-4 대비 +20.43%, GPT-3.5 대비 +10.75%, LLaMA-7B 대비 +83% 우위를 달성해, 전용 파인튜닝이 거대 LLM 프롬프팅을 압도함을 실증.

4. **환각의 급격한 감소**: Gorilla(0-shot)의 TorchHub 환각률 6.98%로 GPT-4(36.55%)의 1/5, TensorFlow Hub에서는 5.40% vs GPT-4 78.65%로 1/14 수준까지 절감.

5. **AST Sub-Tree Matching 평가 체계**: 기능적 등가성을 서브트리 매칭으로 근사하고, 매칭 실패를 '환각', 잘못된 매칭을 '에러'로 구분해 정량화하는 신규 평가 방법론 제시.

6. **Test-time 문서 갱신 적응성**: retriever-aware 학습 덕에 재훈련 없이 API 레포 이전·버전 업그레이드에 즉시 대응 — LLM의 고질적 정적 지식 문제에 실용적 해법 제시.

7. **제약 인식 API 선택**: 파라미터 수·정확도 하한 등 trade-off를 이해하고 적절한 API를 선택하는 능력을 실증, 단순 기능 매칭을 넘어선 의사결정 능력을 정량 평가.

---

## Experiment

평가는 TorchHub, HuggingFace, TensorFlow Hub 3개 데이터셋에서 각각 overall accuracy, hallucination rate, error rate를 측정하며, 4가지 retriever 설정(0-shot, BM25, GPT-Index, Oracle)을 교차 비교.

**Zero-shot AST 정확도**: Gorilla 59.13%(TorchHub), 71.68%(HuggingFace), 83.79%(TensorFlow Hub)로 모든 영역에서 SoTA 달성 — GPT-4는 각각 38.70/19.80/18.20, GPT-3.5는 48.38/16.81/41.75.

**환각률 비교 (0-shot)**: Gorilla는 TorchHub 6.98%, HuggingFace 10.95%, TensorFlow Hub 5.40%로 GPT-4(36.55/37.16/78.65) 대비 평균 5~15배 낮음.

**GPT-Index retriever 사용 시**: Gorilla 61.82(TorchHub)/47.46(HuggingFace)/64.96(TensorFlow Hub)로, GPT-4 59.13/44.58/43.94를 모두 능가. 특히 TensorFlow Hub에서 +21.02%p 격차.

**Oracle retriever 상한선**: Gorilla 67.20/91.26/94.16 — HuggingFace에서 GPT-3.5(89.71)와 GPT-4(85.07)를 모두 앞서며, 완벽한 retriever가 있을 때도 최고 성능 유지.

**Retriever 역효과 현상**: Gorilla를 검색기 없이 학습한 뒤 test-time에 BM25/GPT-Index를 붙이면 TorchHub에서 -21.5%p, HuggingFace에서 -47.57%p로 성능이 오히려 하락 — 비최적 검색기가 모델을 오도함을 확인.

**Retriever-aware 학습 효과**: Oracle retriever를 학습 시 포함시킨 Gorilla는 미포함 대비 TorchHub +12.37%p, HuggingFace +23.46%p 향상 — 단, 학습에 쓴 retriever와 평가 retriever가 일치해야 효과가 유지됨(불일치 시 GPT-Index로 -29.20%p 하락).

**제약 조건 평가 (Accuracy constraint on TorchHub)**: Gorilla 0-shot 47.88%, Oracle 67.60%로 GPT-4(43.66/59.15), GPT-3.5(43.66/69.01)와 경쟁력 있음. LLaMA는 0/17.60로 거의 작동 불능.

**오픈소스 baseline LLaMA-7B**: TorchHub 0-shot 0%로 완전 실패, BM25에서도 8.60%에 그침 — 파인튜닝의 필요성을 극명히 입증.

**흥미로운 관찰**: GPT-3.5가 GPT-4보다 환각률이 낮음(TorchHub 18.81% vs 36.55%) — RLHF가 진실성 유지에 핵심적 역할을 함을 시사.

---

## Limitation

저자 언급 한계로, 평가가 ML 도메인(TorchHub·TensorFlow Hub·HuggingFace) API에 집중되어 있어 RESTful API, SaaS 웹서비스, 시스템 콜 등 일반 API 생태계로의 일반화는 검증되지 않았다.

저자 언급: 현재 retriever(BM25, GPT-Index)가 불완전하면 오히려 성능을 저해하며(TorchHub에서 -21.5%p), 이는 retriever 품질이 시스템 전체 성능의 병목이 됨을 의미한다.

저자 언급: ML API는 학습 데이터 편향으로 인해 특정 sub-group에 불리한 예측을 생성할 수 있는 사회적 위험이 있으며, 자동화된 도구 선택이 이러한 편향을 증폭시킬 가능성이 있다.

독자 관점에서, LLaMA-7B라는 비교적 작은 베이스 모델을 사용해 복잡한 다단계 제약 추론(예: "정확도 70%↑ AND 파라미터 10M↓ AND 지연 100ms↓")에 대한 일반화가 제한적이다 — 실제로 constraint 평가에서 47.88% 수준에 머문다.

독자 관점: 단일 API 호출만 평가 대상이며, 여러 API를 조합하는 프로그램 합성(예: 이미지 로드→분류→번역 파이프라인)은 다루지 않아 실제 에이전트 워크플로우로의 확장성이 미검증이다.

독자 관점: AST sub-tree matching은 구문적 매칭일 뿐, 기능적 등가성(예: 두 모델의 실제 품질 차이)을 포착하지 못해 "정답이지만 최적이 아닌 호출"을 동등하게 인정할 위험이 있다.

독자 관점: GPT-4로 생성한 합성 지시문에 학습 분포가 편향될 가능성이 있으며, 실제 개발자·end-user의 실제 쿼리 분포와 괴리가 존재할 수 있다 — 3:1 train/test 분할이지만 모두 동일 생성 파이프라인에서 나옴.

독자 관점: retriever-aware 학습이 특정 retriever(Oracle)에 과적합되어 test-time에 다른 retriever를 쓰면 급격히 성능이 저하되는 문제는, 실제 배포 시 retriever 업그레이드·교체를 어렵게 만든다.

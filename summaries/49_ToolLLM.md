# ToolLLM: Facilitating Large Language Models to Master 16000+ Real-World APIs

> **논문 정보**: Yujia Qin, Shihao Liang, Yining Ye 외 (Tsinghua University, OpenBMB, Yale, Tencent)
> **arXiv**: 2307.16789 (2023.07)
> **코드**: https://github.com/OpenBMB/ToolBench

---

## Problem

오픈소스 LLM(LLaMA, Vicuna, Alpaca 등)은 현재의 인스트럭션 튜닝이 기본 언어 태스크에 집중되어 있기 때문에 외부 도구(API) 호출을 통해 복잡한 인간 지시를 수행하는 능력이 심각하게 결여되어 있다.
ChatGPT, GPT-4와 같은 SOTA 폐쇄형 LLM은 도구 사용에서 뛰어난 능력을 보이지만 내부 메커니즘이 불투명하여 커뮤니티 기반 연구와 AI 기술 민주화가 제한된다.
기존 도구 학습 연구(APIBench, API-Bank, ToolAlpaca, ToolBench(Xu et al.))는 실제 REST API를 다루지 않거나, 불과 수십~수백 개의 소규모 API 풀에 국한되고, 단일 도구 시나리오만 고려한다.
이들 선행 연구는 사용자가 이상적인 API 셋을 수동으로 미리 지정해야 한다고 가정하지만, 수천~수만 개 API가 존재하는 실세계에서는 이러한 가정이 비현실적이다.
추론 전략 측면에서도 기존 접근은 CoT와 ReACT에 의존하는데, 이는 단일 경로만 탐색하며 초기 오류가 이후 전체 추론을 오염시키는 오류 전파 문제를 가진다.
일부 연구는 실제 API를 호출하지 않고 응답을 시뮬레이션만 하기 때문에, 후속 계획 수립에 필수적인 실시간 환경 피드백이 결여된다.
결과적으로 GPT-4조차 복잡한 다중 도구 지시에 대해 낮은 pass rate를 보여 학습 데이터 주석 작업 자체가 어려워진다.
오픈소스 LLM의 도구 사용 능력을 폐쇄형 모델 수준으로 끌어올리는 대규모 통합 프레임워크가 부재한 상황이다.

---

## Motivation

실세계 REST API 생태계를 포괄하는 대규모 데이터셋을 자동 구축하여 오픈소스 LLM에 도구 사용 능력을 부여하면, AI 기술의 민주화와 커뮤니티 혁신을 촉진할 수 있다.
RapidAPI Hub는 수만 개의 실제 API를 49개 카테고리와 500+ 컬렉션으로 체계화하여 제공하므로, 이를 활용하면 다양성과 실용성이 모두 확보된 벤치마크 구축이 가능하다.
ChatGPT를 활용한 셀프 인스트럭트(self-instruct) 방식은 인간 주석 비용을 크게 줄이면서 고품질 지시문과 솔루션 경로를 대량 생성할 수 있다.
단일 도구뿐 아니라 카테고리 내/컬렉션 간 다중 도구 시나리오까지 포괄해야 실제 사용자 요구(여행 계획, 쇼핑 비교, 정보 집계 등)를 반영할 수 있다.
ReACT의 단일 경로 탐색 한계를 극복하려면 트리 기반 탐색으로 여러 추론 경로를 평가하고 백트래킹할 수 있는 의사결정 알고리즘이 필요하다.
16,000+ 규모의 API 풀에서는 사용자가 관련 API를 수동 선택하는 것이 불가능하므로, 지시문으로부터 관련 API를 자동 추천하는 신경망 리트리버가 파이프라인의 필수 구성요소가 된다.
평가 또한 API의 시간적 변동성과 무한한 솔루션 경로 때문에 고정 ground-truth로 채점할 수 없으므로, ChatGPT 기반 자동 평가기(ToolEval)가 대안이 된다.
이러한 통합 프레임워크(데이터 + 학습 + 평가 + 리트리버)가 갖춰지면 오픈소스 LLM이 unseen API에도 제로샷으로 일반화되는 것을 검증할 수 있다.

---

## Method

1. **RapidAPI 크롤링 및 필터링**: RapidAPI Hub에서 49개 거친 카테고리와 500+ 세분화된 컬렉션(collection)을 기준으로 10,853개 도구(53,190개 API)를 초기 수집한 뒤, (a) 기본 기능 테스트에서 404/내부 에러를 반환하는 API 제거, (b) 응답 시간이 지나치게 긴 API 제거, (c) HTML 소스코드 등 저품질 응답 API 제거를 거쳐 최종 3,451개 도구(16,464개 API)를 확보한다.
2. **API 메타데이터 구조화**: 각 API에 대해 이름, 설명, HTTP 메서드, 필수/선택 파라미터, request body, 실행 가능한 코드 스니펫, 예시 응답을 기록하여 LLM이 제로샷으로도 이해 가능하도록 한다.
3. **인스트럭션 생성 (3종 시나리오)**: 무작위 지시문 브레인스토밍 대신 API 조합을 먼저 샘플링하고 그에 맞는 지시문을 생성하는 역방향 설계를 채택한다; 단일 도구(I1), 카테고리 내 다중 도구(I2), 컬렉션 간 다중 도구(I3)의 세 가지 샘플링 전략으로 다양성을 확보한다.
4. **In-context Seed 프롬프팅**: 인간 전문가가 작성한 12개(단일 도구) / 36개(다중 도구) 시드 예시 중 매번 3개를 무작위 선택하여 ChatGPT에 in-context learning으로 제공한다; I2/I3에서는 같은 카테고리/컬렉션에서 2~5개 도구를 뽑고 각 도구당 최대 3개 API를 샘플링하여 sparsity 문제를 해결한다.
5. **할루시네이션 필터링**: 생성된 지시문 중 존재하지 않는 API를 참조하는 항목을 걸러내어 최종 I1=87,413, I2=84,815, I3=25,251 (총 약 200k) 쌍의 (instruction, 관련 API) 데이터를 확보한다.
6. **Solution Path Annotation**: 각 지시문에 대해 ChatGPT의 function call 기능을 활용해 (Thought, API Name, Parameters) 형식의 다단계 대화로 솔루션 경로를 주석한다; 두 개의 종료 함수 "Finish with Final Answer"와 "Finish by Giving Up"을 추가로 정의한다.
7. **DFSDT (Depth-First Search-based Decision Tree)**: ReACT의 오류 전파와 단일 경로 한계를 해결하기 위해 트리 기반 탐색을 도입한다; 각 노드에서 실패하면 "Finish by Giving Up"을 호출하여 백트래킹하고, 이전에 생성된 노드 정보를 프롬프트에 포함시켜 ChatGPT가 자식 노드를 다양화하도록 유도한다.
8. **DFS vs BFS 선택**: 유효 경로 하나만 찾으면 주석이 완료되므로 BFS보다 DFS가 API 호출 비용이 낮다; 더 나아가 실제 구현에서는 자식 노드 정렬(O(n log n) API 호출)을 생략하는 pre-order traversal 변형을 사용하여 단순 인스트럭션에서 ReACT로 degrade되는 효율적 동작을 확보한다.
9. **API 응답 압축**: API 응답이 1024 토큰을 초과하면 ChatGPT로 응답 스키마의 중요 키만 남기는 전략을 사전 생성해 두고, 인퍼런스 중 적용하여 컨텍스트 길이 문제를 회피한다.
10. **최종 학습 데이터**: DFSDT를 모든 지시문에 적용하여 성공한 경로만 보존, 126,486개의 (instruction, solution path) 쌍을 확보한다 (평균 추론 트레이스 4.0, 실제 API 호출 총 469,585회).
11. **ToolLLaMA 파인튜닝**: LLaMA-2 7B 모델을 대상으로 멀티턴 대화 형식으로 학습; 학습률 5e-5, warmup ratio 4e-2, 배치 크기 64, 2 에폭, position interpolation ratio 2로 컨텍스트 길이를 4096 → 8192로 확장한다.
12. **신경망 API 리트리버**: Sentence-BERT 기반으로 ChatGPT가 생성한 (instruction, relevant API) 쌍을 positive로, 무관한 API를 negative로 하는 contrastive learning을 수행한다; 16,000+ API 풀에서 상위 5개를 추천하여 ground-truth API 대신 ToolLLaMA에 공급 가능하다.
13. **ToolEval 평가기**: AlpacaEval 방식을 따라 ChatGPT 기반 자동 평가를 구축; Pass Rate는 제한 예산 내 지시 완수 여부를, Win Rate는 두 솔루션 경로 간 품질 비교를 측정한다; 각 경로에 대해 4회 이상 예측 후 majority vote로 최종 결정한다.
14. **6개 일반화 설정 평가**: I1-Inst.(미관측 지시), I1-Tool(미관측 도구/동일 카테고리), I1-Cat.(미관측 카테고리), I2-Inst., I2-Cat., I3-Inst.로 구분하여 3단계 일반화 능력을 체계적으로 측정한다.

---

## Key Contribution

1. **실세계 규모 도구 학습 벤치마크 최초 공개**: 3,451개 도구와 16,464개 실제 REST API, 126,486개 인스턴스, 469,585회 실제 API 호출을 포함하여 기존 최대 규모였던 APIBench(1,645 API, 17,002 인스턴스) 대비 API 수 10배, 인스턴스 7배 확장을 달성한다.
2. **DFSDT 추론 알고리즘 제안**: ReACT의 오류 전파와 탐색 공간 제한을 동시에 해결하는 트리 기반 의사결정 전략으로, 실제 ReACT 대비 ChatGPT 평균 Pass Rate를 35.3% → 63.8%로 끌어올리며 ReACT@N(동일 예산 반복 실행) 44.5%보다도 19.3%p 우위를 보인다.
3. **자동화된 데이터 구축 파이프라인**: 인간 주석을 12~36개 시드 예시로 최소화하고 ChatGPT만으로 200k급 instruction-API 쌍과 126k급 솔루션 경로를 생성하는 재현 가능한 방법론을 확립한다.
4. **ToolLLaMA 모델 공개**: LLaMA-2 7B를 기반으로 Text-Davinci-003과 Claude-2를 초과하고 교사 모델 ChatGPT에 필적하는 도구 사용 능력을 증명하며, 가중치와 코드를 완전 공개하여 오픈소스 생태계에 기여한다.
5. **신경망 API 리트리버**: 16,000+ API 풀에서 NDCG@5 84.9를 달성하여 BM25(17.0)와 Ada(45.4)를 압도하고, ground-truth API를 사용한 설정보다도 ToolLLaMA의 Pass Rate와 Win Rate를 높이는 역설적 성능을 보인다.
6. **OOD 일반화 검증**: APIBench(HuggingFace, TorchHub, TensorHub)에서 학습 없이도 Gorilla-ZS+BM25를 넘어서는 성능을 보여 도메인 외 일반화 능력을 실증한다.
7. **ToolEval 자동 평가 체계**: API의 시간 변동성과 해답 다양성 때문에 고정 ground-truth가 불가능한 환경에서 solvable/unsolvable 사례를 포함한 세분화된 Pass/Fail 룰과 majority voting으로 인간 평가와 높은 상관을 보이는 확장 가능한 평가 프로토콜을 설계한다.

---

## Experiment

**실험 대상**: ToolLLaMA(LLaMA-2 7B 파인튜닝), ChatGPT(gpt-3.5-turbo-16k), GPT-4, Claude-2, Text-Davinci-003, Vicuna, Alpaca — 각각 ReACT와 DFSDT 두 추론 전략을 적용.
**평가 설정**: 6개 일반화 조합 (I1-Inst., I1-Tool, I1-Cat., I2-Inst., I2-Cat., I3-Inst.); Pass Rate와 Win Rate(vs ChatGPT-ReACT) 보고.

**메인 결과 (ToolBench 평균)**:
- ToolLLaMA-DFSDT: Pass Rate **66.7%**, Win Rate **60.0%**.
- ToolLLaMA-DFSDT-Retriever: Pass Rate **67.3%**, Win Rate **63.1%** (ground-truth API 사용보다 오히려 향상).
- ChatGPT-DFSDT: Pass Rate 64.8%, Win Rate 64.3% (ToolLLaMA와 동등 수준).
- GPT-4-DFSDT: Pass Rate **71.1%**, Win Rate **70.4%** (전체 최고).
- Claude-2-DFSDT: Pass Rate 22.6%, Win Rate 43.5%.
- Text-Davinci-003-DFSDT: Pass Rate 43.1%, Win Rate 46.3%.
- Vicuna / Alpaca: Pass Rate **0.0%** / Win Rate **0.0%** (도구 사용 완전 실패).

**DFSDT vs ReACT (ChatGPT 기준, 부속 실험)**:
- 평균 Pass Rate ReACT 35.3% → DFSDT 63.8% (**+28.5%p**).
- I1: 37.8% → 58.0%, I2: 40.6% → 70.6%, I3: **27.6% → 62.8%** (+35.2%p, 복잡 시나리오일수록 이득 증가).
- 동일 예산을 투입한 ReACT@N도 44.5%에 그침.

**API 리트리버 성능 (NDCG)**:
- 평균 NDCG@1 / NDCG@5: BM25 18.5 / **17.0**, Ada 49.6 / **45.4**, 제안 모델 78.0 / **84.9**.
- I1 세팅이 I2/I3보다 일관되게 높은 NDCG — 단일 도구 검색이 다중 도구보다 쉬움을 시사.

**OOD 일반화 (APIBench, AST accuracy ↑ / Hallucination rate ↓)**:
- HuggingFace: ToolLLaMA+Retriever **AST 16.77, Hallu. 10.60** vs Gorilla-ZS+BM25 AST 10.51, Hallu. 46.90.
- TorchHub: ToolLLaMA+Retriever **AST 51.16** vs Gorilla-ZS+BM25 AST 44.62.
- TensorHub: ToolLLaMA+Retriever AST 40.59, Hallu. 6.48 (경쟁력 있는 수준).
- Oracle retriever 조건에서 ToolLLaMA는 HuggingFace AST **88.80**, TorchHub 85.88, TensorHub 88.62를 기록.

**학습 세부**: 시퀀스 길이 4096 → 8192 (positional interpolation ratio 2), 학습률 5×10⁻⁵, 배치 64, 2 epoch, warmup ratio 4×10⁻².
**데이터 규모**: 총 126,486 (instruction, solution path) 쌍, 평균 추론 트레이스 4.0, 실제 API 호출 469,585회.

---

## Limitation

RapidAPI는 실제 운영 중인 외부 서비스에 의존하므로 API가 런타임에 다운되거나 응답 포맷이 변경될 수 있어, 동일한 테스트 세트에 대해서도 시간이 지나면 모델 성능 비교가 불공정해질 가능성이 있다.
학습 데이터 전체가 ChatGPT(gpt-3.5-turbo-16k)로부터 distillation된 결과이므로, ToolLLaMA의 성능 상한이 교사 모델인 ChatGPT 수준에 머물고 GPT-4의 우수한 부분은 학습에 반영되지 못한다.
DFSDT는 트리 확장 과정에서 ReACT 대비 더 많은 OpenAI API 호출을 소비하므로 추론 비용이 증가하며, 간단한 태스크에서는 ReACT와 동일한 효율로 degrade되지만 복잡 태스크에서는 여전히 고비용이다.
ToolEval은 ChatGPT를 평가자로 사용하기 때문에 평가자-피평가자 공통 편향(예: ChatGPT가 자신의 출력 스타일을 선호)이 존재할 수 있어, 인간 평가와 높은 상관에도 불구하고 절대적 신뢰도에는 한계가 있다.
본 연구의 파인튜닝은 LLaMA-2 7B에 국한되어 더 큰 모델(13B, 70B)에서의 스케일링 효과나 더 작은 모델(3B 이하)에서의 degrade 양상에 대한 체계적 분석이 부재하다.
API 응답 압축 단계에서 1024 토큰 이상의 응답은 잘라내거나 스키마 제거하므로, 긴 문서나 복합 데이터를 반환하는 API의 경우 중요한 정보가 손실될 위험이 있다.
I1 87k / I2 85k / I3 25k의 분포는 컬렉션 간 다중 도구(I3) 데이터가 상대적으로 적어, 실세계의 가장 어려운 이종 도구 조합 시나리오에서 학습 신호가 부족하다.
Vicuna와 Alpaca가 Pass Rate 0%를 기록한 것처럼 범용 인스트럭션 튜닝이 도구 사용 능력에 거의 기여하지 않음을 보여주지만, 역으로 ToolLLaMA가 도구 외 범용 대화 능력에서 얼마나 퇴화했는지에 대한 검증이 누락되어 멀티 태스크 trade-off가 불분명하다.

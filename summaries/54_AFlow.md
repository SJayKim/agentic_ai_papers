# AFlow: Automating Agentic Workflow Generation

> **논문 정보**: Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu 외 (DeepWisdom, HKUST-GZ, RUC, PKU, KAUST)
> **arXiv**: 2410.10762 (2024.10) | **게재**: ICLR 2025
> **코드**: https://github.com/FoundationAgents/AFlow

---

## Problem

LLM 기반 에이전틱 워크플로우는 코드 생성·데이터 분석·QA·수학 등 다양한 도메인에서 강력한 성능을 보이지만, 그 구성을 전적으로 인간 전문가의 수작업 설계에 의존한다.
각 태스크마다 요구되는 LLM 호출 순서, 프롬프트, 조건 분기, 반복 로직 등을 수동으로 작성·튜닝해야 하므로 새로운 도메인으로 확장하거나 스킬을 전이하는 데 많은 비용이 발생한다.
기존 자동화 연구들은 부분적인 해법만 제시한다. DSPy(Khattab et al., 2024)는 초기 워크플로우를 여전히 사람이 설정해야 하며 프롬프트 최적화에만 집중한다.
TextGrad(Yüksekgönül et al., 2024)나 GPTSwarm(Zhuge et al., 2024)은 그래프 기반 표현의 한계로 조건 분기·병렬 실행·루프를 자연스럽게 표현하지 못해 가능한 워크플로우 다양성을 담아내지 못한다.
ADAS(Hu et al., 2024)는 코드로 워크플로우를 표현해 표현력은 충분하지만, 선형 휴리스틱 탐색을 쓰기 때문에 제한된 반복 내에서 효과적인 구조를 발견하지 못한다.
따라서 "코드로 표현 가능한 충분히 큰 워크플로우 공간을 효율적으로 탐색해 완전히 자동으로 고성능 워크플로우를 생성하는" 체계적 프레임워크가 부재한 상태다.

---

## Motivation

저자들은 워크플로우 최적화를 **코드 기반 그래프의 탐색 문제(search problem over code-represented workflows)**로 재정의한다.
각 워크플로우는 LLM 호출 노드(N)와 그 사이의 엣지(E)로 구성되며, 엣지는 Python 코드로 표현되어 순차/조건/반복/병렬 구조를 모두 담을 수 있다.
이 통합 표현은 그래프(GPTSwarm)나 신경망(DyLAN)이 지원하지 못하는 조건 분기와 제어 흐름을 자연스럽게 담아내 탐색 공간의 표현력을 극대화한다.
이 방대하지만 구조화된 공간을 효율적으로 탐색하기 위해 저자들은 **Monte Carlo Tree Search(MCTS)**의 변형을 도입한다.
MCTS는 tree 구조로 과거 탐색 경험을 **정보 손실 없이 보존**할 수 있어, 같은 워크플로우를 재방문할 때 이전 성공/실패 경험을 정확히 재활용할 수 있다.
동시에 선택(Selection) 단계에서 빈 초기 템플릿으로 복귀할 확률을 일정 비율로 섞어두면 국소 최적에 빠지지 않고 지속적인 탐사가 가능하다.
공통 에이전틱 패턴(Ensemble, Review & Revise 등)을 **Operator**라는 재사용 블록으로 정의해 LLM 옵티마이저의 탐색 효율을 한층 끌어올린다.

---

## Method

1. **워크플로우 형식화**: 워크플로우 W = (N, E)로 정의. 각 노드 Nᵢ는 4-튜플 (Model M, Prompt P, Temperature τ, Output Format F)로 구성되고, 엣지 E는 코드로 표현되어 논리·의존성·실행 순서를 담는다.
2. **엣지 표현 선택**: 그래프(DAG+Petri 확장 필요)·뉴럴넷(적응적이지만 제어 불가) 대비 **코드**가 선형·조건·루프·그래프·네트워크를 모두 포괄하므로 이를 기본 엣지 표현으로 채택한다.
3. **Operator 집합 O**: 7종 사전 정의 — (1) Generate, (2) Format, (3) Review & Revise, (4) Ensemble, (5) Test, (6) Programmer, (7) Custom(기본). 각 Operator는 노드+엣지 조합을 래핑한 재사용 모듈이다.
4. **탐색 공간 단순화**: M·τ·F를 고정하고 프롬프트 P와 코드 엣지 E 및 Operator 배치만 탐색 대상으로 삼아 공간을 유한-유효 영역으로 압축. S_AFlow = {(P₁,…,Pₙ, E, O₁,…,Oₙ)}.
5. **초기화**: 빈 템플릿 W₀(단일 노드, 프롬프트 없음)에서 시작. 데이터셋을 검증:테스트 = 1:4 비율로 무작위 분할.
6. **Soft Mixed Probability Selection (선택 단계)**: 트리 내 상위-k 워크플로우와 초기 W₀를 혼합 확률로 뽑는다. P_mixed(i) = λ·(1/n) + (1−λ)·softmax(α(sᵢ − s_max))로, α=0.4(점수 영향)·λ=0.2(탐색 비중)를 사용해 국소 최적 회피.
7. **LLM-Based Expansion (확장 단계)**: Claude-3.5-Sonnet을 옵티마이저로 사용해 선택된 워크플로우를 **단일 단계 수정**(프롬프트 수정 또는 노드/Operator 추가·제거)한다. 입력에는 부모 워크플로우의 수정 이력, 성공/실패 여부, 예측 로그와 기대 출력이 모두 포함된다.
8. **Execution Evaluation (평가 단계)**: 생성된 자식 워크플로우를 **검증셋에서 5회 실행**해 평균·표준편차를 계산. 반복당 비용은 늘지만 옵티마이저에게 더 정확한 피드백을 제공해 전체 반복 수를 줄인다.
9. **Experience Backpropagation (역전파 단계)**: (워크플로우 성능, 부모 대비 수정 내용, 최적화 성공 여부)를 부모 노드로 역전파하여 experience 버퍼에 누적하고, 점수는 전역 기록에 추가해 다음 Selection에 반영.
10. **종료 조건**: 최대 20라운드 수행하거나 상위-k 평균 점수가 n 라운드 연속 개선되지 않으면 조기 종료.
11. **Operator-Free 모드**: Operator를 전혀 주지 않고 Custom만으로도 실행 가능. Ensemble 유사 구조가 자율 발견되는지 검증하는 ablation 세팅.
12. **단일 수정 원칙**: 한 iteration당 오직 하나의 구조적 변화(노드 1개 추가, 프롬프트 1회 수정 등)만 허용해 트리 상 경험이 명확히 귀속되게 한다.

---

## Key Contribution

1. **문제 재정의**: 에이전틱 워크플로우 최적화를 "코드로 표현된 노드·엣지 공간에 대한 탐색 문제"로 공식화하고, 탐색 공간 S와 평가 함수 G의 수학적 정의를 제공한 최초의 통합 프레임워크를 제시.
2. **MCTS 기반 자동 워크플로우 탐색**: Soft Mixed Probability Selection, LLM-based Expansion, Multi-run Execution Evaluation, Experience Backpropagation의 4단계 루프로 구성된 MCTS 변형을 설계해 기존 선형 휴리스틱(ADAS)의 비효율을 극복.
3. **6개 벤치마크 전수 SOTA**: HumanEval·MBPP·MATH·GSM8K·HotpotQA·DROP에서 수동 설계 대비 평균 +5.7%p, 자동화 기법(ADAS) 대비 +19.5%p 개선을 달성.
4. **비용-성능 파레토 프런티어 달성**: AFlow로 생성한 워크플로우를 사용하면 GPT-4o-mini 같은 소형 모델이 GPT-4o를 능가하며, 추론 비용은 GPT-4o의 **4.55%** 수준.
5. **Operator-Free 자율 발견**: Operator 없이도 GSM8K 93.1%를 달성하고, Ensemble 유사 구조를 자율적으로 만들어내 "완전 자동화"에 한 걸음 더 근접함을 실증.
6. **실용 공개 자원**: 알고리즘 의사코드(Algorithm 1), 옵티마이저 프롬프트, 노드/워크플로우 코드 템플릿, 전체 이터레이션 로그(Appendix)까지 포함해 재현성을 확보.

---

## Experiment

- **벤치마크(6종)**: HumanEval·MBPP (코드, pass@1), MATH lv5 617문항·GSM8K (수학, solve rate), HotpotQA 1,000샘플·DROP 1,000샘플 (QA, F1). 검증:테스트 = 1:4 분할.
- **베이스라인(7종)**: IO, CoT, CoT Self-Consistency(5 answers), MedPrompt(3 answers·5 votes), MultiPersona Debate, Self-Refine(최대 3 iter), ADAS(30 iter).
- **모델 구성**: 옵티마이저 = Claude-3.5-Sonnet, 실행자 = GPT-4o-mini(기본)·DeepSeek-V2.5·Claude-3.5-Sonnet·GPT-4o. 온도: DeepSeek-V2.5는 1, 그 외는 0. AFlow 반복 20라운드.
- **메인 결과(Table 1, 6개 벤치 평균)**: AFlow **80.3%** vs ADAS 67.2% / CoT-SC 76.0% / MultiPersona 75.1% / Self-Refine 70.7% / IO 72.8%. 수동 설계 대비 **+5.7%p**, ADAS 대비 **+19.5%p(상대 개선)**.
- **벤치별 수치**: HotpotQA **73.5 F1** (ADAS 64.5, CoT-SC 68.9), DROP **80.6 F1** (76.6, 78.8), HumanEval **94.7** (82.4, 91.6), MBPP **83.4** (53.4, 73.6), GSM8K **93.5** (90.8, 92.7), MATH lv5 **56.2** (35.4, 50.4).
- **ADAS 대비 개선 폭**: MATH lv5에서 +20.8%p, MBPP에서 +30.0%p — 난이도 높은 태스크일수록 AFlow의 우위가 커진다.
- **전이성(Table 2, HumanEval)**: GPT-4o-mini로 탐색한 워크플로우를 GPT-4o에 적용 시 **96.2%**, Claude-3.5-Sonnet에 적용 시 95.4%. DeepSeek-V2.5로 탐색한 워크플로우도 GPT-4o-mini에서 90.8%로 대부분의 수동 설계를 상회. 단, 특정 모델에서 탐색한 워크플로우가 같은 모델에서 가장 잘 작동해 "모델별 최적 워크플로우가 다름"을 시사.
- **비용 파레토(Figure 4, HumanEval)**: GPT-4o-mini + AFlow 조합이 GPT-4o 단독보다 높은 pass@1을 달성하면서 실행 비용은 **GPT-4o의 약 4.55%** 수준 — 파레토 프런티어 전면 재정의.
- **Ablation (Operator 유무, GSM8K)**: Operator 포함 AFlow 최종 93.5%, Operator 없는 AFlow도 93.1%로 모든 수동 설계(최대 92.8%)를 상회. Operator는 수렴 속도를 가속하고 점진적 개선을 돕지만, 없어도 AFlow가 Self-Consistency Ensemble 유사 구조를 자율 발견.
- **Case Study (GSM8K 20라운드 이터레이션)**: 라운드 2에 ScEnsemble operator 추가(점수 0.8872), 라운드 3에 Programmer 검증 단계 추가(0.9160), 라운드 8·10에서 prompt 정제(0.9333→0.9352). 라운드 5의 "custom review 직접 수정"과 라운드 14의 "discount 과집중 재서술" 같은 실패 시도는 트리에 기록돼 이후 탐색에서 회피.

---

## Limitation

MCTS 기반 탐색은 반복마다 검증셋 5회 실행을 요구하므로, 태스크 복잡도와 반복 수에 비례해 탐색 비용이 선형 이상으로 증가한다.
검증셋(전체의 1/5) 위에서 최적화되므로 분포가 크게 다른 신규 문제에 **과적합**할 가능성이 존재하며, 논문에서도 서로 다른 모델 간 워크플로우 전이 시 성능이 일부 떨어지는 현상을 관찰한다.
AFlow는 사전 탐색(offline search) 패러다임이기 때문에 **실시간으로 들어오는 새 태스크**에 즉시 적응하는 온라인 적응 능력은 제공하지 못한다.
Model M·Temperature τ·Output Format F를 고정한 단순화 가정 하에서만 수렴이 보장되며, 이들 파라미터까지 공동 탐색하는 경우의 안정성은 논의되지 않았다.
평가 함수 G가 명확한 수치 스코어를 주는 **reasoning 태스크(QA·코드·수학)**에 한정되어 있어, 개방형 생성·창작·장기 에이전트 실행처럼 평가가 모호한 태스크로의 일반화는 별도 연구 과제로 남는다.
Operator 집합은 여전히 사람이 설계해 주입해야 하며, 완전 자동 발견 모드(Custom만 사용)에서는 수렴이 느려지고 탐색 비용이 커진다.
옵티마이저로 Claude-3.5-Sonnet 같은 최상위 LLM에 의존하므로, 탐색 단계 자체의 API 비용과 외부 의존성이 실배포 시 병목이 될 수 있다.

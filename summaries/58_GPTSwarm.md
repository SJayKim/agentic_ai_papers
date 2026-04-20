# GPTSwarm: Language Agents as Optimizable Graphs

> **논문 정보**: Mingchen Zhuge, Wenyi Wang, Louis Kirsch, Francesco Faccio, Dmitrii Khizbullin, Jürgen Schmidhuber (KAUST, IDSIA)
> **arXiv**: 2402.16823 (2024.02)
> **학회**: ICML 2024 Oral (top 1.5%)
> **코드**: https://gptswarm.org

---

## Problem

LLM 기반 에이전트 시스템이 폭발적으로 증가하고 있으나 각 시스템은 프롬프트 설계와 토폴로지가 수작업으로 결정되어 확장성과 재현성이 떨어진다.
Chain of Thought, ReAct, Tree of Thought, Reflexion, Graph of Thought 같은 프롬프팅 기법들은 서로 다른 코드베이스로 파편화되어 있어 공통된 추상화 없이 통합하기 어렵다.
AutoGPT, LangChain, LlamaIndex, XAgent 등 단일 에이전트 프레임워크와 CAMEL, ChatDev, AutoGen, MetaGPT 등 멀티 에이전트 프레임워크는 각각 고유한 통신·오케스트레이션 규약을 갖고 있어 상호 결합이 불가능하다.
기존 방법들은 에이전트 간 통신 토폴로지(누가 누구와 연결되는가)를 고정된 휴리스틱으로 수동 설계하며, 작업에 따라 이 토폴로지를 자동으로 학습할 메커니즘이 없다.
또한 노드 단위 프롬프트 최적화 방법(OPRO, PromptBreeder)은 단일 전역 프롬프트를 겨냥하여 여러 노드가 상호작용하는 그래프 구조의 프롬프트를 동시에 최적화하지 못한다.
에이전트 시스템을 신경망 가중치처럼 자동 개선할 수 있는 통일된 최적화 가능한 추상화가 절실하다.

---

## Motivation

Marvin Minsky의 "Society of Mind" 이론은 고차 지능이 단순하고 모듈화된 인지 구성요소들의 결합에서 창발한다고 주장하며, 이 관점은 LLM 에이전트 시스템 설계에 자연스럽게 적용된다.
LLM 에이전트의 각 연산(LLM 추론, 도구 호출, API 호출, 임베디드 액션)을 노드로 정의하고 정보 흐름을 엣지로 정의하면, 전체 시스템을 계산 그래프(DAG)로 표현할 수 있다.
여러 에이전트가 협력하는 스웜(swarm)은 하위 그래프들을 결합한 복합 그래프(composite graph)로 표현되며, 에이전트 간 엣지는 통신 채널을 의미한다.
이러한 그래프 표현이 주어지면 노드의 프롬프트와 엣지의 연결 패턴을 학습 가능한 파라미터로 취급하여 신경망 가중치처럼 자동 최적화할 수 있다.
LLM의 in-context learning 능력을 감안하면, 프롬프트와 추론 구조를 최적화하는 행위는 본질적으로 LLM 메타러닝에 해당하며 Schmidhuber 계열의 자기참조 학습 아이디어와 연결된다.
DAG 최적화는 고전적 딥러닝의 노드/엣지 pruning(Ivakhnenko 1965)으로 거슬러 올라가는 유서 깊은 주제이며, 최근에는 미분 가능한 연속 최적화로 확장되고 있다.

---

## Method

GPTSwarm은 에이전트 시스템을 최적화 가능한 계산 그래프로 추상화한 뒤 노드 프롬프트와 엣지 연결을 동시에 학습한다.

### 1. 노드·에이전트·스웜 정의
노드 n은 LLM 호출·도구 호출·함수 호출·임베디드 액션 등 기본 연산 단위이며 연산 루틴 f_n을 수행한다.
에이전트는 DAG G = (N, E, F, o)로 정의되며, N은 노드 집합, E ⊂ N×N은 유향 엣지, F = {f_n}은 연산 루틴, o는 출력 노드이다.

### 2. 그래프 실행 알고리즘 (Algorithm 1)
입력 x와 각 노드 n에 대해 토폴로지 순서로 z_n = {f_v(z_v, x) : v ∈ pre(n)}을 누적하고 최종 출력 ŷ = f_o(z_o, x)를 반환한다.
선행 노드가 없는 노드는 빈 컨텍스트로 시작하며, 대다수 루틴은 입력 x를 무시하고 선행 노드 출력만 사용한다.

### 3. 복합 그래프(Swarm) 구성
K개 에이전트 그래프 {G_k}를 결합하여 복합 그래프 G_E = (N', E_E, F', o')를 구성한다.
추가 엣지 E ⊂ ∪_{i≠j} N_i × N_j는 에이전트 간 통신 채널을 나타내며 전체 구조는 여전히 DAG로 제한된다.

### 4. 엣지 최적화 문제 정식화
잠재 엣지 집합 {e_i}_{i=1}^d이 주어지면 2^d가지 구성이 가능하며, 최적화 목표는 max_E u_τ(G_E)이다 (u_τ는 태스크 유틸리티).
조합적 복잡성과 u_τ의 비미분성을 해결하기 위해 각 엣지 e_i에 포함 확률 θ_i ∈ [0,1]을 할당하고 분포 D_θ 위에서 기대 유틸리티를 최적화한다.

### 5. REINFORCE 기반 엣지 학습 (Algorithm 2)
∇_θ E_{G_E~D_θ}[u_τ(G_E)] ≈ (1/M) Σ_{i=1}^M û_τ(G_i) ∇_θ log p_θ(G_i)의 unbiased gradient estimator를 사용한다.
매 반복 M개 그래프를 샘플링하고 Adam(α = 0.4) 등으로 θ를 업데이트하며, 사이클을 만드는 엣지는 자동 제외한다.

### 6. 노드 프롬프트 최적화 — Separation of Concerns
각 노드에 파라미터화된 프롬프트 p_n과 자연어 기능 설명 d_n("a Python code generator" 등)을 부여하여 파라미터화된 그래프 G_P = (N, E, F_P, o)를 구성한다.
모든 타 프롬프트가 고정되어 있다는 가정 하에 한 번에 하나의 노드 프롬프트만 갱신하는 가정을 도입한다.

### 7. 노드 최적화 알고리즘 (Algorithm 3)
각 노드 n에 대해 빈 history h_n을 초기화하고, 그래프 실행 후 (z_n, x, f_{p_n n}(z_n, x))를 h_n에 추가한다.
OPRO 같은 프롬프트 개선 함수 I(h_n, p_n, d_n)을 적용하여 입출력 쌍을 few-shot 예시로 활용한 개선된 프롬프트를 얻는다.

### 8. 복합 최적화 및 모듈 라이브러리
엣지 최적화와 노드 최적화는 독립적으로 또는 결합하여 수행할 수 있으며, 프레임워크는 DirectAnswer·GenerateQuery·WebSearch·FileAnalyzer·CombinedAnswer 등 공용 모듈과 인덱스 기반 메모리를 제공한다.
CoT·ToT·ReAct·Reflexion·Self-Consistency는 모두 기본 노드 연산의 재조합으로 구현되어 통일된 그래프 표현 하에서 비교·결합된다.

---

## Key Contribution

1. **통합 그래프 추상화**: CoT, ToT, ReAct, Reflexion, Self-Consistency 등 이질적인 LLM 에이전트 기법을 단일 계산 그래프(DAG) 표현으로 통일하여 상호 비교·결합을 가능하게 했다.
2. **스웜(복합 그래프) 형식화**: 여러 에이전트 그래프를 결합한 composite graph 개념을 제시하고, 에이전트 간 엣지를 통신 채널로 정의하여 계층적 집단 지능을 모델링했다.
3. **REINFORCE 기반 엣지 자동 최적화**: 통신 토폴로지를 확률 분포 D_θ로 파라미터화하고 unbiased policy gradient로 학습하는 최초의 자동 오케스트레이션 최적화 기법을 제안했다.
4. **Separation-of-Concerns 노드 프롬프트 최적화**: 각 노드가 고유 기능 설명 d_n을 갖는 모듈형 구조 위에서 타 프롬프트를 고정한 채 한 노드씩 개선하는 반복 알고리즘을 정립했다.
5. **오픈소스 모듈형 프레임워크**: DirectAnswer·WebSearch·FileAnalyzer·CombinedAnswer 등 기본 노드를 제공하여 새로운 에이전트 시스템을 재조합으로 신속히 구축할 수 있게 했다.
6. **적대 에이전트 자동 격리**: 엣지 최적화가 악성 노드를 자동으로 비활성화하여 멀티 에이전트 시스템의 견고성을 높이는 부수적 능력을 실증했다.
7. **다중 벤치마크 검증**: MMLU·Mini Crosswords·HumanEval·GAIA 네 가지 벤치마크에서 Tree of Thought·GPT-4-Turbo 등 강력한 베이스라인 대비 일관된 개선을 달성했다.

---

## Experiment

**MMLU 적대 설정**: 4-choice MMLU 검증셋 앞 10%에서 k IO 에이전트 + k 적대 에이전트(k=1,3,5,7) 구성으로 GPT-4-Turbo(temperature 0.2)를 사용했고, REINFORCE 200회 반복 (반복당 4그래프 샘플)으로 적대 에이전트를 격리하여 단일 에이전트 기준선 수준으로 점수를 회복시켰다.
**MMLU 협력 설정**: 7개 역할 기반 IO 에이전트에 엣지 최적화를 적용하여 5 training seed 평균 **+2.1% ± 1.1%** 개선을 달성했다.
**Mini Crosswords 베이스라인**: 20문제 서브셋, 초기 확률 θ=10%, 학습률 α=0.4, M=20, GPT-3.5-Turbo(temperature 0)에서 초기 분포 **0.465 ± 0.0509** → 10회 반복 후 **0.575 ± 0.0275** (3 run 평균).
**Mini Crosswords 밀도 대조**: 학습된 분포의 평균 엣지 수 **32.76 ± 1.93** vs 동일 밀도 무작위 분포 0.125 파라미터 분포 **32.80 ± 0.11**, 후자 정확도 **0.510 ± 0.0552** — 개선이 단순 엣지 증가가 아님을 확인.
**Mini Crosswords GPT-4-Turbo 평가**: 최적화된 분포를 GPT-4-Turbo로 평가 시 **0.800 ± 0.0616**으로 Tree of Thought(GPT-4) **0.675** 및 ToT(GPT-4-Turbo) **0.668** 대비 유의미한 초과.
**HumanEval**: ReAct 스타일 코드 생성 에이전트에 노드 프롬프트 최적화 적용, 최근 10개 입력에 대한 효과적 입출력 쌍을 demonstration으로 선택; 최적화 없음 **0.76** → 8회 반복 후 **0.88 ± 0.007** (online 학습 기준, 3 run 평균).
**GAIA 메인 결과**: 7×ToT + Self-Consistency 스웜으로 Level 1 **30.56% ± 3.25**, Level 2 **20.93% ± 1.27**, Level 3 **3.85% ± 2.43**, 평균 **18.45%**로 GPT-4-Turbo(9.70%) 대비 **90.2% 상대 향상**.
**GAIA 난이도별 상대 향상**: Level 1 +47.3%, Level 2 +260.2%, Level 3 변화 없음 — 고난도 추론은 여전히 과제로 남음.
**GAIA Ablation (Level 1 validation)**: IO 에이전트 16.60% → ToT 단일 에이전트 25.66% → 3×ToT Choose-Best 스웜 30.18% ± 4.30 → 7×ToT Self-Consistency 30.56% ± 3.25 (5 run 평균).
**GAIA 비용**: 7×ToT Self-Consistency 스웜의 쿼리당 평균 소요 시간 **~414.89초**, Human baseline ~422.26초에 근접 (단 Human 정확도 94%).
**도구 사용 빈도**: GAIA 태스크 중 **43.9%**가 웹 브라우징을 요구하여 웹 접근 능력 강화가 핵심 확장 방향으로 지목됨.

---

## Limitation

대규모 스웜에서 REINFORCE 기반 엣지 최적화는 분산이 크고 수렴이 느려, GAIA 실험에서는 엣지·노드 최적화를 적용하지 못하고 수동 자기일관성만 사용했다.
엣지 선택은 본질적으로 이산적이며 유틸리티 함수 u_τ가 비미분이므로 연속 완화에 의존하며, 매 반복마다 다수의 LLM 호출이 필요해 API 비용 부담이 크다.
한 번에 하나의 노드 프롬프트만 갱신하는 separation-of-concerns 가정은 노드 간 강한 상호작용이 있는 경우 최적성을 보장하지 않는다.
GAIA Level 3에서는 개선이 AutoGPT와 동일한 **3.85%**에 머물러, 다단계 장기 추론이 필요한 고난도 문제에는 현재 접근이 충분치 않다.
웹 탐색 구현이 문제 진술에 주어진 URL 직접 다운로드와 SearchApi 기반 Google 검색으로만 제한되어 심층 웹 네비게이션이 불가능하며, 이는 GAIA 성능 상한의 주요 원인이다.
DAG 제한으로 인해 반복적 루프(while loop 형태의 자기참조 에이전트 동작)는 현재 프레임워크로 모델링하기 어렵다.
벤치마크 평가 샘플 수가 Mini Crosswords 20문제, MMLU 검증셋 10% 등으로 제한적이며, 실제 배포 규모에서의 견고성은 추가 검증이 필요하다.

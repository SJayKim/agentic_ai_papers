# GPTSwarm: Language Agents as Optimizable Graphs

> **논문 정보**: Mingchen Zhuge, Wenyi Wang, Louis Kirsch, Francesco Faccio, Dmitrii Khizbullin, Jürgen Schmidhuber (KAUST, IDSIA)
> **arXiv**: 2402.16823 (2024.02)
> **학회**: ICML 2024 Oral (top 1.5%)
> **코드**: https://gptswarm.org

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트 시스템의 프롬프트와 토폴로지를 수동으로 설계해야 하며, CoT, ToT, ReAct, Reflexion 등이 서로 다른 코드베이스로 파편화되어 통합·자동 최적화하는 통일된 방법론이 존재하지 않는다. |
| **Motivation** | 에이전트 시스템을 계산 그래프(DAG)로 모델링하면, 각 노드(에이전트·도구)의 프롬프트와 엣지(정보 흐름)를 최적화 변수로 취급하여 자동으로 개선할 수 있다. 신경망 가중치 최적화와 유사한 메타러닝 패러다임이다. |
| **Limitation** | 대규모 에이전트 그래프에서 최적화 수렴이 느리다. 엣지 최적화가 이산적이라 미분 불가능하며, 매 반복마다 LLM 호출이 필요해 비용 발생. GAIA Level 3에서 개선이 미흡(3.85%). 웹 탐색이 URL 직접 접근과 단순 검색으로 제한. |

---

## Method

GPTSwarm은 에이전트 시스템을 DAG로 추상화하고, 노드·엣지 최적화를 동시에 수행한다.

### 1. 계산 그래프 정의
- **노드(Node)**: LLM 추론, 도구 호출, API 호출 등 기본 연산 단위
- **에이전트(Graph)**: 노드들로 구성된 DAG `G = (N, E, F, o)`. 각 노드는 선행 노드 출력과 입력을 받아 루틴 수행
- **스웜(Composite Graph)**: 여러 에이전트 그래프를 결합한 상위 구조. 에이전트 간 엣지가 통신 채널 정의

### 2. 엣지 최적화 (Edge Optimization)
- 가능한 연결 집합 `{e_i}^d`에 대해 포함 확률 `θ_i ∈ [0,1]`을 파라미터로 정의
- **REINFORCE 알고리즘**: M개 그래프를 샘플링 후 유틸리티 평가, gradient로 θ 업데이트
- Adam optimizer 사용, cycle 생성 엣지는 자동 제외

### 3. 노드 최적화 (Node Optimization)
- 각 노드의 프롬프트를 독립적으로 최적화 (separation of concerns)
- 반복 실행 중 입출력 이력 누적, OPRO 등 기존 프롬프트 최적화 방법 활용
- 효과적인 입출력 쌍을 선별하여 few-shot context 구성

### 4. 복합 최적화
- 엣지·노드 최적화를 독립적 또는 결합하여 수행
- 웹 검색, 파일 분석, 코드 실행, 인덱스 기반 메모리 등 다양한 도구 모듈과 결합 가능
- 기존 프롬프팅 기법들을 기본 노드 연산의 재조합으로 구현

---

## Key Contribution

1. **에이전트 시스템의 통합 그래프 추상화**: CoT, ToT, ReAct, Reflexion을 하나의 계산 그래프 표현으로 통일
2. **프롬프트 + 토폴로지 동시 자동 최적화**: 노드와 엣지를 함께 최적화하여 수동 설계 한계 극복
3. **REINFORCE 기반 엣지 최적화**: 적대적 에이전트 필터링, 최적 통신 패턴 자동 발견
4. **오픈소스 모듈형 프레임워크**: 기본 연산 노드의 재조합으로 다양한 에이전트 시스템 구축

---

## Experiment & Results

**MMLU (일반 지식 QA)**:
- 적대적 설정: 엣지 최적화가 적대 에이전트를 효과적으로 격리하여 단일 에이전트 기준선 성능 회복
- 협력 설정(7가지 역할): 단일 에이전트 대비 **+2.1% ± 1.1%** 향상

**Mini Crosswords**:
- REINFORCE 10회 반복 후 **0.575 ± 0.028** → GPT-4-Turbo 평가 시 **0.800 ± 0.062**
- Tree of Thought (GPT-4: 0.675) 대비 유의미한 초과
- 동일 엣지 수의 무작위 분포(0.510) 대비 우월 — 단순 밀도 증가가 아님을 확인

**HumanEval (코드 생성)**:
- 최적화 없음: **0.76** → 8회 반복 후 **0.88 ± 0.007**

**GAIA (실세계 QA)**:
- GPTSwarm(7×TOT + Self-Consistency): 전체 **18.45%** — GPT-4-Turbo 단독(9.70%) 대비 **90.2% 상대 향상**
- Level 1: 30.56% (GPT-4-Turbo 20.75% 대비 +47.3%)
- Level 2: 20.93% (GPT-4-Turbo 5.81% 대비 +260.2%)

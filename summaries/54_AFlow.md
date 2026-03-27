# AFlow: Automating Agentic Workflow Generation

> **논문 정보**: Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu 외 (DeepWisdom, HKUST-GZ, RUC, PKU, KAUST)
> **arXiv**: 2410.10762 (2024.10) | **게재**: ICLR 2025
> **코드**: https://github.com/FoundationAgents/AFlow

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 에이전틱 워크플로우 구축에 상당한 인간 노력이 필요하여 확장성과 일반화가 제한된다. DSPy는 수동 워크플로우 설정이 필수이고, GPTSwarm은 그래프 구조 한계로 다양성이 부족하며, ADAS는 선형 휴리스틱 탐색의 효율 한계로 제한된 반복 내에 효과적인 워크플로우를 찾지 못한다. |
| **Motivation** | 워크플로우를 코드로 표현된 LLM 호출 노드와 엣지의 그래프로 모델링하면 탐색 공간을 체계적으로 정의할 수 있다. MCTS로 이 공간을 효율적으로 탐색하되, 트리 구조가 과거 경험을 정확히 보존하여 반복 시 재활용 가능하게 한다. |
| **Limitation** | (1) MCTS 탐색 비용이 태스크 복잡도와 반복 횟수에 비례. (2) 탐색된 워크플로우가 검증 세트에 과적합 가능성. (3) 사전 탐색 방식으로 신규 태스크에 실시간 적응 불가. (4) 평가 함수가 명시적 추론 태스크에 한정. |

---

## Method

### 1. 워크플로우 형식화: 코드 기반 그래프
- 워크플로우 W를 LLM 호출 노드 N과 엣지 E로 정의
- 각 노드: Model M, Prompt P, Temperature τ, Output Format F
- 엣지 E는 코드(조건문, 루프, 순차 실행)로 표현 — 그래프 구조 대비 최대 표현력

### 2. 오퍼레이터: 재사용 가능한 빌딩 블록
- 7종: Generate, Format, Review & Revise, Ensemble, Test, Programmer, Custom
- 오퍼레이터 없이 Custom만으로도 기본 노드 구성 가능 (GSM8K 93.1%)

### 3. MCTS 기반 워크플로우 탐색 (4단계)
- **Soft Mixed Probability Selection**: 상위-k 워크플로우와 초기 템플릿 중 혼합 가중 확률로 시작점 선택. P_mixed(i) = λ·(1/n) + (1-λ)·softmax(α·scores). α=0.4, λ=0.2
- **LLM-Based Expansion**: 과거 경험(수정 이력, 예측 로그)을 활용해 Claude-3.5-sonnet이 자식 워크플로우 생성
- **Execution Evaluation**: 검증 세트에서 5회 실행하여 평균·표준편차 계산
- **Experience Backpropagation**: 성능, 수정 내용, 최적화 성공 여부를 부모 노드로 역전파

### 4. 탐색 공간 및 초기화
- Model, Temperature, Format 고정, 프롬프트 P와 코드 엣지 E에만 탐색 집중
- 빈 템플릿(단일 노드)부터 시작, 매 반복 단일 수정 적용
- 최대 20라운드 또는 n 라운드 연속 개선 없으면 조기 종료

---

## Key Contribution

1. **워크플로우 최적화를 코드 공간 탐색으로 형식화**: MCTS 기반 통합 프레임워크 최초 제안
2. **6개 벤치마크 전수 SOTA**: 수동 설계 대비 평균 +5.7%, ADAS 대비 +19.5%
3. **비용 효율**: AFlow 워크플로우로 소형 모델이 GPT-4o 능가, 추론 비용은 GPT-4o의 4.55%
4. **오퍼레이터 독립적 자율 발견**: 오퍼레이터 없이도 앙상블 유사 구조를 자율 발견

---

## Experiment & Results

- **벤치마크**: HumanEval, MBPP (코드), MATH lv5, GSM8K (수학), HotpotQA, DROP (QA)
- **비교**: IO, CoT, CoT SC, MedPrompt, MultiPersona Debate, Self-Refine, ADAS
- **실행 모델**: GPT-4o-mini, **최적화**: Claude-3.5-sonnet

**주요 결과**:

| 벤치마크 | AFlow | ADAS | CoT SC |
|---------|-------|------|--------|
| HotpotQA (F1) | **73.5** | 64.5 | 68.9 |
| DROP (F1) | **80.6** | 76.6 | 78.8 |
| HumanEval | **94.7** | 82.4 | 91.6 |
| MBPP | **83.4** | 53.4 | 73.6 |
| GSM8K | **93.5** | 90.8 | 92.7 |
| MATH lv5 | **56.2** | 35.4 | 50.4 |
| 평균 | **80.3** | 67.2 | 76.0 |

- ADAS 대비 MATH +20.8%p, MBPP +30.0%p
- **전이성**: GPT-4o-mini용 워크플로우 → GPT-4o 적용 시 HumanEval 96.2%
- **어블레이션**: 오퍼레이터 없는 AFlow도 GSM8K 93.1%로 모든 수동 설계 방법 능가

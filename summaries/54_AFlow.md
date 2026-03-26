# AFlow: Automating Agentic Workflow Generation

> **논문 정보**: Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu 외 (DeepWisdom, HKUST-GZ, RUC, PKU, KAUST)
> **arXiv**: 2410.10762 (2024.10)
> **코드**: https://github.com/FoundationAgents/AFlow

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전틱 워크플로우 구축에 상당한 인간 노력이 필요하여 확장성과 일반화가 제한된다. 기존 자동화 방법(DSPy, ADAS 등)은 초기 수동 설정이 필요하거나 워크플로우 다양성이 부족. |
| **Motivation** | 워크플로우를 코드로 표현된 LLM 호출 노드와 엣지의 그래프로 모델링하면, 탐색 공간을 체계적으로 탐색할 수 있다. MCTS로 이 공간을 효율적으로 탐색하면 수동 개입 없이 최적 워크플로우 발견 가능. |
| **Limitation** | 저자 언급: MCTS 탐색 비용이 태스크 복잡도에 비례. 독자 관점: 발견된 워크플로우가 특정 벤치마크에 과적합될 가능성. 실시간 적응이 아닌 사전 탐색 방식. |

---

## Method

1. **워크플로우 = 코드 기반 그래프**: LLM 호출을 노드로, 논리적 흐름/조건/의존을 엣지로 모델링
2. **오퍼레이터(Operators)**: Ensemble, Review & Revise 등 사전 정의된 재사용 가능한 에이전틱 연산 패턴을 빌딩 블록으로 활용
3. **MCTS 기반 탐색**: Soft mixed-probability selection → LLM-driven expansion → Execution evaluation → Backpropagation으로 워크플로우를 반복적으로 개선
4. **코드 수정을 통한 탐색**: 각 탐색 단계에서 워크플로우 코드를 직접 수정하여 새로운 구성 탐색

---

## Key Contribution

1. **워크플로우 최적화를 코드 공간 탐색으로 형식화**: MCTS로 무한한 워크플로우 공간을 효율적으로 탐색
2. **6개 벤치마크에서 SOTA**: 수동 설계 대비 +5.7%, 기존 자동화 대비 +19.5%
3. **비용 효율**: 작은 모델이 GPT-4o를 능가하면서 추론 비용 4.55%

---

## Experiment & Results

- **벤치마크**: HumanEval, MBPP, MATH, GSM8K, HotpotQA, DROP
- **비교**: IO, CoT, CoT SC, Self-Refine, ADAS 등

**주요 결과**: HotpotQA F1 73.5%(CoT 68.9%), MATH 56.2%(ADAS 35.4%), HumanEval pass@1 94.7%(ADAS 87.8%). 6개 벤치마크 전수에서 최고 성능. 작은 모델+AFlow 워크플로우가 GPT-4o 직접 사용보다 우수.

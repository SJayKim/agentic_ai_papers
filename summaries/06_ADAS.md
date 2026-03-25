# Automated Design of Agentic Systems (ADAS)

> **논문 정보**: Shengran Hu, Cong Lu, Jeff Clune (University of British Columbia, Vector Institute, Canada CIFAR AI Chair)
> **arXiv**: ICLR 2025
> **코드**: https://github.com/ShengranHu/ADAS

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 연구자들이 강력한 에이전트 시스템을 수동으로 설계하고 있지만, 머신러닝의 역사가 보여주듯 수동 설계는 결국 학습된 솔루션으로 대체된다. 에이전트 빌딩 블록(CoT, Self-Reflection, Tool Use 등)의 조합 공간이 방대하여 수동 탐색은 비효율적이다. |
| **Motivation** | NAS가 수동 CNN 설계를 대체했듯, 에이전트 시스템 설계도 자동화할 수 있다. 아직 발견되지 않은 빌딩 블록이 무수히 많고, 이를 효과적으로 조합하는 것은 수동으로 불가능하다. 코드 공간에서 에이전트를 정의하면 Turing Complete하므로 이론적으로 모든 가능한 에이전트 설계를 학습할 수 있다. |
| **Limitation** | (1) Meta Agent Search가 메타 에이전트로 GPT-4를 사용하므로 탐색 비용이 상당하다. (2) 발견된 에이전트의 해석 가능성은 코드로 보장되나, 왜 특정 설계가 작동하는지의 인과적 이해는 부족하다. (3) 평가가 비교적 좁은 벤치마크(ARC, DROP, MGSM 등)에 집중되어, 실제 복잡한 에이전트 태스크에서의 효과는 미확인. (4) 안전성 측면에서 자동 생성된 코드의 악의적 행동 가능성을 완전히 배제할 수 없다. |

---

## Method

ADAS는 **코드 공간에서 에이전트 시스템을 자동 설계**하는 연구 분야를 정의하고, 그 첫 번째 알고리즘인 **Meta Agent Search**를 제안한다.

1. **ADAS 프레임워크의 3대 구성요소**
   - **Search Space**: 에이전트가 코드로 정의되므로 프롬프트, 도구 사용, 워크플로우, 이들의 조합 모두 탐색 가능
   - **Search Algorithm**: FM이 메타 에이전트로서 코드를 작성하여 새 에이전트를 생성
   - **Evaluation Function**: 태스크별 정확도, 비용, 지연시간 등으로 후보 에이전트 평가

2. **Meta Agent Search 알고리즘**
   - 메타 에이전트(GPT-4)가 반복적으로 새로운 에이전트를 코드로 프로그래밍
   - 각 반복에서: (1) 이전 발견들의 아카이브를 참조하여 "흥미로운" 새 에이전트 설계 제안 → (2) 코드로 구현 → (3) 태스크에서 평가 → (4) 아카이브에 추가
   - 최대 5회까지 자동 리파인하여 에러 없는 코드 보장
   - 기존 수동 설계(CoT, Self-Refine, LLM Debate 등)를 초기 시드로 아카이브에 포함

3. **발견된 에이전트 패턴 예시**
   - **Structured Feedback and Ensemble Agent**: 5개 CoT → 다수 전문가 비평 → 반복 정제 → 앙상블
   - **Dynamic Memory and Refinement Agent**: 동적 메모리를 활용한 반복 정제
   - **Divide and Conquer Agent**: 문제를 하위 문제로 분할 후 전문가별 해결

기존 프롬프트 최적화(OPRO 등)가 프롬프트만 변경하는 것과 달리, ADAS는 워크플로우·도구·프롬프트 전체를 코드 수준에서 탐색한다.

---

## Key Contribution

1. **ADAS 연구 분야 정의**: 에이전트 시스템의 자동 설계라는 새로운 연구 방향을 체계화. 탐색 공간·알고리즘·평가 함수의 3대 구성요소를 명확히 정의.
2. **코드 공간 탐색**: 에이전트를 코드로 정의하여 Turing Complete한 탐색 공간 확보. 이론적으로 모든 가능한 에이전트 설계를 발견할 수 있는 잠재력.
3. **Meta Agent Search**: FM이 점진적으로 더 나은 에이전트를 프로그래밍하는 열린 탐색 알고리즘. 아카이브 기반 탐색으로 이전 발견을 누적 활용.
4. **교차 도메인·모델 전이**: 한 도메인에서 발견된 에이전트가 다른 도메인과 다른 모델에서도 우수한 성능을 유지하는 일반화 능력 실증.

---

## Experiment & Results

**ARC Challenge (GPT-3.5 평가)**:
- Meta Agent Search: 25회 반복에서 점진적으로 성능 향상, 최고 정확도 ~14% (CoT 6.0%, Self-Refine 6.7%, LLM Debate 4.0% 대비)
- Claude-Sonnet 전이 시 최고 에이전트 **48.3%** (CoT 25.3%, Self-Refine 39.3%)

**4개 도메인 벤치마크 (GPT-3.5)**:
- Reading Comprehension (DROP): F1 **79.4** vs CoT 64.2, Role Assignment 65.8 (+13.6)
- Math (MGSM): 정확도 **53.4%** vs LLM Debate 39.0% (+14.4%)
- Multi-task (MMLU): **69.6%** vs CoT 65.4%
- Science (ARC-Challenge): **34.6%** vs Self-Refine 31.6%
- 프롬프트 최적화(OPRO) 대비: DROP 79.4 vs 69.1, MGSM 53.4 vs 30.6

**교차 도메인 전이 (MGSM에서 발견된 에이전트)**:
- GSM8K: **69.1%** vs CoT 34.9% (+25.9%)
- GSM-Hard: **30.9%** vs Role Assignment 18.0% (+13.2%)
- 비수학 도메인(DROP, MMLU)에서도 수동 설계 대비 우위 유지

**교차 모델 전이 (ARC, GPT-3.5 → Claude-Sonnet)**:
- 최고 에이전트 48.3% vs CoT 25.3% — 모델 전환 후에도 큰 격차 유지

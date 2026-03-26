# τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

> **논문 정보**: Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra AI, Princeton University)
> **arXiv**: 2406.12045 (2024.06)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 에이전트 벤치마크는 도구-에이전트 상호작용만 평가하고, 실세계에서 필수적인 사용자와의 대화 + 정책 문서 준수를 함께 평가하지 못한다. |
| **Motivation** | 고객 서비스 시나리오에서 에이전트는 도구(API)를 사용하면서 동시에 사용자와 대화하고 회사 정책을 따라야 한다. GPT-4o조차 50% 미만의 성공률로, 이 복합적 요구가 현재 LLM의 핵심 도전. |
| **Limitation** | 저자 언급: 시뮬레이션된 사용자로 인한 실제 사용자 행동과의 괴리. 독자 관점: 항공/소매 2개 도메인에 한정. |

---

## Method

1. **현실적 시나리오 설계**: 항공사, 소매업의 고객 서비스 시나리오에서 에이전트가 도메인 특화 API + 정책 문서 + 시뮬레이션 사용자와 상호작용
2. **pass^k 신뢰성 메트릭**: k번 반복 시도 중 모든 시도를 통과하는 비율로, 에이전트의 안정성 평가
3. **3자 상호작용**: Tool(API) - Agent(LLM) - User(시뮬레이터) 간의 동시 상호작용 평가

---

## Key Contribution

1. **도구-에이전트-사용자 3자 상호작용 벤치마크**: 도구 호출 + 사용자 대화 + 정책 준수를 동시 평가하는 최초의 체계적 벤치마크
2. **pass^k 메트릭**: 단일 성공률이 아닌 반복 신뢰성을 측정하여 실세계 배포 적합성 평가

---

## Experiment & Results

- GPT-4o: 50% 미만 태스크 성공률 — 현재 최고 모델도 3자 상호작용에서 크게 부족
- 정책 준수와 도구 사용의 동시 요구가 핵심 병목

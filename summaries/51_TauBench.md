# τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

> **논문 정보**: Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra AI, Princeton University)
> **arXiv**: 2406.12045 (2024.06)
> **코드**: https://github.com/sierra-research/tau-bench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 에이전트 벤치마크는 도구-에이전트 상호작용만 평가하고, 실세계에서 필수적인 사용자와의 다턴 대화 + 도메인 정책 문서 준수를 함께 평가하지 못한다. 또한 에이전트의 일관성(reliability)을 단일 시도 성공률 외의 지표로 측정하지 않는다. |
| **Motivation** | 고객 서비스 시나리오에서 에이전트는 API 도구를 사용하면서 동시에 사용자와 대화하고 회사 정책을 따라야 한다. GPT-4o조차 τ-retail에서 61.2%, τ-airline에서 35.2% 성공률에 그치며, pass^8은 25% 미만으로 급락해 실세계 배포에 큰 도전임을 보여준다. |
| **Limitation** | (1) 시뮬레이션된 사용자가 실제 사용자의 행동을 완전히 대체하지 못함. (2) 항공사·소매 2개 도메인에 한정. (3) gpt-4-turbo FC 에이전트로 태스크를 튜닝해 데이터 편향 가능성. (4) pass^1 보상이 정책 위반 일부를 포착하지 못함. |

---

## Method

### 1. POMDP 기반 3자 상호작용 프레임워크
- 태스크를 POMDP (S, A, O, T, R, U)로 공식화
- 상태 공간 S = S_db ⊗ S_user: 에이전트는 데이터베이스와 시뮬레이션 사용자 양쪽과 동시 상호작용
- 에이전트는 도메인 정책 문서와 API 도구만 직접 접근 가능; 데이터베이스는 API 경유로만 읽기/쓰기

### 2. 벤치마크 구성 3단계
- **Stage I (수작업 설계)**: 실세계 대응 도메인의 DB 스키마, API, 정책 문서 설계. τ-retail: 7 write + 8 non-write API, τ-airline: 6 write + 7 non-write API
- **Stage II (LM 자동 생성)**: gpt-4로 DB 항목 대량 생성 (τ-retail: 500 users, 50 products, 1000 orders; τ-airline: 500 users, 300 flights, 2000 reservations)
- **Stage III (수동 검증)**: 사용자 지시문이 도메인 정책 하에서 단 하나의 DB 결과만 산출하도록 반복 검증. 각 태스크를 40회 이상 실행해 모호성 제거

### 3. 평가 방식: 데이터베이스 상태 비교
- 에피소드 종료 후 최종 DB 상태를 ground truth와 비교 (r_action)
- 에이전트 응답이 필요한 출력을 포함하는지도 평가 (r_output)
- 보상 r = r_action × r_output ∈ {0, 1}: 객관적이고 빠른 평가

### 4. pass^k 신뢰성 메트릭
- pass^k는 k번 i.i.d. 시도 모두 성공해야 하는 엄격한 지표 (코드 생성 pass@k와 반대)
- 수식: pass^k = E_task [C(c, k) / C(n, k)]
- 동일 태스크에 대해 사용자 LM과 에이전트 LM의 확률적 샘플링이 자연스러운 대화 변이를 생성

### 5. 에이전트 구현
- **Function Calling (FC)**: 매 턴 에이전트가 사용자 메시지 또는 도구 호출을 자율 결정
- **ReAct**: "Thought: {reasoning} Action: {JSON}" 형식
- **Act-only**: 추론 없이 행동만 출력
- 각 태스크 최대 30회 에이전트 액션으로 제한

---

## Key Contribution

1. **도구-에이전트-사용자 3자 상호작용 벤치마크 최초 제안**: 도구 호출 + 다턴 대화 + 도메인 정책 준수를 동시에 평가
2. **pass^k 메트릭**: 반복 신뢰성을 측정하여 실세계 배포 적합성을 정량 평가
3. **객관적 평가 체계**: DB 상태 비교로 LM judge 없이 빠르고 신뢰성 있는 평가
4. **실패 유형 분석**: Wrong argument(19.4%), Wrong info(25.0%), Wrong decision(22.2%), Partial resolution(33.3%) 4가지 패턴 체계적 분류

---

## Experiment & Results

- **모델**: gpt-4o, gpt-4-turbo, claude-3-opus, gpt-3.5-turbo, meta-llama-3-70B
- **도메인**: τ-retail (115 태스크), τ-airline (50 태스크)

**pass^1 (Function Calling)**:
- gpt-4o: retail 61.2% / airline 35.2% / avg 48.2%
- gpt-4-turbo: 57.7 / 32.4 / 45.1
- claude-3-opus: 44.2 / 34.7 / 39.5
- gpt-3.5-turbo: 20.0 / 10.8 / 15.4
- llama-3-70B: 14.8 / 14.4 / 14.6

**pass^k 급락**: gpt-4o FC τ-retail pass^1≈61% → pass^8<25% — 고성능 모델도 반복 일관성 취약

**방법론 비교**: FC > ReAct > Act-only 일관되게 우수

**정책 제거 ablation**: τ-retail gpt-4o 61.2%→56.8% (-4.4%), τ-airline 35.2%→10.8% (-24.4%) — 항공 도메인의 복잡한 ad-hoc 규칙이 핵심 도전

**실패 분석**: 부분 해결(33.3%) > 오정보(25.0%) > 잘못된 결정(22.2%) > 잘못된 인자(19.4%)

**할루시네이션**: gpt-4o FC 태스크당 비존재 ID 호출 0.46회, gpt-3.5-turbo Act 6.34회

**비용**: gpt-4o FC + gpt-4 사용자 시뮬레이션 τ-retail 1회 전체 ~$200

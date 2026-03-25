# Agent-Oriented Planning in Multi-Agent Systems

> **논문 정보**: Ao Li, Yuexiang Xie, Songze Li, Fugee Tsung, Bolin Ding, Yaliang Li (HKUST, Alibaba Group, Southeast University)
> **arXiv**: 2410.02189 (2024.10)
> **코드**: https://github.com/lalaliat/Agent-Oriented-Planning

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 다중 에이전트 시스템에서 메타 에이전트가 사용자 쿼리를 하위 태스크로 분해하고 적절한 에이전트에 할당하는 "에이전트 지향 계획(agent-oriented planning)"은 기존 프롬프트 기반 방법으로는 에이전트의 실제 능력과 서브태스크를 효과적으로 연결하지 못해 성능이 최적에 미치지 못한다. |
| **Motivation** | 예: "주석과 구리 100kg의 혼합물 녹는점을 800°C로 낮추려면?" 같은 쿼리를 "두 금속의 녹는점 확인"으로 분해하면 검색 에이전트가 두 엔티티를 동시에 처리하지 못할 수 있다. 에이전트의 능력 경계에 맞춘 세밀한 분해와 동적 수정이 필요하다. |
| **Limitation** | 저자 언급: 보상 모델 학습에 실제 에이전트 호출 데이터가 필요하여 초기 비용이 큼. 독자 관점: 보상 모델이 특정 에이전트 구성에 과적합될 수 있으며, 에이전트 추가/변경 시 재학습 필요성 미논의. 평가가 추론 벤치마크에 국한되어 실세계 멀티모달 태스크에서의 검증 부족. |

---

## Method

1. **3가지 설계 원칙**
   - **Solvability (해결 가능성)**: 각 서브태스크는 할당된 단일 에이전트가 해결 가능해야 함
   - **Completeness (완전성)**: 서브태스크 집합이 원본 쿼리의 모든 필수 정보를 포함해야 함
   - **Non-Redundancy (비중복성)**: 불필요하거나 중복된 서브태스크가 없어야 함

2. **Fast Decomposition & Allocation**
   - 메타 에이전트가 사용자 쿼리와 에이전트 설명을 함께 받아 서브태스크를 분해하고 에이전트를 할당
   - 태스크 간 의존 관계를 순차 구조로 명시
   - 분해·할당을 동시에 수행하여 효율성 확보 (분리 실행 대비 효과적)

3. **Reward Model 기반 Solvability 평가**
   - 실제 에이전트 호출 없이 서브태스크의 해결 가능성을 예측하는 보상 모델 학습
   - 평가 결과에 따라 3가지 분기: 실행 / 재계획(replan) / 상세 계획(plan-in-detail)
   - Representative Works 메커니즘: 에이전트의 과거 성공 사례를 참조하여 서브태스크-에이전트 적합성 판단

4. **Detector (완전성·비중복성 검사)**
   - 분해된 서브태스크에서 누락된 핵심 정보나 중복 내용을 식별
   - 메타 에이전트에 수정 제안을 전달

5. **Feedback Loop**
   - 에이전트 실행 후 결과를 메타 에이전트에 피드백하여 후속 서브태스크를 동적 조정
   - 실패 시 서브태스크 재설명(re-describe) 또는 추가 분해

---

## Key Contribution

1. **에이전트 지향 계획의 3대 설계 원칙**: Solvability, Completeness, Non-Redundancy를 체계적으로 정의하고, 이를 실현하는 프레임워크 제시
2. **보상 모델 기반 효율적 평가**: 실제 에이전트 호출 없이 서브태스크 해결 가능성을 예측하여 m×n 호출 비용을 회피
3. **동적 계획 수정**: 중간 결과에 기반한 피드백 루프와 재계획 메커니즘으로 기존 정적 분해의 한계 극복

---

## Experiment & Results

- **데이터셋**: HotpotQA, FEVER, TriviaQA 등 다중 에이전트 협업이 필요한 추론 벤치마크
- **에이전트 구성**: 검색 에이전트, 코드 에이전트, 상식 추론 에이전트 등
- **Baseline**: 단일 에이전트 시스템, ReAct, AutoGen, 기존 multi-agent planning

**주요 결과**:
- AOP가 모든 벤치마크에서 단일 에이전트 및 기존 MAS 계획 전략 대비 일관된 향상
- 보상 모델 도입으로 불필요한 에이전트 호출 감소 → 토큰 비용 절감
- Ablation: Detector 제거 시 완전성 하락, Reward Model 제거 시 해결 불가능한 서브태스크 비율 증가, Feedback Loop 제거 시 복잡 쿼리에서 성능 하락이 두드러짐

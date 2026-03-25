# ALMA: Learning to Continually Learn via Meta-learning Agentic Memory Designs

> **논문 정보**: Yiming Xiong, Shengran Hu, Jeff Clune (University of British Columbia, Vector Institute, Canada CIFAR AI Chair)
> **arXiv**: 2026.02
> **코드**: https://github.com/zksha/alma

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 파운데이션 모델의 추론 시 무상태성(statelessness)이 에이전트 시스템의 지속 학습을 병목한다. 기존 메모리 설계는 인간이 수동으로 구축하며 고정되어 있어, 다양하고 비정상적(non-stationary) 실세계 태스크에 적응하지 못한다. 도메인마다 최적의 메모리 구조가 달라, 인간이 일일이 설계하는 것은 비효율적이다. |
| **Motivation** | 코딩 에이전트는 유사 함수의 코드 스니펫을, 탐색 에이전트는 공간 지도와 위험 정보를 저장해야 하듯, 도메인마다 필요한 메모리 구조가 근본적으로 다르다. 기존 ADAS 등이 에이전트 아키텍처 전체를 탐색하지만 메모리의 지속 학습 능력을 명시적으로 최적화하지 않으므로, 메모리 설계에 특화된 메타 학습이 필요하다. |
| **Limitation** | (1) Meta Agent로 GPT-5를 사용하여 메모리 설계 탐색 비용이 상당하다 (11 learning steps, 43개 설계 탐색). (2) 4개 게임 환경에서만 검증되어 실세계 태스크(웹, 코딩 등)로의 전이는 미확인. (3) 발견된 메모리 설계가 특정 에이전트 프레임워크에 종속될 수 있어, 다른 프레임워크에서의 재사용성이 불확실하다. (4) 평가가 순차적 의사결정에 집중되어, 대화형·검색형 태스크에서의 효과는 미검증. |

---

## Method

ALMA는 **Meta Agent**가 메모리 설계를 실행 가능한 코드로 표현하고, 열린 탐색(open-ended exploration)을 통해 도메인에 최적화된 메모리 아키텍처를 자동 발견하는 프레임워크다.

1. **메모리 설계의 코드 표현**
   - 메모리 시스템을 Python 추상 클래스로 정의: `general_update`(메모리 수집), `general_retrieve`(지식 검색) + 내부 서브모듈(DB 스키마, 검색 로직 등)
   - 코드를 탐색 공간으로 사용하여 이론적으로 임의의 메모리 설계(DB 스키마, 검색/업데이트 메커니즘 포함) 발견 가능

2. **평가 프로토콜**
   - **Memory Collection Phase**: 빈 메모리에서 시작, 에이전트가 태스크를 수행하며 경험 축적 (검색 없이 수집만)
   - **Deployment Phase**: 수집된 메모리를 활용하여 새 태스크 해결. Static(고정 메모리) + Dynamic(동적 업데이트) 두 모드

3. **열린 탐색 루프 (Meta Agent)**
   - **Sample**: 아카이브에서 기존 메모리 설계와 평가 로그를 최대 5개 샘플링
   - **Ideate & Plan**: 샘플된 설계의 코드·평가 결과를 분석하여 개선 방향 도출
   - **Implement**: 새 메모리 설계를 코드로 구현
   - **Evaluate**: 에이전트 시스템에 통합하여 성능 측정 (성공률, 3회 평균)
   - **Store**: 새 설계와 평가 로그를 아카이브에 저장 → 향후 샘플링에 활용
   - GPT-5로 Meta Agent 구동, 11 learning steps에서 43개 메모리 설계 탐색

4. **발견된 설계의 특성**
   - 도메인별로 전혀 다른 메모리 구조 발견: ALFWorld는 Affordance Graph + Spatial Graph, Baba Is AI는 Strategy Library + Token Graph, MiniHack는 Risk/Interaction Memory + Spatial Experience
   - 각 설계가 해당 도메인의 고유한 지식 유형과 검색 패턴에 특화

---

## Key Contribution

1. **메모리 설계의 메타 학습**: 인간 수동 설계를 대체하여, Meta Agent가 코드 수준에서 메모리 아키텍처를 자동 탐색. 이론적으로 임의의 메모리 설계(DB 스키마 + 검색/업데이트 로직)를 발견 가능.
2. **지속 학습 최적화**: 기존 ADAS류가 일회성(one-shot) 성능만 평가하는 것과 달리, 메모리의 경험 축적·재활용을 통한 지속 학습 능력을 명시적으로 최적화.
3. **도메인별 특화 설계 발견**: 4개 벤치마크에서 각각 구조적으로 전혀 다른 최적 메모리 설계를 자동 발견하여, 범용 고정 설계의 한계를 실증.
4. **교차 모델 전이**: GPT-5-nano에서 학습한 메모리 설계가 GPT-5-mini에서 더 큰 개선을 보여, 메모리 설계의 모델 독립적 전이 가능성 확인.

---

## Experiment & Results

**벤치마크**: ALFWorld(가정 태스크), TextWorld(텍스트 어드벤처), Baba Is AI(규칙 조작 퍼즐), MiniHack(로그라이크 게임)

**비교 대상**: No Memory, Trajectory Retrieval, Reasoning Bank, Dynamic Cheatsheet, G-Memory

**주요 결과 (GPT-5-nano, 성공률%)**:
- ALMA: ALFWorld **12.4**, TextWorld **6.2**, Baba Is AI **19.0**, MiniHack **11.7**, 전체 평균 **12.3**
- 최고 수동 설계(G-Memory): 7.6, 2.1, 14.3, 6.8, 전체 평균 7.7
- No Memory: 2.9, 5.4, 9.5, 6.7, 전체 평균 6.1
- ALMA가 No Memory 대비 +6.2%p, 최고 수동 설계 대비 +4.6%p 향상

**GPT-5-mini 전이 (성공률%)**:
- ALMA: ALFWorld **87.1**, TextWorld **75.0**, Baba Is AI **33.3**, MiniHack **20.0**, 전체 평균 **53.9**
- 최고 수동 설계: 80.0, 68.8, 38.0, 16.7, 전체 평균 ~48.6
- No Memory 대비 +12.8%p. 더 강력한 모델에서 더 큰 delta(+6.6%p 추가) → 메모리 설계가 강한 모델을 더 잘 지원

**스케일링**: 메모리 수집 태스크 수 증가에 따라 ALMA가 수동 설계보다 더 빠르고 안정적으로 성능 향상 (Figure 4)

**비용 효율**: 대부분의 수동 설계 대비 낮은 토큰 비용으로 더 높은 성능 달성 (Figure 6)

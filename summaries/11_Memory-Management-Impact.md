# How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior

> **논문 정보**: Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Zirui Liu, Jiliang Tang, Himabindu Lakkaraju, Zhen Xiang (Harvard University, University of Georgia, Michigan State University, University of Minnesota)
> **arXiv**: 2025.05
> **코드**: https://github.com/yuplin2333/agent_memory_manage

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 메모리 관리(추가/삭제) 전략이 장기 성능에 어떤 영향을 미치는지 체계적으로 분석된 바 없다. 기존 메모리 시스템은 다양한 에이전트에 맞춰 특화 설계되어, 기본적인 추가·삭제 연산이 장기 동작에 미치는 영향에 대한 통합적 이해가 부족하다. |
| **Motivation** | 에이전트 메모리 뱅크는 동적(시간에 따라 변화)이고 노이즈가 많은(에이전트 자체 생성 출력 포함) 독특한 특성을 지닌다. 잘못된 경험이 메모리에 축적되면 오류 전파로 장기 성능이 점진적으로 악화될 수 있으며, 이는 정적 외부 지식 기반의 ICL 연구와 근본적으로 다른 문제다. |
| **Limitation** | (1) 4개 특정 에이전트(RegAgent, EHRAgents, AgentDriver, CIC-IoT Agent)에서만 검증되어, 더 복잡한 다단계 에이전트에 대한 일반화가 미확인. (2) Experience-following 속성이 모든 LLM에서 동일하게 발현되는지 충분히 검증되지 않았다(GPT-4o, DeepSeek-V3로 부분 확인). (3) 메모리 삭제 전략의 최적 주기·비율에 대한 이론적 프레임워크 부재. (4) 태스크 분포 변화 시나리오가 단순한 순차 도메인 전환에 한정. |

---

## Method

이 논문은 LLM 에이전트 메모리의 두 가지 기본 연산(추가·삭제)이 장기 성능에 미치는 영향을 실증적으로 분석한다.

1. **Experience-Following 속성 발견**
   - 현재 태스크 쿼리와 검색된 메모리 레코드 간 입력 유사도가 높으면, 에이전트 출력도 검색된 경험과 매우 유사해지는 현상
   - 메모리 크기가 커질수록 더 유사한 레코드가 검색되어 이 속성이 강화됨
   - 고정 메모리(Fixed-memory) 설정에서는 입력·출력 유사도 모두 낮아, 에이전트가 추론에 의존

2. **메모리 추가 분석**
   - **Add-all**: 모든 실행을 메모리에 추가 → 노이즈 축적으로 성능 저하
   - **Coarse 평가 (C1/C2/C3)**: 자동 평가기(GPT-4o-mini, GPT-4.1-mini, 파인튜닝 모델)로 선별 추가
   - **Strict 평가 (Human/Oracle)**: 정답 대비 검증으로 선별 추가
   - **핵심 발견**: 평가기 품질이 높을수록(Strict > C3 > C2 > C1 > Add-all) 장기 성능 향상. 실행 품질과 메모리 크기가 공동으로 성능 결정

3. **오류 전파 (Error Propagation)**
   - 잘못된 메모리 레코드가 검색되면 에이전트가 오류를 복제·증폭
   - 이 오류가 다시 메모리에 추가되면 미래 태스크에도 전파
   - Error-free 변형(ground-truth 출력 사용) 대비 즉각적 성능 갭 발생, Add-all/Coarse에서 갭이 시간에 따라 확대

4. **메모리 삭제 분석**
   - **Periodic Deletion**: 주기적으로 오래된 레코드 삭제 (FIFO)
   - **History-based Deletion**: 미래 실행에 도움이 되었는지 기록하여, 도움이 안 된 레코드 삭제
   - **Hybrid**: 두 전략 결합
   - **핵심 발견**: Trajectory 평가기를 삭제에도 활용하면, 미래 태스크 평가 결과가 "무료 품질 라벨"로 작동하여 메모리 품질 향상

5. **도전 시나리오**
   - **태스크 분포 변화**: 시간에 따라 태스크 도메인이 변하는 상황에서 메모리 관리의 중요성 증가
   - **메모리 자원 제약**: 제한된 메모리 용량에서 가장 가치 있는 경험만 유지해야 하는 상황

---

## Key Contribution

1. **Experience-Following 속성 정의**: LLM 에이전트가 메모리에서 검색된 경험을 강하게 모방하는 근본적 행동 패턴을 정량적으로 규명. 이 속성이 오류 전파와 잘못된 경험 재생의 원인임을 밝힘.
2. **오류 전파 메커니즘 실증**: 노이즈가 있는 메모리가 장기 성능을 점진적으로 악화시키는 과정을 구체적으로 보여줌. Add-all 방식이 Fixed-memory보다 오히려 나쁠 수 있음을 입증.
3. **Trajectory 평가기의 이중 역할**: 메모리 추가뿐 아니라 삭제에서도 평가기를 활용하는 것이 효과적이며, 미래 태스크 실행 결과가 기존 메모리의 품질 신호로 작용한다는 실용적 통찰.
4. **메모리 관리 설계 원칙**: 4개 에이전트·다양한 LLM에서 일관된 결과를 통해, 메모리 품질 관리가 메모리 크기보다 중요하다는 설계 원칙을 제시.

---

## Experiment & Results

**에이전트**: RegAgent(회귀 예측), EHRAgents(의료 기록 관리), AgentDriver(자율 주행), CIC-IoT Agent(IoT 보안)

**메모리 추가 (Table 1)**:
- RegAgent: Fixed 67.53 → Add-all **55.48** (악화), Strict **70.30** (향상)
- EHRAgents: Fixed 16.75 → Add-all 13.05 (악화), Strict **49.86** (3배 향상)
- AgentDriver: Fixed 40.11 → Add-all 32.32 (악화), C2 **40.06**, Strict **53.94** (향상)
- 패턴: Add-all은 모든 에이전트에서 Fixed보다 나쁨 → 노이즈 메모리의 해로움 확인

**Experience-Following**: 입력-출력 유사도 간 Pearson 상관 r≈1 (RegAgent), 메모리 크기 증가에 따라 상관 강화

**오류 전파**: Error-free 변형 대비 Add-all/Coarse에서 성능 갭이 시간에 따라 확대. Strict에서는 갭이 안정적이거나 심지어 역전(AgentDriver에서 ~2000 실행 후 ground-truth 초과)

**메모리 삭제**: History-based 삭제가 Periodic 삭제보다 우수. Hybrid가 가장 안정적.

**백본 모델**: GPT-4o, DeepSeek-V3에서도 동일한 experience-following 패턴 확인.

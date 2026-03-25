# AgentRefine: Enhancing Agent Generalization through Refinement Tuning

> **논문 정보**: Dayuan Fu, Keqing He, Yejie Wang, Wentao Hong, Zhuoma Gongque, Weihao Zeng, Wei Wang, Jingang Wang, Xunliang Cai, Weiran Xu (Beijing University of Posts and Telecommunications, Meituan)
> **arXiv**: ICLR 2025 (2025.01)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 에이전트 튜닝(Agent-FLAN, AgentGym 등)은 학습 환경(held-in)에서는 우수하지만 새로운 환경(held-out)으로의 일반화가 극히 부족하다. 포맷 오류, 비논리적 추론, 동일 오류 반복 등의 문제가 빈발하며, 이는 올바른 trajectory를 단순 암기하는 것에서 비롯된다. |
| **Motivation** | 기존 에이전트 모델은 환경이 명시적 부정 피드백을 제공해도 동일한 잘못된 행동을 반복한다 — 경험에서 학습하지 못하고 관찰-행동 쌍을 암기할 뿐이다. 자기 수정(self-refinement) 능력이 에이전트 일반화의 핵심이라는 가설을 세우고, 오류-수정 trajectory로 학습시키면 새 환경에서도 적응할 수 있다. |
| **Limitation** | (1) GPT-4o로 합성 데이터를 생성하므로, 데이터 품질이 GPT-4o의 능력에 의존. (2) Held-in 태스크(Alfworld)에서는 Agent-FLAN/AgentGym보다 낮은 성능 — 일반화를 위해 특화 성능을 일부 희생. (3) 합성 환경의 다양성이 실제 세계 복잡성을 완전히 반영하지 못할 수 있다. (4) Refinement 턴 수가 2회 이상으로 강제되어, 자연스러운 오류 분포와 다를 수 있다. |

---

## Method

AgentRefine는 합성 환경에서 **오류-수정 trajectory**를 생성하여, 에이전트가 실수에서 학습하는 능력을 튜닝하는 프레임워크다.

1. **데이터 생성 파이프라인 (TRPG 영감)**
   - **Script Generation**: 다양한 인간 페르소나(Chan et al.)에 기반하여 LLM이 환경·태스크·사용 가능 행동을 포함한 스크립트 생성
   - **Trajectory Generation**: LLM이 DM(Dungeon Master)과 Player 역할을 동시 수행
     - Player: ReAct 형식으로 사고(thought) + 행동(action) 생성
     - DM: Player의 행동을 관찰하고, 파라미터 오류·논리 오류·위치 오류를 판정
     - 오류 발생 시 오류 턴을 유지하고 LLM에게 환경 피드백에 기반한 수정(refine) 유도
   - **Verification**: 스크립트의 행동 유효성 코드 검증 + trajectory의 JSON 형식/완료 여부/오류-수정 턴 수(최소 2회) 검증

2. **Refinement Tuning**
   - DM의 관찰을 User로, Player의 사고+행동을 Assistant로 변환하여 multi-turn chat 형식으로 구성
   - **핵심: 오류 턴의 loss를 마스킹** — 모델이 잘못된 사고 과정을 학습하지 않도록 방지
   - 올바른 행동과 수정 행동에서만 학습 → "암기가 아닌 자기 수정" 능력 획득

3. **기존 방법과의 차이**
   - Agent-FLAN/AgentGym: 올바른 trajectory만 학습 → 패턴 암기 → 새 환경에서 적응 실패
   - AgentRefine: 오류+수정 trajectory 학습 → 환경 피드백에서 적응 → 새 환경에서 탐색적 문제 해결

---

## Key Contribution

1. **에이전트 일반화와 자기 수정의 상관 관계 규명**: 에이전트 일반화 능력이 올바른 행동 암기가 아닌 자기 수정 능력에서 비롯됨을 실증적으로 밝힘.
2. **합성 에이전트 환경 프레임워크**: TRPG에서 영감을 받아 다양한 페르소나 기반 에이전트 환경·태스크를 자동 생성, 수동 환경 구축의 한계 극복.
3. **오류 턴 loss 마스킹**: 오류 행동의 loss를 마스킹하는 것이 필수적임을 입증 — 마스킹 없이는 75% 성능 하락.
4. **Held-out 일반화**: 학습에 포함되지 않은 5개 태스크에서 기존 에이전트 튜닝 방법을 일관되게 초과.

---

## Experiment & Results

**모델**: LLaMA-3-8B, Mistral-7B, LLaMA-3-70B

**태스크 5개**: Alfworld(held-in for Agent-FLAN), BabyAI, SciWorld, PDDL, Jericho. AgentBoard 프레임워크로 평가.

**LLaMA-3-8B 결과 (Progress Rate)**:
- Held-out 평균: AgentRefine **40.8%** vs Agent-FLAN 20.5%, AgentGym 34.6%, LLaMA-3-8B-Instruct 40.1%
- Jericho: AgentRefine **32.3%** vs Agent-FLAN 10.1%, AgentGym 12.9% — 가장 큰 격차
- PDDL: AgentRefine **37.8%** vs Agent-FLAN 25.5%, AgentGym 16.6%

**Mistral-7B 결과**: AgentRefine가 held-out에서 Agent-FLAN(87.6→held-in but 6.7 held-out) 대비 압도적 일반화

**LLaMA-3-70B 결과**: AgentRefine가 Agent-FLAN(70B) 대비 SciWorld(46.4 vs 16.4), PDDL(58.6 vs 53.7)에서 우위

**Ablation (Table 2, 8K 데이터)**:
- w/o refinement loss(오류 마스킹 제거): 평균 36.1 → 전체 성능 하락
- w/o refinement data(수정 데이터 제거): 평균 35.0 → 수정 trajectory의 핵심 역할 확인
- w erroneous loss(오류 턴도 학습): 평균 **28.2** — 75% 하락, 오류 학습의 해로움 입증

**강건성**: 행동 설명 순서를 바꾸는 perturbation에서 AgentRefine만 안정적 성능 유지 (Agent-FLAN은 급락)

**스케일링**: 4K→64K 데이터 증가에 따라 성능 단조 증가 (Success 26.4→50.3, Progress 38.2→57.4)

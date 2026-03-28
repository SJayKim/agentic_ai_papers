# AgentRefine: Enhancing Agent Generalization through Refinement Tuning

> **논문 정보**: Dayuan Fu, Keqing He, Yejie Wang, Wentao Hong, Zhuoma Gongque, Weihao Zeng, Wei Wang, Jingang Wang, Xunliang Cai, Weiran Xu (Beijing University of Posts and Telecommunications, Meituan)
> **arXiv**: 2501.01702 (2025) | **학회**: ICLR 2025
> **코드**: https://agentrefine.github.io/

---

## Problem

오픈소스 LLM 기반 에이전트는 GPT-4 등 상용 모델과 비교해 여전히 큰 성능 격차가 존재한다. 기존 에이전트 튜닝(Agent-FLAN, AgentGym 등)은 학습 데이터와 동일한 환경(held-in)에서는 우수한 성능을 보이지만, 새로운 환경(held-out)으로의 일반화 성능이 크게 떨어진다. 분석 결과, 기존 모델들은 observation-action 매핑을 단순 암기하는 방식으로 학습하며, 학습 환경의 action 형식이 조금만 변경되어도 성능이 급락한다(Agent-FLAN: -30.4%, AgentGym: -25.6%). 한번 잘못된 행동을 출력하면 환경으로부터 명시적인 부정 피드백을 받아도 동일한 오류를 반복하는 "error loop" 현상이 관찰된다. 포맷 오류, 비논리적 추론, 중복 생성 등 다양한 일반화 실패 유형이 발생하며, general alignment 데이터 혼합으로도 이 문제를 근본적으로 해결하지 못한다.

---

## Motivation

에이전트의 일반화 능력은 단순히 정답 궤적을 암기하는 것이 아니라, 환경 피드백을 기반으로 자신의 실수를 인식하고 수정하는 자기 정제(self-refinement) 능력에서 비롯된다는 가설을 세운다. Reflexion, Self-Refine 등 선행 연구에서 영감을 받아, 에이전트 일반화와 self-refinement 사이의 상관관계를 규명하고자 한다. 좋은 에이전트는 새로운 환경에서 오류를 만났을 때 이전 행동을 수정하고 합리적인 탐색을 통해 올바른 행동 시퀀스를 발견할 수 있어야 한다. TRPG(Tabletop Role-playing Game)에서 영감을 받아, LLM이 DM과 플레이어 역할을 동시에 수행하며 오류-수정 과정을 포함하는 합성 데이터를 자동 생성하는 프레임워크를 제안한다.

---

## Method

1. **Script Generation (환경 스크립트 생성)**: Persona Hub에서 다양한 인간 페르소나를 샘플링하여 각 페르소나에 맞는 에이전트 환경을 생성. 위치, 아이템, 플레이어 정보를 JSON 형식으로 표현. 의도적으로 방해 위치/아이템을 포함시켜 오류 발생 가능성을 높인다.

2. **Trajectory Generation (궤적 생성)**: LLM이 Dungeon Master(DM)과 Player 두 역할을 동시에 수행하며 multi-turn 상호작용을 생성. DM은 thinking → observing → evaluating 3단계, Player는 ReAct 형식으로 Thought → Action을 수행. 각 턴 생성 후 verifier가 오류를 검출하면 해당 오류 턴을 유지하고 수정하도록 프롬프트.

3. **Verification (검증)**: 스크립트 검증(validation code로 action 이름 검사), 궤적 검증(JSON 오류, 태스크 미완료, action-validation 불일치). 오류-수정 턴이 2회 미만이면 재생성하여 충분한 refinement 과정을 보장.

4. **Refinement Tuning (정제 학습)**: 궤적을 SFT 데이터셋으로 변환(DM observation → user turn, Player thought+action → assistant turn). **Erroneous Loss Masking**: 오류 턴의 토큰에 대한 loss를 마스킹하여 잘못된 추론 과정을 학습하지 않도록 한다. 정상 턴과 수정 턴의 토큰만 학습 신호로 사용.

5. **데이터 규모**: 4K~64K 규모의 합성 데이터 생성, LLaMA3-8B/70B, Mistral-v0.3 등 다양한 모델에 적용.

---

## Key Contribution

1. **에이전트 일반화와 self-refinement 간의 상관관계를 최초로 규명**: 궤적 암기가 아닌 오류 수정 능력이 일반화의 핵심임을 실증.
2. **Refinement Tuning 패러다임**: 오류 턴을 포함한 궤적에서 오류 loss를 마스킹하는 새로운 학습 방식.
3. **TRPG 기반 합성 프레임워크**: 페르소나 기반으로 다양한 환경/태스크/궤적을 자동 생성하며 verifier로 품질 보장.
4. **강건성 향상**: held-in 환경의 action 형식 변형에 대해 기존 방법은 20~30% 하락하지만, AgentRefine는 오히려 3.7% 상승하며 표준편차 3.73%로 안정적.
5. **오픈소스 모델로도 합성 가능**: DeepSeek-v2.5로도 데이터 합성이 가능하여 상용 모델 의존도를 낮추는 경로 제시.

---

## Experiment & Results

- **평가 환경**: SciWorld, Alfworld(held-in), BabyAI, PDDL, Jericho의 5개 에이전트 태스크 + HotpotQA 추론 태스크.
- **Held-out 일반화 (LLaMA3-8B)**: SciWorld 14.4% vs Agent-FLAN 1.1% (+13.3%p), PDDL 16.6% vs 8.3% (+8.3%p), Jericho 32.3% vs 10.1% (+22.2%p).
- **Perturbation 강건성 (Alfworld)**: AgentRefine 48.5% (Std 3.73%) vs Agent-FLAN 36.9% (Std 21.98%) vs AgentGym 36.3% (Std 19.97%). Agent-FLAN은 67.2%→36.9%로 30.4%p 하락, AgentRefine는 44.8%→48.5%로 오히려 +3.7%p.
- **Ablation (8K)**: Refinement data 제거 시 SciWorld 33.1→21.3% (-11.8%p). Erroneous loss masking 미적용 시 33.1→19.0% (-14.1%p).
- **Best-of-N (N=10)**: Alfworld 93.3%, BabyAI 67.0%, SciWorld 40.0%으로 greedy 대비 평균 25%p+ 향상.
- **Scaling**: 데이터 4K→64K 시 Average Success Rate 26.4%→50.3%, Progress Rate 30.5%→57.4%.
- **HotpotQA**: AgentRefine EM 37.0%, F1 44.6% vs Agent-FLAN EM 24.6%, F1 32.4%.
- **오픈소스 합성**: DeepSeek-v2.5로 4K 데이터 합성 시 BabyAI 36.6% (Agent-FLAN 25.0% 대비 +11.6%p).

---

## Limitation

- Held-in 태스크(Alfworld)에서는 해당 환경에서 직접 학습한 Agent-FLAN(67.2%)이나 AgentGym(61.9%)에 비해 AgentRefine(44.8%)의 성능이 낮아, 특정 환경 최적화와 일반화 사이의 trade-off가 존재.
- 합성 데이터 생성에 GPT-4o를 사용하며, 오픈소스 모델 대체 시 성능 차이가 발생하여 강한 LLM 의존도가 남아 있다.
- 검증(verification)이 rule-based로 이루어져, 복잡한 논리/의미적 오류를 완전히 포착하지 못할 가능성이 있다.
- GPT-4 판별 정확도가 88%로, 약 12%의 오류 턴 분류 불일치가 데이터 품질에 영향을 줄 수 있다.
- 평가가 텍스트 기반 게임/시뮬레이션 환경에 집중되어, 웹 브라우징, 코드 생성 등 실제 에이전트 응용에의 일반화는 미검증.

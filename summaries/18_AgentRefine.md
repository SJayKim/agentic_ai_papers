# AgentRefine: Enhancing Agent Generalization through Refinement Tuning

> **논문 정보**: Dayuan Fu, Keqing He, Yejie Wang, Wentao Hong, Zhuoma Gongque, Weihao Zeng, Wei Wang, Jingang Wang, Xunliang Cai, Weiran Xu (Beijing University of Posts and Telecommunications, Meituan)
> **arXiv**: 2501.01702 (2025) | **학회**: ICLR 2025
> **코드**: https://agentrefine.github.io/

---

## Problem

오픈소스 LLM 기반 에이전트는 GPT-4 등 상용 모델과 비교해 여전히 큰 성능 격차를 보이며, 이를 줄이기 위한 에이전트 튜닝(agent-tuning) 연구가 활발히 진행되어 왔다.

그러나 Agent-FLAN, AgentTuning, AgentGym 등 기존 에이전트 튜닝 방법들은 학습 데이터와 동일한 환경(held-in)에서는 뛰어난 성능을 보이지만, 학습 시 보지 못한 새로운 환경(held-out)으로의 일반화 성능이 극히 저조하다.

저자들의 분석에 따르면 held-out 환경에서 기존 모델들은 포맷 오류(formatting error), 비논리적 추론(illogical reasoning), 중복 생성(duplicated generation) 등 다양한 실패 유형을 보이며, 이는 단순히 일반 정렬(alignment) 데이터를 혼합한다고 해결되지 않는다.

더 심각한 것은 "error loop" 현상으로, 모델이 한 번 잘못된 행동을 출력하면 환경이 명시적인 부정 피드백(예: "Nothing happens", "No known action")을 제공해도 동일한 잘못된 행동을 반복적으로 내뱉는다.

Alfworld 같은 held-in 태스크에서 action 표현만 살짝 변형해도(semantic은 동일하게 유지) 기존 방법들의 success rate가 급격히 하락하는 현상이 관찰되어, 이들이 실제 의사결정을 배운 것이 아니라 observation-action 매핑을 암기한 것임이 드러난다.

이러한 문제는 에이전트 튜닝 데이터가 제한된 수의 수동 제작 환경에 편중되어 있고, 궤적에 오류 수정(refinement) 과정이 포함되지 않아 발생하는 구조적 한계로 지목된다.

결국 진정한 일반화 가능한 오픈소스 에이전트를 구축하기 위해서는 궤적 암기가 아닌 다른 학습 패러다임이 요구된다.

---

## Motivation

저자들은 에이전트의 일반화 능력이 단순한 정답 궤적 암기가 아니라, 환경 피드백을 기반으로 자신의 실수를 인식하고 수정하는 자기 정제(self-refinement) 능력에서 비롯된다는 가설을 제시한다.

이 가설은 Reflexion(Shinn et al., 2024)과 Self-Refine(Madaan et al., 2024) 같은 선행 연구에서 영감을 받았으며, 좋은 에이전트는 새로운 환경에서 오류를 맞닥뜨렸을 때 이전 행동을 수정하고 합리적인 탐색을 통해 올바른 행동 시퀀스를 발견할 수 있어야 한다고 본다.

기존 Self-Refine 계열 연구들이 "답 생성 → 수정 요청 → 재생성"의 instance-level 강제 파이프라인으로 동작하는 반면, 저자들은 궤적 내부의 step-level에서 모델이 자발적으로 오류를 수정하도록 학습시키는 것이 일반화의 열쇠라고 본다.

그러나 오류-수정 과정을 포함하는 궤적을 수동으로 대규모 수집하는 것은 비현실적이므로, 합성 데이터(synthetic data) 기반의 대안이 필요하다.

이를 위해 저자들은 Tabletop Role-playing Game(TRPG)에서 영감을 얻어, 한 LLM이 Dungeon Master(DM)와 Player를 동시에 연기하며 오류와 수정을 자연스럽게 포함한 multi-turn 궤적을 생성하는 프레임워크를 고안한다.

또한 환경 다양성을 확보하기 위해 10억 개 페르소나를 담은 Persona Hub(Chan et al., 2024)를 활용하여 다양한 직업·관심사 기반 환경을 자동 생성함으로써 단일 시나리오에 대한 과적합을 방지한다.

이 접근은 환경 합성, 궤적 합성, 정제(refinement) 학습을 하나의 통합된 파이프라인으로 묶어 에이전트 일반화 연구에 새로운 패러다임을 제시하려는 목적을 가진다.

---

## Method

1. **Persona 기반 스크립트 생성(Script Generation)**: Persona Hub에서 인간 페르소나 p_i를 샘플링한 뒤, LLM에게 해당 페르소나에 맞는 agent 환경(locations, items, player 정보)과 task, available actions를 담은 "script"를 생성하도록 프롬프트한다.

2. **계층적 JSON 환경 표현**: 위치/아이템 간 계층 관계를 JSON 형식으로 명시하며, 의도적으로 방해용(interfering) 위치·아이템을 포함시켜 trajectory 생성 시 오류가 자연스럽게 발생할 여지를 만든다.

3. **Action 스키마 정의**: 각 action마다 name, validation code(정규식 기반 rule), parameter 목록을 함께 생성하여, 후속 verifier가 action 이름·파라미터의 유효성을 기계적으로 검증할 수 있게 한다.

4. **DM-Player 이중 역할 궤적 생성(Trajectory Generation)**: 하나의 LLM이 DM과 Player를 동시에 연기하는 TRPG 방식으로 multi-turn 궤적을 생성한다. DM 턴은 thinking → observing → evaluating의 3단계 구조이고, Player 턴은 ReAct(Thought → Action) 형식이다.

5. **DM의 오류 레이블링**: DM은 평가 단계에서 Player의 직전 action에 대해 parameter_error, place_error(잘못된 장소에서 수행), logic_error 세 종류 오류 여부를 boolean 필드로 기록한다.

6. **Verification**: 스크립트 검증(모든 action의 validation code가 파라미터 예시에 매칭되는지), 궤적 검증(특정 턴 t에서 JSON 포맷 오류·미완료·action-validation 불일치 등) 규칙을 rule-based로 수행한다.

7. **Error-Refine 턴 수량 제약**: 생성된 궤적의 error-refine 턴이 2회 미만이면 충분한 수정 과정이 없다고 판단하여 LLM에게 궤적 전체를 재생성하도록 요구하며, 4회의 LLM 호출 내에 verification을 통과한 궤적만 데이터로 저장한다.

8. **Refinement Tuning용 데이터 변환**: DM의 observation을 user turn, Player의 thought+action을 assistant turn으로 매핑하여 ReAct 형식 SFT 데이터셋 D_RT을 구성한다.

9. **Erroneous Loss Masking**: 학습 손실 J(θ)를 재정의하여, DM이 오류로 표시한 턴의 Player thought/action 토큰에 대한 loss를 마스킹한다. 이를 통해 모델은 정상 턴과 수정(refinement) 턴의 토큰만 학습 신호로 사용하게 된다.

10. **데이터 합성 모델**: 메인 실험에서는 gpt-4o-2024-05-13을 1-shot trajectory / 3-shot script 예시와 함께 사용하며, Appendix 실험에서는 DeepSeek-v2.5를 오픈소스 대안으로 활용한다.

11. **학습 하이퍼파라미터**: 학습률 5e-6, cosine 스케줄러, warm-up 없음, batch size 64, max length 8192(7/8B) 또는 4096(70B), 10 epoch 학습 후 best 체크포인트 선택.

12. **베이스 모델 다양성**: LLaMA3-8B, LLaMA3-70B, Mistral-7B-v0.3 등 다양한 아키텍처·스케일에 적용해 일반화를 검증한다.

13. **데이터 스케일링**: 4K, 8K, 16K, 32K, 64K 5단계로 데이터 규모를 변화시키며 성능 변화를 분석하여 합성 파이프라인의 확장성을 증명한다.

14. **평가 프레임워크**: AgentBoard를 기반으로 하되, 프롬프트를 Act-only에서 ReAct로 변경하고 히스토리 thought/action/observation을 plaintext가 아닌 chat format으로 재구성한다.

---

## Key Contribution

1. **에이전트 일반화-자기정제 상관관계의 최초 규명**: 궤적 암기보다 step-level self-refinement 능력이 held-out 일반화의 핵심 요인임을 ablation과 perturbation 실험으로 실증했다.

2. **Refinement Tuning 학습 패러다임 제안**: 오류 턴을 궤적에 의도적으로 포함시키되 해당 턴 토큰의 loss만 마스킹하는 새로운 SFT 방식을 도입해 "모델이 오류를 보되 학습하지 않게" 만들었다.

3. **TRPG 기반 전주기 합성 프레임워크**: Persona Hub → Script → DM+Player 이중 역할 궤적 → Verifier의 완전 자동 파이프라인으로 질의(환경)와 응답(궤적)을 동시에 합성하며 품질을 보장하는 최초의 시도다.

4. **강건성(robustness) 입증**: Alfworld action 재배열 같은 5종 perturbation에서 Agent-FLAN은 평균 30.4%p 하락하는 반면 AgentRefine는 오히려 +3.7%p 상승하고 표준편차도 21.98%→3.73%로 크게 개선됐다.

5. **Diversity 개선**: t-SNE 시각화와 Best-of-N 실험을 통해 AgentRefine 모델의 thought가 Agent-FLAN·AgentGym보다 훨씬 다양하게 분포함을 정량화했고, BoN 대비 greedy 평균 격차가 25%p+로 가장 크다는 결과를 얻었다.

6. **오픈소스 합성 모델 성공**: GPT-4o 대신 DeepSeek-v2.5로 데이터를 합성해도 Agent-FLAN을 held-out에서 능가하여 상용 모델 의존도를 완화할 수 있음을 보였다.

7. **추론(HotpotQA) 태스크로의 전이**: 결정(decision-making) 태스크로 학습된 모델이 추론 태스크 HotpotQA에서도 EM 37.0 / F1 44.6으로 Agent-FLAN(EM 24.6)을 큰 폭으로 능가해 정제 능력이 도메인을 넘어 전이됨을 보였다.

---

## Experiment

- **평가 환경**: SciWorld, Alfworld(held-in), BabyAI, PDDL, Jericho 5개 의사결정 태스크 + HotpotQA 추론 태스크로 구성되며, AgentBoard에서 Held-out Score = (BabyAI×112 + SciWorld×90 + PDDL×60 + Jericho×20)/282의 가중 평균으로 계산한다.

- **Held-out 일반화 (LLaMA3-8B)**: SciWorld Success 14.4% vs Agent-FLAN 1.1% (+13.3%p), PDDL 16.6% vs 8.3% (+8.3%p), Jericho 32.3%(Progress) vs 10.1% (+22.2%p), BabyAI 37.5% vs 25.0%로 held-out 전 영역 우위.

- **Mistral-7B 시리즈**: AgentRefine Alfworld Success 51.4%로 Agent-FLAN 77.6%보다 낮지만, held-out인 PDDL에서 11.7% vs 0%, Jericho에서 5.0% vs 0%로 일반화 격차가 뚜렷하다.

- **LLaMA3-70B 시리즈**: AgentRefine이 PDDL Success 38.3%, SciWorld 17.7%, Jericho 15.0%로 Agent-FLAN(25.0%, 5.5%, 0.0%)을 모두 상회한다.

- **Perturbation Robustness (Alfworld, 5종 변형)**: AgentRefine 평균 Success 48.5% (Std 3.73) vs Agent-FLAN 36.9% (Std 21.98) vs AgentGym 36.3% (Std 19.97). Agent-FLAN은 67.2%→최저 1.5%까지 떨어지지만 AgentRefine는 44.8~54.5% 구간에 안정적으로 머문다.

- **Ablation (8K)**: AgentRefine 평균 기반에서 refinement loss masking 제거 시 SciWorld Success 7.7%→4.4%, Alfworld 48.5%→40.3%로 하락. Refinement 데이터 전체 제거 시 BabyAI 37.1%→30.4%, PDDL 21.7%→11.7%로 하락. Erroneous 토큰 학습(masking 역전) 시 SciWorld는 약 75% 상대 드롭으로 7.7%→3.3%까지 급락.

- **Best-of-N (N=10, T=1)**: AgentRefine Alfworld Success 44.8→93.3% (+48.5%p), BabyAI 37.5→67.0% (+29.5%p), SciWorld 14.4→40.0% (+25.6%p), PDDL 16.6→30.0%, Jericho 10.0→25.0%로 평균 개선 폭이 25%p+에 달한다.

- **Scaling**: 4K→64K 학습 데이터 증가에 따라 Average Success Rate 26.4→30.6→33.9→(중간)→50.3%, Average Progress Rate 30.5→38.2→43.5→47.5→57.4%로 지속 상승.

- **HotpotQA 추론 태스크**: AgentRefine EM 37.0 / F1 44.6으로 LLaMA3-8B-Instruct(29.3/36.6), AgentGym(28.0/37.4), Agent-FLAN(24.6/32.4)을 모두 능가.

- **Reflexion 결합**: AgentRefine+Reflexion은 Alfworld Success 90.3%로 AgentGym+Reflexion(86.5%), Agent-FLAN+Reflexion(83.1%)을 넘으며, held-out인 Jericho에서도 10.0%로 유일하게 양의 성능을 유지한다.

- **오픈소스 합성 (DeepSeek-v2.5, 4K)**: BabyAI Success 36.6% (Agent-FLAN 25.0% 대비 +11.6%p), PDDL 16.6% vs 8.3%, Jericho 5.0% vs 0% — GPT-4o 합성 대비 소폭 하락하지만 베이스라인을 명확히 능가한다.

- **GPT-4 Judgement 신뢰도**: 오류 턴 판별에서 GPT-4와 인간 평가 일치율이 88/100 (TP 47, TN 41, FP 9, FN 3)로 데이터 품질이 합리적 수준임을 검증.

- **IND Filtering**: Agent-FLAN에서 IND 672/34440, AgentGym에서 IND 5350/14485 샘플 제거 시 held-in Alfworld Success가 각각 1.5%, 5.9%까지 붕괴하지만 AgentRefine은 44.8%로 유지되어 근본적 일반화 능력 차이를 시사.

---

## Limitation

- Held-in 태스크(Alfworld)에서는 동일 환경을 직접 학습한 Agent-FLAN(67.2%)이나 AgentGym(61.9%)에 비해 AgentRefine(44.8%)이 뒤처져, 특정 환경 최적화와 일반화 사이에 명확한 trade-off가 존재한다.

- 메인 실험의 합성 데이터가 gpt-4o-2024-05-13에 의존하며, DeepSeek-v2.5로 대체했을 때 Alfworld Success 36.6%→32.0%, SciWorld 11.1%→2.2% 등 눈에 띄는 성능 하락이 발생해 강한 LLM 의존도가 남아 있다.

- Verification이 정규식과 규칙 기반으로만 이루어져, 의미적(logical) 오류나 미묘한 task 불일치를 완전히 포착하지 못할 가능성이 있고, 결과적으로 잘못 레이블된 오류 턴이 학습에 포함될 수 있다.

- GPT-4 기반 오류 턴 판정의 인간 일치율이 88%에 그쳐 약 12%의 분류 오류가 데이터셋에 내재되며, 이는 Refinement Tuning의 loss masking 정확도에 직접적인 영향을 미친다.

- 평가가 주로 텍스트 기반 게임/시뮬레이션(AgentBoard)에 국한되어 웹 브라우징, GUI 조작, 코드 실행 같은 실제 응용 영역으로의 일반화는 본 논문에서 검증되지 않았다.

- Persona Hub 기반 환경 합성이 다양성을 확보하지만, 생성된 환경이 실세계 물리·인과 구조를 얼마나 반영하는지에 대한 정량적 검증은 부족하다.

- Erroneous loss masking이 강력한 효과를 보이지만, 일부 선행 연구(Ye et al., 2024)와 반대되는 결론이어서 언제 "오류에서 배우기"가 유효하고 언제 "오류를 마스킹"해야 하는지에 대한 일반 이론이 미제시 상태로 남아 있다.

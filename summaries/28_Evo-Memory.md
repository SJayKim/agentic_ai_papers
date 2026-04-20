# Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory

> **논문 정보**: Tianxin Wei, Noveen Sachdeva, Benjamin Coleman, Zhankui He 외 (UIUC, Google DeepMind)
> **arXiv**: 2511.20857 (2025.11)
> **코드**: N/A

---

## Problem

LLM 에이전트의 장기 계획과 문제 해결을 위해서는 statefulness가 필수이며, 메모리는 이를 가능케 하는 핵심 요소이지만 관리·진화 메커니즘에 대한 연구는 크게 부족하다.

기존 평가들은 대부분 정적 대화 상황에 집중되어 있어, 메모리가 단순히 대화에서 수동적으로 검색되어 질의에 응답하는 역할에 머문다.

이는 진화하는 태스크 스트림에 걸쳐 경험(experience)을 축적하고 재사용하는 동적 능력을 간과한다.

실세계 환경, 예컨대 대화형 문제 해결 어시스턴트나 체화 에이전트(embodied agent)에서는 LLM이 연속적인 태스크 스트림을 처리해야 하지만, 축적된 상호작용에서 학습하지 못해 귀중한 맥락적 통찰을 잃어버리는 한계가 있다.

즉, 에이전트는 "무엇이 말해졌는지(what was said)"는 기억해도 "무엇을 배웠는지(what was learned)"는 기억하지 못한다.

기존 StreamBench는 순차 학습을 평가하지만 사실 유지에만 집중하고 추론·궤적 재사용을 측정하지 않으며, LifelongBench는 환경·스킬 간 평생 학습을 다루지만 메모리 구조나 업데이트를 모델링하지 않는다.

따라서 메모리 기법들이 현실적인 스트리밍 시나리오에서 이력 전략(historical strategies)을 어떻게 검색·통합·진화시키는지를 통합적으로 평가하는 프레임워크가 부재하다.

---

## Motivation

Conversational recall은 과거의 사실(예: 2x²+3x−1=0의 해)을 검색하는 반면, experience reuse는 향후 태스크를 위한 추론 전략(예: 이차방정식 공식을 사용하는 방법)을 추상화하는 질적으로 다른 능력이다.

이러한 재사용이 없으면 모델은 유사 문제를 반복적으로 풀어야 하며, 장기 어시스턴트가 맥락은 회상해도 세션 간 적응에 실패하는 현상으로 이어진다.

테스트 시점 적응(TTA)에서 출발한 test-time learning 연구는 continuous self-improvement로 확장되고 있으며, reflection·planning·self-evolution을 통해 에이전트가 자율적으로 계획을 수정하고 피드백을 합성하는 방향으로 발전 중이다.

LLM 메모리 시스템 또한 단순 버퍼에서 policy-driven control(무엇을 저장·검색·덮어쓸지 결정)과 구조화된 관계적·절차적 표현으로 진화하고 있다(RepoGraph, MEM0, Zep, Dynamic Cheatsheets 등).

그러나 이러한 다양한 메모리 모듈을 통합된 프로토콜로 비교하고, 특히 "태스크 간 경험 재사용"을 명시적으로 테스트하는 벤치마크가 없어 발전 방향이 파편화되어 있다.

저자들은 정적 데이터셋을 순차적 태스크 스트림으로 재구조화하여 각 상호작용 후 메모리를 검색·적응·진화시키도록 요구하는 "test-time evolution" 평가 체계를 제안한다.

또한 단순한 ExpRAG 베이스라인과 정교한 ReMem 파이프라인을 함께 제공하여, 경험 재사용의 상한과 하한을 동시에 가늠할 수 있도록 설계 공간을 명시한다.

이를 통해 평가·프레임워크·방법론의 세 축에서 자기 진화 메모리 연구의 표준 참조점을 확립하는 것이 목표다.

---

## Method

1. **통합 에이전트 형식화**: 메모리 증강 에이전트를 (F, U, R, C) 튜플로 정의한다 — F는 기반 LLM, U는 메모리 업데이트 파이프라인, R은 검색 모듈, C는 검색 결과를 작업 컨텍스트로 변환하는 구성 메커니즘이다.

2. **Search–Synthesis–Evolve 루프**: 각 시점 t에서 입력 x_t와 메모리 M_t에 대해 R_t = R(M_t, x_t)로 관련 메모리를 검색하고, C̃_t = C(x_t, R_t)로 작업 컨텍스트를 합성한 뒤 ŷ_t = F(C̃_t)를 산출하고, m_t = h(x_t, ŷ_t, f_t)를 만들어 M_{t+1} = U(M_t, m_t)로 메모리를 진화시킨다.

3. **스트리밍 데이터셋 재구조화**: 기존 정적 데이터셋을 시퀀스 τ = {(x_1, y_1), ..., (x_T, y_T)}로 변환하여 초기 태스크가 이후 태스크의 전략에 기여할 수 있는 ground-truth 궤적을 구성하고, 예측 궤적 (x_1, ŷ_1, M_1) → ... → (x_T, ŷ_T, M_T)로 평가한다.

4. **데이터셋 스위트**: Single-turn 추론·QA로 MMLU-Pro, GPQA-Diamond, AIME-24/25, ToolBench를 포함하고, Multi-turn 체화 환경으로 AgentBoard 계열의 AlfWorld, BabyAI, ScienceWorld, Jericho, PDDL을 포함하여 총 10개 데이터셋을 동일 프로토콜로 평가한다.

5. **ExpRAG(Experience RAG) 베이스라인**: 각 메모리 항목을 m_i = S(x_i, ŷ_i, f_i)의 구조화된 경험 텍스트로 저장하고, 검색 점수 φ로 Top-k 경험을 뽑아 in-context learning 원리로 ŷ_t = F(x_t, R_t)를 생성한 뒤 M_{t+1} = M_t ∪ {(x_t, ŷ_t, f_t)}로 단순 append한다.

6. **ReMem(Think–Act–Refine) 제안**: ReAct의 두 축을 세 축으로 확장하여 각 스텝 t, 연산 n에서 a_t^n ∈ {Think, Act, Refine} 중 하나를 선택하고 o_t^n = Agent(x_t, M_t, a_t^n)으로 전이한다.

7. **세 연산의 역할**: Think는 내부 추론과 태스크 분해를 생성해 후속 행동을 가이드하고, Act는 환경에서 연산을 실행하거나 사용자에게 응답을 산출하며, Refine은 메모리에 대한 메타 추론을 수행해 유용한 경험을 활용하고 노이즈를 가지치기하며 M_t를 재조직한다.

8. **MDP 형식화**: 상태 s_t^n = (x_t, M_t, o_t^{1:n−1}), 행동 공간 {Think, Act, Refine}, 전이는 Agent 연산자와 환경 응답으로 주어지며, 스텝 내에서 Think와 Refine은 여러 차례 수행 가능하고 Act 선택 시 스텝이 종료된다.

9. **평가 지표 4종**: (1) answer accuracy(single-turn 정답률), (2) success rate와 progress rate(multi-turn 목표 달성), (3) step efficiency(목표 도달 스텝 수), (4) sequence robustness(태스크 순서 변동 하 안정성)로 학습·적응·재사용을 모두 측정한다.

10. **비교 기법 4범주**: 영구 메모리 없는 파이프라인(ReAct, A-Mem), 적응형 메모리(SelfRAG, MemOS, Mem0, LangMem), 절차적 지식 메모리(Dynamic Cheatsheet의 Cu/RS 변형, AWM), 제안 프레임워크(ExpRecent, ExpRAG, ReMem)로 구분하여 모두 동일한 search–predict–evolve 프로토콜로 평가한다.

11. **백본 모델**: Gemini 2.5 Flash/Flash-Lite/Pro와 Claude 3.5 Haiku/3.7 Sonnet 계열에서 평가하며, 피드백 f_t는 correctness 신호로 한정한다.

---

## Key Contribution

1. **Streaming 벤치마크 Evo-Memory**: 기존 정적 데이터셋을 태스크 스트림으로 재구조화하고 "conversational recall"과 "experience reuse"를 명시적으로 구분하여, 다양한 single-turn 및 multi-turn 태스크에 걸쳐 test-time evolution을 평가하는 최초의 통합 벤치마크를 제시한다.

2. **통합 평가 프레임워크**: 메모리 중심 지표(accuracy, success/progress rate, step efficiency, sequence robustness)와 (F, U, R, C) 형식화로 10개 이상의 메모리 모듈을 동일 프로토콜로 비교할 수 있는 재현 가능한 코드·설정을 공개한다.

3. **ExpRAG 베이스라인**: 단순한 태스크-수준 검색 증강만으로도 복잡한 적응형 메모리 시스템을 능가하는 경우가 많음을 보여, 경험 재사용의 효용을 실증하는 강력한 레퍼런스를 제공한다.

4. **ReMem 파이프라인**: ReAct의 Think-Act 루프에 Refine 차원을 추가해 추론·행동·메모리 진화를 단일 MDP로 통합하고, 메모리를 수동적 맥락에서 능동적 적응 컴포넌트로 전환한다.

5. **Task similarity 상관관계 정량화**: 데이터셋 내 태스크 유사도(임베딩 클러스터 중심과의 평균 cosine 거리)와 ReMem 개선폭 사이 Pearson r = 0.717(Gemini 2.5 Flash), r = 0.563(Claude 3.7 Sonnet)의 상관을 보고하여 메모리 진화에서 의미적 중첩의 중요성을 밝힌다.

6. **Sequence 난이도 효과 분석**: Easy→Hard vs Hard→Easy 순서가 메모리 적응에 영향을 미치며, ReMem은 Hard→Easy 방향에서 0.94/0.97 Success/Progress로 가장 견고함을 보인다.

7. **Failure-aware 메모리 통찰**: 성공·실패 경험이 혼재된 메모리에서도 ReMem이 선택적 활용으로 견고성을 유지함을 보여, 향후 failure-aware 메모리 진화 전략의 필요성을 제시한다.

---

## Experiment

LLM 백본은 Gemini 2.5 Flash/Flash-Lite/Pro와 Claude 3.5 Haiku/3.7 Sonnet이며, 비교 기법은 ReAct, A-Mem, SelfRAG, MemOS, Mem0, LangMem, DC-Cu, DC-RS, AWM, ExpRecent, ExpRAG, ReMem이다.

Single-turn 벤치마크(Claude 3.7 Sonnet 기준) 평균 성능은 Baseline 0.54, ReMem 0.58, ExpRAG 0.59로 개선폭이 중간 수준이지만, Gemini 2.5 Flash에서는 ReMem이 0.65로 Baseline 0.59 대비 상승하고 ToolBench에서 0.85/0.71 API 정확도를 기록한다.

Single-turn 세부로는 Claude 3.7 Sonnet 기준 ReMem이 GPQA 0.67, MMLU-Pro Eco. 0.86, ToolBench 0.87/0.71을 달성하며, ExpRAG도 GPQA 0.70, ToolBench 0.88/0.72로 경쟁력 있는 수치를 보인다.

Multi-turn 체화 환경에서 ReMem(Claude 3.7 Sonnet)은 평균 Success 0.78, Progress 0.91로 Baseline 0.24/0.52 대비 +0.54/+0.39의 극적 개선을 보이며, AlfWorld 0.92/0.96, BabyAI 0.73/0.83, PDDL 0.83/0.95, ScienceWorld 0.62/0.89를 달성한다.

Gemini 2.5 Flash 기준 multi-turn에서도 ReMem은 평균 0.50/0.64로 Baseline 0.27/0.46을 상회하며, 특히 AlfWorld에서 0.66/0.81, ScienceWorld에서 0.58/0.81의 강한 성능을 보인다.

Step efficiency 측면에서 ReMem은 AlfWorld에서 평균 22.6 스텝에서 11.5 스텝으로 약 49% 감소를 달성하여 추론 과정의 간결화 효과를 입증한다.

Task similarity와의 상관관계는 Pearson r = 0.717(Gemini 2.5 Flash), r = 0.563(Claude 3.7 Sonnet)으로, PDDL·AlfWorld처럼 임베딩 클러스터 비율이 높은 데이터셋이 더 큰 이득을 얻고 AIME-25·GPQA 같은 다양성 높은 데이터셋은 이득이 작다.

Sequence 난이도 실험(Table 3)에서 ReMem은 Easy→Hard 평균 0.77/0.92, Hard→Easy 평균 0.81/0.94로 두 방향 모두 안정적이며, 특히 AlfWorld Hard→Easy에서 0.94/0.97의 최고 성능을 기록한다.

Feedback 실험(Table 4)에서 실패 경험까지 저장했을 때 ReMem은 Claude 3.7 Sonnet 기준 AlfWorld 0.92/0.96, ScienceWorld 0.69/0.91, 평균 0.81/0.94로 견고하지만, baseline(A-Mem, SelfRAG, Mem0, DC-Cu/RS, AWM)은 0.40~0.45/0.74 수준에 머물러 노이즈 누적에 취약함을 보인다.

RQ5의 누적 성능 곡선에서 ReMem은 AlfWorld·BabyAI·PDDL·ScienceWorld 모두에서 History 베이스라인보다 빠른 적응과 안정적 유지를 보이며 장기 태스크 시퀀스에서 robustness를 입증한다.

전반적으로 Evolving-memory 방법들은 두 백본 모두에서 일관된 이득을 보이며, 특히 소형 모델에서 이득이 크게 나타나 test-time refinement가 경량 LLM 강화의 실용적 경로임을 시사한다.

---

## Limitation

저자가 명시한 한계로 MemOS와 LangMem은 체화 환경과 완전히 호환되지 않아 multi-turn 데이터셋 평가에서 제외되었으며, 이로 인해 모든 기법이 모든 도메인에서 비교되지 못한다.

피드백 f_t가 correctness 신호로 제한되어 있어, 부분 정답·정성적 피드백·보상 희소 환경에서의 검증이 부족하다.

태스크 유사도와 개선폭의 강한 상관(r = 0.717)은 도메인이 혼재되거나 유사도가 낮은 실세계 스트림에서는 ReMem의 이득이 축소될 수 있음을 시사한다.

Refine 연산의 추가는 각 스텝당 LLM 호출 수를 증가시키므로, 단순 ReAct 대비 토큰·지연시간 비용이 상승하지만 논문은 이를 정량적으로 명시하지 않는다.

실패 경험을 포함한 저장은 ReMem에서 견고하지만 여전히 AlfWorld S가 0.92에서 0.92로 유지되는 수준이며, 실패-인지 메모리 진화의 명시적 설계는 미완으로 남아 있다.

평가가 대체로 correctness가 명확한 벤치마크에 편중되어 있어, 창의적 생성·다중 정답 가능 태스크·개방형 사용자 상호작용에서의 일반화가 불투명하다.

MDP 형식화는 개념적으로 깔끔하지만 Refine 연산을 언제 멈출지에 대한 정책 학습이 명시적으로 제공되지 않아, 실제 구현에서는 프롬프트 수준의 휴리스틱에 의존한다.

마지막으로 벤치마크가 텍스트 기반 환경에 집중되어 있어, 멀티모달 관찰이나 실제 로봇 플랫폼 같은 넓은 체화 설정으로의 확장은 추가 연구가 필요하다.

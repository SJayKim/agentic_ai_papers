# MASS: Multi-Agent System Search — Optimizing Agents with Better Prompts and Topologies

> **논문 정보**: Han Zhou, Xingchen Wan, Ruoxi Sun, Hamid Palangi, Shariq Iqbal, Ivan Vulić, Anna Korhonen, Sercan Ö. Arık (Google, University of Cambridge)
> **arXiv**: 2502.02533 | **학회**: ICLR 2026
> **코드**: 미공개

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)은 복잡한 태스크에서 단일 에이전트 대비 성능을 향상시키지만, 효과적인 MAS를 새로운 도메인에 맞추어 설계하는 작업은 본질적으로 매우 어렵다.

단일 에이전트가 이미 가지는 프롬프트 민감성(prompt sensitivity)이 다중 에이전트가 캐스케이드(cascade)로 연결될 때 복합적으로 증폭되어, 프롬프트의 작은 변화가 시스템 전체의 급격한 성능 저하로 이어진다.

여기에 더해 에이전트를 어떻게 연결할지를 결정하는 토폴로지(topology) 설계는 대부분 수동 시행착오에 의존하고 있으며, 이는 상당한 실험 비용과 전문가 개입을 요구한다.

결과적으로 MAS 최적화 문제는 무한에 가까운 프롬프트 공간과 조합적으로 폭발하는 토폴로지 공간을 동시에 탐색해야 하는 이중 최적화 문제가 된다.

기존 자동화 연구들은 설계 공간의 한쪽 측면에만 집중해 왔다: DSPy는 프롬프트 엑젬플러 설계를 자동화하고, More-Agents는 에이전트 수 스케일링만 다루며, ADAS는 LLM 메타 에이전트로 새로운 토폴로지 코드를 생성하고, AFlow는 사전 정의된 연산자 위에서 MCTS로 토폴로지를 탐색한다.

그러나 이들 중 어느 것도 프롬프트 설계 공간과 토폴로지 설계 공간의 상호작용을 체계적으로 다루지 않아, MAS 성능 향상에 무엇이 가장 중요한지는 여전히 불분명한 상태였다.

특히 사전 정의된 연산자의 프롬프트가 최적화되지 않은 채 토폴로지만 탐색될 경우 “잘못된 프롬프트를 가진 에이전트들”이 누적적으로 전체 시스템을 악화시킬 수 있다.

이러한 격차로 인해 “MAS 설계에서 실제로 중요한 요소는 무엇이며, 이를 효율적으로 자동 탐색할 수 있는가?”라는 질문이 미해결 과제로 남아 있었다.

---

## Motivation

저자들은 최적화 알고리즘을 제안하기 전에, MAS 설계 공간 자체의 특성을 정량적으로 분석하는 데서 출발한다.

첫 번째 관찰은 블록 레벨 분석에서 나온다: MIPRO로 프롬프트만 최적화한 단일 CoT 에이전트가, 동일한 추론 토큰 예산 하에서 Self-Consistency, Self-Refine, Multi-Agent Debate 같은 에이전트 수 스케일링 방식보다 일관되게 더 높은 MATH 정확도를 달성한다.

즉 “에이전트 수를 늘리는 것”보다 “각 에이전트의 프롬프트를 잘 최적화하는 것”이 토큰 효율성 측면에서 훨씬 강력하며, 프롬프트 최적화 이후 Self-Consistency를 얹을 때에야 비로소 스케일링이 다시 유의미해진다.

두 번째 관찰은 워크플로우 레벨 분석이다: HotpotQA와 LiveCodeBench에서 다양한 토폴로지를 APO 상태에서 평가했을 때, 일부 토폴로지(예: debate)만이 +3% 수준의 이득을 제공하고 다른 토폴로지(예: Reflect)는 -15%까지 성능을 오히려 악화시킨다.

이는 유익한 토폴로지가 전체 탐색 공간의 극히 일부에 불과하며, 무조건 복잡한 토폴로지를 조합하는 접근이 오히려 해로울 수 있음을 의미한다.

이 두 관찰은 NAS(Neural Architecture Search) 연구에서 “탐색 알고리즘보다 탐색 공간 설계가 더 중요하다”는 기존 통찰과 정확히 병렬을 이룬다.

따라서 저자들은 MAS 최적화를 (a) 개별 에이전트를 먼저 프롬프트 수준에서 최적화하고 (b) 영향력 있는 토폴로지만 남긴 가지치기된 공간에서 탐색하며 (c) 마지막으로 워크플로우 전체를 공동 프롬프트 최적화하는 local-to-global, prompt-to-topology 순서의 다단계 문제로 재정식화한다.

이러한 분해는 조합 폭발을 각 단계의 관리 가능한 최적화 문제로 환원시키며, 영향력 기반 가지치기는 탐색 효율을 추가로 개선한다.

---

## Method

MASS는 플러그앤플레이 프롬프트 옵티마이저(MIPRO 기본)와 설정 가능한 토폴로지 공간 위에서 3단계 인터리빙 최적화를 수행하는 프레임워크이다.

1. **설계 공간 — 5가지 빌딩 블록 정의**: Aggregate(N_a개의 병렬 예측을 다수결/Self-Consistency로 합산), Reflect(N_r 라운드의 검증자 기반 반복 개선; Self-Refine·Reflexion에 해당), Debate(다자 토론으로 상호 비평), Summarize(N_s 라운드 요약으로 장문맥 처리), Tool-use(N_T∈{0,1} 이진 삽입 결정으로 RAG 리트리버나 코드 실행기 통합)로 구성된 통일 탐색 공간 A={a_i}를 정의한다.

2. **초기 Predictor 웜업(Single-Agent APO)**: 모든 단계의 기반이 되는 초기 예측 에이전트 a_0에 대해 MIPRO를 적용해 instruction과 1-shot exemplar를 공동 최적화하여 a_0* ← O_D(a_0)을 얻는다. MIPRO는 검증셋 성능을 기준으로 모델 자체의 정답 예측에서 few-shot을 부트스트랩하고, 데이터셋 요약·힌트로 다양한 instruction 후보를 제안한 뒤 instruction×demo 공간을 공동 탐색한다.

3. **Stage 1 — Block-level Prompt Optimization (1PO)**: 웜업된 a_0*를 고정한 채, 각 빌딩 블록 a_i를 최소 에이전트 구성(예: debate는 2 predictor + 1 debator)으로 축소하여 개별 프롬프트 최적화 a_i* ← O_D(a_i | a_0*)를 수행한다. 최소 구성에서 최적화하는 이유는 나중에 스케일 업될 때에도 최적 프롬프트가 유지되도록 하고 combinatorial 복잡도를 낮추기 위함이다.

4. **증분 영향력(Incremental Influence) 계산**: 각 블록의 최적화 후 검증 성능을 기록하여 I_{a_i} = E(a_i*) / E(a_0*) 비율을 산출한다. 이 값은 초기 단일 에이전트 대비 해당 빌딩 블록을 통합했을 때의 상대적 성능 이득을 정량화한다.

5. **Stage 2 — Workflow Topology Optimization (2TO, 선택 확률 산출)**: 영향력 I_a를 온도 t로 샤프닝한 Softmax(I_a, t)로 변환해 각 차원의 선택 확률 p_a를 얻는다. 저자들은 t=0.05로 설정하여 영향력 있는 차원이 거의 확정적으로 선택되도록 한다.

6. **Stage 2 — 확률적 가지치기 및 Rejection Sampling**: 각 a_i에 대해 u~Uniform(0,1)를 뽑아 u > p_{a_i}이면 거절, 아니면 수용하는 방식으로 가지치기된 탐색 공간 A_p를 형성한다. 그 위에서 전체 에이전트 수 N(a)가 예산 B를 넘지 않는 설정을 샘플링해 총 N=10개의 후보 워크플로우를 구성한다.

7. **Stage 2 — 규칙 기반 워크플로우 조립 및 평가**: 샘플링된 차원들을 사전 정의된 순서 규칙(중복 순열 제거)에 따라 W_c ← (a_i*, a_{i+1}*, …) 형태로 조립한다. 각 후보 워크플로우를 검증셋에서 3회 평가하여 가장 높은 점수의 W_c*를 선정한다.

8. **Stage 3 — Workflow-level Prompt Optimization (3PO)**: 선정된 W_c*의 전체 에이전트를 하나의 통합 엔티티로 간주하고 W* ← O_D(W_c*) joint prompt optimization을 수행한다. 이는 Stage 1에서 독립적으로 튜닝된 프롬프트들을 에이전트 간 상호의존성(한 에이전트 출력이 다른 에이전트 입력이 되는 관계)을 모델링하도록 재조정하는 파인튜닝 단계로 작동한다.

9. **실행 예산과 하이퍼파라미터**: bootstrapped demo는 에이전트당 최대 3개, instruction 후보는 10개, 최적화 라운드는 10회로 제한한다. 모델 temperature T=0.7, 최대 출력 4096 토큰, Softmax 샤프닝 t=0.05, 토폴로지 후보 수 N=10, 토폴로지당 검증 반복 3회. 동일 LLM 백본이 evaluator와 optimizer 역할을 겸한다.

10. **병렬성**: Stage 1과 Stage 2는 에이전트/토폴로지 간 독립적이므로 완전한 병렬 실행이 가능하며, 이는 ADAS·AFlow 같은 iterative 탐색 알고리즘 대비 wall-clock 효율의 본질적 이점이 된다.

---

## Key Contribution

1. **MAS 설계 공간의 최초 체계적 정량 분석**: 프롬프트 최적화가 에이전트 수 스케일링보다 토큰 효율적이고, 영향력 있는 토폴로지가 전체 공간의 작은 부분집합에 불과함을 2개 축의 실험(Fig. 2 token-accuracy, Fig. 4 per-topology)으로 실증했다.

2. **MASS — 3단계 인터리빙 최적화 프레임워크**: block-level PO(1PO) → topology optimization(2TO) → workflow-level PO(3PO)로 이어지는 local-to-global, prompt-to-topology 최적화 파이프라인을 제안해 조합 폭발 문제를 단계별로 분해한다.

3. **영향력 기반 탐색 공간 가지치기 기법**: 블록 단위 증분 영향력 I_a = E(a_i*)/E(a_0*)를 정의하고 Softmax(I_a, t)로 변환한 확률적 rejection sampling으로 열위 토폴로지를 자동 배제한다.

4. **플러그앤플레이 아키텍처**: MIPRO, TextGrad 등 임의의 프롬프트 옵티마이저와 커스텀 토폴로지 빌딩 블록(예: task-specific Summarize, Tool-use 실행기)을 자유롭게 교체/추가 가능한 모듈식 설계를 제공한다.

5. **실용적 MAS 설계 3원칙 도출**: (a) 개별 에이전트를 먼저 최적화하라, (b) 영향력 있는 토폴로지만 선택해 조합하라, (c) 워크플로우 레벨에서 에이전트 간 상호의존성을 공동 최적화하라.

6. **다중 모델·다중 태스크에서의 일관된 우수성**: Gemini 1.5 Pro/Flash, Claude 3.5 Sonnet, Mistral Nemo 4종 백본과 reasoning·multi-hop·long-context·coding 영역의 8개 벤치마크에서 ADAS·AFlow 대비 일관된 성능 우위를 재현했다.

---

## Experiment & Results

**평가 설정**: 주 실험은 Gemini 1.5 Pro/Flash (gemini-1.5-{pro,flash}-002)로 수행하고, Claude 3.5 Sonnet과 Mistral Nemo 12B로 핵심 결과를 재검증했다.

**벤치마크**: Reasoning(MATH, DROP), Multi-hop/Long-context(HotpotQA, MuSiQue, 2WikiMultiHopQA from LongBench), Coding(MBPP, HumanEval, LiveCodeBench test-output-prediction)의 총 8개.

**베이스라인**: CoT, CoT-SC(@9 agents), Self-Refine(2 agents @5 rounds), Multi-Agent Debate(3 agents @3 rounds + 1 judger), ADAS(LLM meta-agent), AFlow(MCTS). 모든 베이스라인은 쿼리당 comparable inference cost와 최대 에이전트 수 10으로 통제된다.

**Gemini 1.5 Pro 평균 정확도**: MASS **78.79%** vs Multi-Agent Debate 70.26% vs ADAS 69.72% vs Self-Consistency 68.18% vs CoT 65.28%.

**Gemini 1.5 Pro 태스크별 MASS 결과**: MATH **84.67%** (CoT 71.67, ADAS 80.00), DROP **90.52%** F1 (CoT 70.59, ADAS 72.96), HotpotQA 69.91, MuSiQue **51.40** (ADAS 41.95), 2WikiMQA 73.34, MBPP **86.50%** pass@1 (CoT 68.33, ADAS 73.00), HumanEval 91.67, LiveCodeBench **82.33%** (CoT 66.33).

**Gemini 1.5 Flash 평균**: MASS **74.30%** vs Multi-Agent Debate 65.91 vs ADAS 64.75 vs CoT 60.87. 더 작은 모델에서도 ADAS 대비 약 +9.5%p 향상.

**Flash 태스크별 하이라이트**: MATH 81.00% (CoT 66.67, Debate 71.67), DROP 91.68% F1, 2WikiMQA 76.69, LiveCodeBench 72.17% (CoT 51.17).

**단계별 기여 분해(8 태스크 평균, Gemini 1.5 Pro)**: CoT 63.5 → APO 68.0 → 1PO 74.2 → 2TO 77.3 → 3PO 78.8. 각 단계 증분은 APO +4.5%p, 1PO **+6.2%p**, 2TO **+3.1%p**, 3PO **+1.5%p**로, 1PO 단계의 기여가 가장 크다.

**Ablation(HotpotQA)**: 2TO만 단독 수행 시 성능이 약 3%p 하락, 가지치기 없이 2TO를 수행 시에도 약 3%p 하락하여 프롬프트 선행 최적화와 공간 가지치기가 모두 필수임을 확인했다.

**Optimization Trajectory(DROP, Fig. 6)**: MASS는 1PO → 2TO → 3PO 전 라운드에 걸쳐 단조 증가 궤적을 보이며 약 80라운드에서 90%+ F1에 수렴하는 반면, ADAS는 과도하게 복잡한 토폴로지를 생성해 조기 정체, AFlow는 MCTS 특성상 큰 분산을 보인다.

**병렬성 이점**: 1PO와 2TO 내부는 완전 병렬화 가능하여 실제 wall-clock 비용에서 iterative 베이스라인 대비 유리하다.

**모델 일반성**: Claude 3.5 Sonnet 및 Mistral Nemo 12B 백본에서도 일관된 향상이 관찰되어 기법이 특정 모델에 과적합되지 않음을 확인했다.

---

## Limitation

3단계 전체 파이프라인은 에이전트별 블록 최적화, 토폴로지 후보 10개×검증 3회, 워크플로우 공동 최적화 등 상당한 검증셋 평가와 LLM API 호출을 요구하여 대규모 실시간 배포 시 비용 부담이 크다.

토폴로지 조립이 사전 정의된 규칙 기반 순서로 이루어지므로, 에이전트 간 임의 그래프나 동적 라우팅 같은 자유 구조는 탐색 범위에 포함되지 않는다.

MIPRO를 기본 옵티마이저로 채택하기 때문에 프롬프트 옵티마이저 자체의 표현력과 탐색 한계가 MASS 전체 성능의 상한을 결정하게 된다.

Stage 1과 Stage 3 모두 레이블이 부여된 검증 분할에서의 metric 기반 최적화를 전제하므로, 지도 신호가 없거나 정답 정의가 모호한 open-ended 태스크로의 이식이 어렵다.

빌딩 블록이 Aggregate/Reflect/Debate/Summarize/Tool-use 5종으로 제한되어 계층적 위임, 동적 역할 전환, 장기 메모리 공유 같은 보다 복잡한 협력 패턴은 다루지 않는다.

모든 에이전트에 동일 LLM 백본을 사용하는 단일 모델 가정 하에서 검증되었으며, 이종(heterogeneous) 모델 조합이나 모델 선택 자체를 하이퍼파라미터로 포함하는 시나리오는 탐구되지 않았다.

증분 영향력 I_a가 초기 에이전트 a_0*에 조건화되어 계산되므로, 초기 웜업 품질이 낮을 경우 후속 단계의 선택 확률이 왜곡될 수 있고 특정 태스크에 대한 평가 노이즈에 민감할 수 있다.

저자들이 AFlow의 메타 프롬프트가 Claude 3.5 Sonnet에서만 제대로 동작하여 Gemini 실행기 + Claude 최적화기 혼합으로 재현했다고 명시하듯, 자동 MAS 설계 기법들 간의 공정 비교 자체가 프레임워크 호환성에 크게 의존하는 한계가 있다.

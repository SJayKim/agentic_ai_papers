# EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms

> **논문 정보**: Siyu Yuan, Kaitao Song, Jiangjie Chen, Xu Tan, Dongsheng Li, Deqing Yang (Fudan University, Microsoft Research Asia)
> **arXiv**: 2406.14228 (2024.06)
> **코드**: https://evo-agent.github.io

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)의 설계는 거의 전적으로 수작업에 의존한다.

MetaGPT, AutoGen, Camel, Generative Agents 같은 대표적 프레임워크는 캐릭터 역할, 태스크 범위, 스킬, 프롬프트를 인간이 미리 정의해야 동작한다.

이러한 수동 설계는 새 도메인이나 새 태스크가 등장할 때마다 프레임워크를 재설계해야 한다는 확장성 문제를 만든다.

자동 에이전트 생성을 시도한 AutoAgents는 "Planner - Agent Observer - Plan Observer" 구조를, AgentVerse는 "Expert Recruitment - Collaborative Decision Making - Action Execution - Evaluation" 파이프라인을 고정적으로 강제하여 여전히 인간 설계 개입이 필수이다.

이런 고정 아키텍처는 다룰 수 있는 태스크 범위를 제한하고, 특정 도메인에 맞게 에이전트 수를 자유롭게 확장하지 못하게 만든다.

결과적으로 "단일 전문 에이전트에서 출발해 자동으로 MAS로 확장하는 일반적(agent-framework-agnostic) 패러다임"이라는 연구 질문이 미해결로 남아 있다.

특히 인간 노동 비용이 커질수록 에이전트 수를 스케일업하여 성능을 끌어올리는 전략이 근본적으로 막힌다는 점이 핵심 병목이다.

저자들은 이 문제를 "handcrafted setting dependency"로 명명하고 이를 해소할 범용 생성 메커니즘을 목표로 설정한다.

---

## Motivation

인간 사회는 서로 다른 특성을 가진 다수의 개체로 구성되며, 이들을 선택·조율·협력시키면 복잡한 미션을 효율적으로 수행할 수 있다.

이는 진화 알고리즘(Evolutionary Algorithm, EA)의 reproduction/mutation/recombination/selection 메커니즘과 구조적으로 유사하다.

EA는 비모수(non-parametric) 최적화 방법으로, 프레임워크 구조에 구애받지 않고 "진화시킬 변수"와 "진화 연산자"만 정의하면 임의의 시스템에 적용 가능하다.

실제로 EvoPrompt(Guo et al., 2023), EvoPrompting(Chen et al., 2023a) 등은 이미 EA가 이산적 프롬프트·코드 최적화에 유효함을 보였다.

이로부터 "에이전트의 설정(역할, 스킬, 프롬프트)"을 진화 가능한 유전자로 간주하면, 수작업 없이 단일 에이전트로부터 다양한 전문 에이전트 집단을 번식시킬 수 있다는 가설이 세워진다.

특히 EA의 프레임워크 무관성은 MetaGPT·AutoGen·Camel·AgentVerse 같은 이종 프레임워크 위에 동일한 방식으로 얹을 수 있게 해준다.

이러한 관점은 "단일 에이전트 시점에서 one-shot으로 MAS를 파생시킨다"는 EvoAgent의 핵심 설계 철학을 형성한다.

---

## Method

EvoAgent는 기존 에이전트 프레임워크를 초기 개체로 간주하고, 진화 연산자를 T회 반복해 전문 에이전트 집단을 자동 생성하는 4-stage 파이프라인이다.

1. **Initialization**: MetaGPT, AutoGen, Camel 등 임의의 기존 프레임워크를 초기 부모 에이전트 A(0,0)로 지정한다.

2. **진화 변수 정의**: 역할(role), 스킬(skills), 프롬프트(prompts) 등 "무엇을 진화시킬 것인가"를 명시한다.

3. **Crossover (부모 결과 기반 보강)**: 부모 에이전트 {A'(0,t-1),...,A'(N-1,t-1)}가 사용자 요청에 대한 결과 R(i,t-1)을 생성하면, LLM이 이 결과에서 누락된 스킬을 식별하여 새로운 자식 에이전트 설정으로 업데이트한다. 예: 여행 계획 결과에서 숙박 정보 누락 감지 → Accommodation Agent 생성.

4. **Mutation (다양성 확보)**: N개의 부모로부터 N'(>N)개의 자식을 생성하되, LLM이 자식과 부모를 비교하여 자식을 명확히 구별되도록 수정한다. 태스크 해결 능력은 유지하면서 설정 다양성을 보장한다.

5. **Selection (Quality-Check)**: LLM 기반 quality-check 모듈이 모든 자식 후보와 이전 세대 누적 에이전트를 함께 평가한다. 부모 특성의 계승 여부, 부모와의 차별화, 기존 에이전트와의 중복 여부(예: 숙박 타입 중복 → 폐기)를 점검해 상위 N개를 선별한다.

6. **Results Update**: 선별된 N개 자식 에이전트가 각자 후보 결과 R(i,t)를 생성하고, LLM이 이전 세대 최종 결과 R(t-1)과 통합하여 새 최종 결과 R(t)를 도출한다. 이는 자연선택 단계에 해당한다.

7. **반복(T iterations)**: 2~6단계를 T회 반복하며 에이전트 집단을 점진적으로 진화시킨다. 각 세대에서 이전 세대 모든 에이전트가 다음 세대 비교 풀에 누적 추가된다.

8. **기본 구성 EVOAGENT(N,T)**: N은 이터레이션당 population size, T는 이터레이션 수. 주 실험 설정은 EVOAGENT(1,3) — 3회 이터레이션, 각 1개 신규 에이전트로 초기 에이전트와 함께 총 4개 에이전트 협업.

9. **Selection 전략 변형**: Random(무작위 1개), PK(동일 백본 LLM이 최적 선택), All-in(모든 후보 통합 사용) 세 가지를 제공한다.

10. **프레임워크 적용 예시**: MetaGPT 토론 시나리오에서는 두 팀 각각을 EvoAgent로 확장, Camel에서는 AI assistant 역할을, AutoGen에서는 group chat의 expert role을 자동 생성한다. 어느 경우에도 추가 수작업이 필요 없다.

---

## Key Contribution

1. **프레임워크 불가지론적 MAS 자동 생성**: 단일 전문 에이전트를 초기 개체로 삼아 어떠한 기존 프레임워크(MetaGPT, AutoGen, Camel, AgentVerse 등) 위에도 추가 설계 없이 적용되는 범용 multi-agent 생성 방법을 최초로 제시한다.

2. **에이전트 생성의 진화 파이프라인 형식화**: Initialization → Crossover → Mutation → Selection(Quality-Check) → Results Update의 5단계를 알고리즘 1로 정형화하고, 각 단계의 LLM 기반 연산자(Evo_Crossover, Evo_Mutation, Evo_Update, LLM_Quality)를 정의한다.

3. **Quality-Check 모듈 도입**: population size가 1을 넘을 때 중복·저품질 에이전트를 걸러내는 선택 모듈을 제공하여, N>1 설정에서 계획 품질 저하를 방지한다.

4. **광범위한 태스크·백본 검증**: 지식 QA(Logic Grid Puzzle, Trivia Creative Writing, Codenames), 멀티모달(MMMU), 인터랙티브 과학(ScienceWorld), 실세계 계획(TravelPlanner) 4개 영역과 LLaMA2-13B, Mistral-7B, GPT-3.5, GPT-4, GPT-4V, Gemini-Pro 6개 백본에서 일관된 향상을 입증한다.

5. **약한 LLM에서의 강건성**: SPP 등 기존 multi-persona prompting이 무력화되는 소형 모델에서도 EvoAgent는 일관된 개선을 보이며, 진화 기반 다양성이 모델 크기와 독립적으로 작동함을 보인다.

6. **실세계 프레임워크 확장 사례 제시**: MetaGPT debate, Camel role-playing, AutoGen group chat 세 실제 프레임워크에 부착하여 에이전트 수 스케일업이 가능함을 직접 시연한다.

---

## Experiment

**NLP/추론 태스크 (GPT-4 기준, Table 1)**:
- Logic Grid Puzzle: EVOAGENT **77.00%** vs AutoAgents 69.00% (+8.0%p), Direct 60.50%.
- Trivia Creative Writing: EVOAGENT **84.40%** vs AutoAgents 82.00%, SPP 79.20%.
- Codenames Collaborative: EVOAGENT **84.53%** vs AutoAgents 83.56%, Direct 79.38%.

**GPT-3.5 백본 (Table 1)**:
- Logic 71.50%, Writing 60.80%, Code 79.38% — 모두 AgentVerse/AutoAgents 대비 최고 성적.

**약한 LLM (LLaMA2-13B, Table 1)**:
- Logic: EVOAGENT **35.50%** vs SPP 0.00%, AgentVerse 10.00%, AutoAgents 16.00%.
- Writing: 49.60%, Code: 27.83% — Direct 대비 압도적 향상.

**MMMU 멀티모달 (Figure 2)**: GPT-4V 및 Gemini-Pro 모두에서 Self-Refine, SPP가 CoT보다 성능이 떨어지는 반면 EVOAGENT는 accuracy 전반에서 우위를 보인다.

**ScienceWorld 인터랙티브 과학 (Table 2)**:
- GPT-4 Overall: EVOAGENT(1,1) **30.42** vs baseline 27.97 (+2.45).
- GPT-4 Short-trajectory: **48.67** vs 42.41 (+6.26), Medium 36.17 vs 36.00, Long 11.38 vs 10.58.
- GPT-3.5 Overall: 19.02 vs 17.12 (+1.90), Short 33.26 vs 27.90 (+5.36).
- 짧은 궤적에서 이득이 가장 크며, 긴 궤적에서는 컨텍스트 부담으로 향상폭이 작아짐.

**TravelPlanner 실세계 계획 (Table 3, GPT-4)**:
- Commonsense Macro: **31.4%** vs Direct 27.5% (+3.9%p).
- Hard Constraint Macro: **18.9%** vs Direct 16.1% (+2.8%p).
- Final Pass Rate: **7.2%** vs Direct 2.2% (+5.0%p) — 3배 이상 향상.
- Gemini-Pro Commonsense Macro 16.9%, Final 1.7%. GPT-3.5 Final 1.1% (Direct 0.0%).

**Ablation — Quality-Check 효과 (Table 4)**:
- EVOAGENT(2,3): w/o QC Com. 62.8/Hard 12.7 → w/ QC Com. 67.0/Hard 15.2.
- EVOAGENT(3,3): w/o QC 62.7/13.7 → w/ QC 66.8/15.8.
- N>1에서 QC 없으면 중복 에이전트로 인한 품질 저하 발생.

**Selection 전략 비교 (Table 4)**: All-in w/ QC이 Hard 17.0으로 최적, PK는 QC 없을 때 13.6으로 우세하나 QC 있을 때 오히려 역전.

**Variant 비교 (Table 6, GPT-3.5 EVOAGENT(1,3) 대비)**:
- Suggest_3: Com. 57.5/Hard 5.7, Overgen_3: 56.3/9.0, PromptRefine_3: 61.2/11.0 모두 EVOAGENT(1,3)의 64.2/11.0보다 열세.

**시간 효율 (Table 5, Llama-3.1-70B)**: EvoAgent Logic 67.00(1060.8s), Writing 74.50(1209.6s), Code 74.62(859.2s) — AgentVerse/AutoAgents 대비 최고 성능이면서 시간 비용은 비슷한 수준.

**Iteration 효과 (Table 7)**: Trivia Creative Writing에서 iteration 3 이후 성능 수렴. 단순 NLP 태스크는 조기 포화.

---

## Limitation

다수 전문 에이전트를 생성·협업시키므로 단일 에이전트 대비 토큰 비용이 유의미하게 증가한다.

Table 5에서 확인되듯 실행 시간도 Direct 대비 3~5배 증가하여 latency-sensitive 응용에 부담이 된다.

AgentVerse와 AutoAgents 외 다른 MAS 프레임워크(예: DyLAN, SWIFTSAGE, LEGO)와의 광범위한 비교는 수행되지 않았다.

이는 각 프레임워크마다 벤치마크별 추가 설계가 필요하기 때문이라 저자 스스로 인정하고 있다.

생성된 에이전트의 품질을 인간 평가자로 수동 검증하지 않았으며, 오직 다운스트림 태스크 성능으로만 간접 평가했다.

ScienceWorld 결과에서 드러나듯 긴 궤적(long-trajectory) 태스크에서는 multi-agent의 누적 컨텍스트 부담으로 향상폭이 축소된다.

Quality-Check 없이 All-in 전략을 쓰면 부적절한 에이전트(예: 여행 계획에 영양사 할당)가 과도하게 긴 출력을 생성해 LLM 컨텍스트 윈도우를 초과하고 delivery rate가 붕괴한다.

초기 에이전트가 새 에이전트 결과를 통합할 때 user preference를 commonsense rule보다 우선시하는 편향이 관찰되어, 향후 연구 과제로 남아 있다.

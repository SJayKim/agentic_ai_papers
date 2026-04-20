# Multi-Agent Collaboration Mechanisms: A Survey of LLMs

> **논문 정보**: Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O'Sullivan, Hoang D. Nguyen (University College Cork, Pusan National University, Trinity College Dublin)
> **arXiv**: 2501.06322v1 (10 Jan 2025)
> **코드**: N/A

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)이 급속도로 발전하고 있지만, 에이전트 간 협업의 메커니즘을 체계적으로 분석한 연구는 부족하다.

기존 서베이들은 주로 단일 에이전트 관점에 집중하거나, 협업의 일부 측면(예: 커뮤니케이션 구조)만 다루며 포괄적인 프레임워크를 제공하지 못한다.

Wang et al.[136]는 brain/perception/action으로 구성된 단일 에이전트 프레임워크를 제안하지만 다중 에이전트 협업은 행동·성격 차원의 논의에 머문다.

Guo et al.[47]은 layered/decentralized/centralized/shared message pool 등 통신 구조를 프로파일링했지만 협업 유형·전략·조율 아키텍처 등 다른 핵심 차원을 다루지 않는다.

Lu et al.[82]는 merging/ensemble/cooperation 전략을 정리했지만 competition과 coopetition을 간과한다.

Li et al.[70], Chen et al.[46], Gao et al.[68]은 각각 소프트웨어 공학·agent-based simulation·디지털 트윈이라는 특정 도메인에 국한된다.

결과적으로 "어떻게 LLM 에이전트가 실제로 협력·경쟁·조율하는지"에 대한 know-how 수준의 체계가 누락되어 있다.

이 공백은 MAS의 잠재력(지식 기억 분산, 장기 계획, 효과적 일반화, 상호작용 효율성)을 실제 응용으로 연결하는 데 장애가 된다.

---

## Motivation

인간 사회의 집단 지성(society of mind[87], theory of mind[45])은 팀워크와 전문화를 통해 개인 능력을 초월하는 문제 해결을 가능하게 한다.

AI 에이전트도 유사하게 개별 강점과 관점을 결합하면 단일 LLM의 한계(hallucination[57], auto-regressive 제약[49], scaling law[55,69])를 완화할 수 있다.

MAS는 지식을 분산 저장해 단일 시스템 과부하를 막고[51,154], 장기 계획을 에이전트 간 위임으로 지속시키며[58], 전문화된 프롬프트·페르소나로 일반화 능력을 강화한다.

병렬 sub-task 처리로 상호작용 효율성도 높아져, 복합 다단계 태스크 해결을 가속화한다.

LLM은 "brain"으로서 에이전트에 정교한 추론·언어 능력을 부여할 수 있으며, AgentVerse[24], MetaGPT[56], Consensus-LLM[21] 등은 emergent social behavior와 합의 형성을 입증했다.

그러나 LLM은 본래 에이전트 간 통신을 위해 훈련되지 않았기에 cascading hallucination, 역할 충돌, 종료 조건 불명확 같은 새로운 문제가 발생한다.

따라서 Actors–Types–Structures–Strategies–Coordination의 5차원 렌즈로 협업을 해부하고, 기존 연구를 통합적으로 비교할 수 있는 확장 가능 프레임워크가 필요하다.

이 프레임워크는 5G/6G, Industry 5.0, QA, 사회·문화 시뮬레이션까지 다양한 도메인의 설계 지침으로 작동할 수 있다.

---

## Method

본 서베이는 LLM 기반 MAS 협업 메커니즘을 **5차원 프레임워크**로 체계화한다.

1. **수학적 정식화 (Agent)**: 에이전트를 $a = \{m, o, e, x, y\}$로 정의하며, $m = \{arch, mem, adp\}$는 LLM 아키텍처·메모리(system prompt $r$)·어댑터, $o$는 목적, $e$는 환경(context window), $x$는 입력, $y = m(o, e, x)$는 출력이다.

2. **수학적 정식화 (System)**: 시스템 $S = (A, O_{collab}, E, C)$는 에이전트 집합 $A = \{a_i\}_{i=1}^n$, 집단 목표 $O_{collab}$, 공유 환경 $E$, 협업 채널 집합 $C = \{c_j\}$로 구성되고, 최종 출력은 $y_{collab} = S(O_{collab}, E, x_{collab} | A, C)$로 표현된다.

3. **Actors 차원**: 참여 에이전트의 동질성(같은 LLM) vs 이질성(서로 다른 LLM·역할), 에이전트 수($n$), 역할 특화(리더/비평가/연구자/코더) 등을 구분한다.

4. **Types 차원 — Cooperation**: 모든 $o_i$가 $O_{collab} = \bigcup_{i=1}^n o_i$로 정렬되는 협력 유형으로, Reflexion의 Actor–Evaluator 피드백[117], ToM 공유 신념 상태[75], AgentVerse의 역할 분업[24], MetaGPT의 assembly-line SOP[56], CAMEL[74], AutoGen[134]이 대표 사례이다.

5. **Types 차원 — Competition**: 에이전트 목표가 상호 배타적($o_i \neq o_j$)이며 디베이트·전략 게임 상황을 포함한다. LLMARENA의 7개 게임 벤치마크[22], 식당 경영 시뮬레이션[155], LEGO의 Explainer–Critic[54], Mixture-of-Agents 학습[104]이 예시이다.

6. **Types 차원 — Coopetition**: 협력과 경쟁이 혼재된 형태로, Negotiation 시뮬레이션[2,34]과 Mixture-of-Experts 게이팅[6,15]이 해당된다.

7. **Hybrid Coordination**: 서로 다른 유형의 채널이 공존하는 설계로, 2개 디베이트 에이전트($c_{comp}$)와 판정 에이전트($c_{coop}$)가 결합되는 구조[77] 등이 포함된다.

8. **Structures 차원**: Peer-to-peer(평등 직접 통신), Centralized(Manager–Worker 조율), Distributed(공유 메시지 풀·분산 의사결정), Hierarchical(전략–전술–실행 다층 구조)으로 분류한다.

9. **Strategies 차원 — Rule-based**: 사전 정의된 규칙으로 상호작용을 엄격히 통제하며, 사회심리학 영감 디베이트·다수결[151], 이벤트-트리거 규칙[162], peer-review 기반 비평[143], 합의 탐색[21]이 대표 사례이다.

10. **Strategies 차원 — Role-based**: 각 에이전트 $a_i$가 분할된 목적 $o_i \subset O_{collab}$을 담당하며 AgentVerse[24], MetaGPT[56], RoCo 멀티로봇 대화 역할[83], BabyAGI의 3-chain 구조[120]가 포함된다.

11. **Strategies 차원 — Model-based**: 확률적 의사결정을 수행하며 ToM 기반 신념 추론[75], ToM+논리규칙 통합 계층적 RL[16], 게임 환경의 opponent modeling[141]이 예이다.

12. **Coordination Protocols**: 메시지 포맷, 턴 순서, 종료 조건, 합의 메커니즘(majority voting, consensus seeking)을 포함하고, 동기식 vs 비동기식, 공유 블랙보드 vs 직접 메시지를 구분한다.

13. **Collaboration Stage**: 정보 흐름이 일어나는 시점을 early-stage(데이터·context 공유), mid-stage(모델 파라미터·가중치 교환, federated 방식), late-stage(출력·행동 앙상블)로 3분할한다.

14. **Channel 정의**: 두 채널이 Actors/Type/Structure/Strategy 중 하나라도 다르면 별개 채널로 간주하여 피어투피어 내부에서도 일부 경쟁·일부 협력 채널이 공존할 수 있도록 모델링한다.

15. **분석 방법론**: 100편 이상의 MAS 연구를 이 5차원 프레임워크로 분류하고 유형–전략–구조의 조합별 빈도·장단점·도메인 적용을 정리하여 Table 1~3 및 Fig. 2~4로 시각화한다.

---

## Key Contribution

1. **5차원 협업 프레임워크**: Actors–Types–Structures–Strategies–Coordination Protocols를 통해 LLM MAS 협업을 수학적 정식화($a = \{m, o, e, x, y\}$, $S = \{A, O_{collab}, E, C\}$)와 함께 체계화한 최초의 서베이이다.

2. **Competition·Coopetition 포괄**: 기존 서베이가 간과한 경쟁·협경(coopetition) 유형을 명시적으로 정의하고 사례를 수집하여, cooperation 중심 담론을 확장한 점에서 Table 1에서 "High" 등급을 차지한다.

3. **Hybrid Collaboration Channel 모델**: 하나의 시스템 내에 서로 다른 유형의 $c_j$가 공존하는 구조를 공식화하여 디베이트+판정, Explainer+Critic 같은 실제 설계를 일반화한다.

4. **Stage-wise Collaboration 분류**: early/mid/late-stage 3단계로 협업 정보 흐름을 분류하여 federated learning·MoE·ensemble까지 통합적으로 설명한다.

5. **실세계 응용 도메인 리뷰**: 5G/6G 네트워크, Industry 5.0, 질의응답, 소프트웨어 개발, 사회·문화 시뮬레이션, 디지털 트윈 등 다양한 분야의 MAS 배치 사례를 비교 분석한다.

6. **열린 문제·미래 방향**: 집단 추론, 의사결정, 인간-AI 협업, 신뢰성, 확장성, 문화적 맥락 등 핵심 개방 과제를 식별하고 연구 로드맵을 제시한다.

7. **기존 서베이 대비 전영역 "High" 평가**: Table 1에서 Multi-Agent 집중도·협업 메커니즘 리뷰·일반 프레임워크 제안·실세계 응용 리뷰 4개 축 모두 High 등급을 획득한 유일한 서베이로 포지셔닝된다.

---

## Experiment

본 논문은 서베이이므로 자체 실험 대신 **체계적 문헌 분석**과 프레임워크 기반 비교 연구를 수행한다.

분석 대상은 LLM 기반 MAS 관련 **100편 이상**의 논문이며, 전체 서베이는 **35페이지** 분량으로 7개 섹션(Introduction, Background, Concept, Methodology, Applications, Open Problems, Conclusion)으로 구성된다.

기존 서베이 **8편**([136], [70], [82], [50], [68], [120], [46], [47])을 Table 1에서 4개 축(Multi-Agent 집중, 메커니즘 리뷰, 프레임워크 제안, 실세계 응용)으로 비교한 결과, 본 서베이가 4축 모두 "High" 등급을 받은 유일한 연구로 나타난다.

**Collaboration Types 통계 (Table 2)**: Cooperation은 code generation[12,56,60,117], decision making[91,117], game[75], QA[33,54,74,117], recommendation[131] 등 **5개 시나리오 · 13건**의 참조를 가진 가장 보편적 유형이다.

Competition은 debate[77], game[22,155], QA[54,104] **3개 시나리오 · 5건**, Coopetition은 negotiation[2,34] **1개 시나리오 · 2건**으로 아직 초기 단계임이 확인된다.

**Collaboration Strategies 통계 (Table 3)**: Rule-based는 QA·consensus seeking·navigation·peer-review 등 **4개 시나리오**, Role-based는 decision making·software development·robotics **3개**, Model-based는 game·decision making·robotics **3개** 시나리오에 배치된다.

**Role-based 집중도**: AgentVerse[24], MetaGPT[56], BabyAGI의 **3-chain**(Task creation/prioritization/Execution)[120], RoCo[83] 등 소프트웨어·로봇 영역에서 압도적으로 많이 채택된다.

**Structures 분포 (Fig. 1)**: Centralized 구조가 가장 흔하게 관찰되며, Generative Agents 류의 Distributed가 확장성에서, Hierarchical이 과학 연구용 다중 전문가 MAS에서 강점을 보인다.

**응용 도메인별 대표 사례**: 소프트웨어 개발은 ChatDev·MetaGPT(centralized, role-based cooperation), 사회 시뮬레이션은 Generative Agents(distributed cooperation), 5G/6G는 분산 자원 관리(distributed coopetition), 게임은 LLMARENA의 **7개** 동적 환경 벤치마크[22]와 **2-agent** 식당 매니저 시뮬레이션(50 customers)[155]이다.

**Stage-wise 분포**: 대부분의 MAS는 late-stage(출력 앙상블·voting)와 mid-stage(파라미터 교환) 협업에 집중되고, 동기식 턴 기반 통신이 지배적이며 비동기식 접근은 아직 초기이다.

---

## Limitation

LLM 기반 MAS 분야가 빠르게 진화하고 있어, 2025년 1월 출판 시점 이후의 최신 연구들(예: 새로운 멀티 에이전트 벤치마크, 프로토콜 표준)을 반영하지 못한다.

5차원 분류(Actors/Types/Structures/Strategies/Coordination) 중 일부 경계 사례는 모호해질 수 있으며, 예컨대 hybrid 채널은 cooperation·competition·coopetition 어느 쪽으로도 분류 가능해 정량적 통계에 노이즈를 유발한다.

실제 배포 환경에서의 MAS 협업 효율성·레이턴시·비용에 대한 정량적 벤치마크 비교가 제한적이며, 저자도 "정량적 비교가 부족하다"고 인정한다.

보안·프라이버시·정렬(alignment)·악의적 에이전트 방어 등 실용적 배포 도전 과제에 대한 심층 분석이 짧게만 다뤄진다.

에이전트 수 $n$이 커질 때 발생하는 통신 비용 폭발과 cascading hallucination 증폭에 대한 정량 모델링은 제시되지 않는다.

이질적 LLM 간 상호운용성(서로 다른 벤더·버전·프롬프트 포맷)과 동적 팀 구성·역할 재할당에 대한 구체적 알고리즘은 open problem으로만 남겨져 있다.

Coopetition 관련 사례가 **2건**에 불과해 이 차원의 실증적 근거가 매우 얕으며, MoE를 coopetition으로 포함시킨 분류가 다소 느슨하다는 논란이 가능하다.

인간-AI 협업, 문화적 맥락, 장기 기억·자기 진화 같은 주제는 연구 방향 수준에서만 언급되고 구체적 설계 지침으로 이어지지 않는다.

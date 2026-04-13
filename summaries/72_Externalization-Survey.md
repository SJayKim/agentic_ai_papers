# Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering

> **논문 정보**: Chenyu Zhou, Huacan Chai, Wenteng Chen, Zihan Guo, Rong Shan, Yuanyi Song, Tianyi Xu, Yingxuan Yang, Aofan Yu, Weiming Zhang, Congming Zheng, Jiachen Zhu, Zeyu Zheng, Zhuosheng Zhang, Xingyu Lou, Changwang Zhang, Zhihui Fu, Jun Wang, Weiwen Liu, Jianghao Lin, Weinan Zhang (Shanghai Jiao Tong University, Sun Yat-Sen University, Shanghai Innovation Institute, Carnegie Mellon University, OPPO)
> **arXiv**: 2604.08224 (2026.04)
> **코드**: N/A

---

## Problem

LLM 에이전트의 신뢰성 있는 동작을 위해 필요한 핵심 역량들 -- 장기 메모리 유지, 절차적 전문지식의 일관된 실행, 외부 도구/서비스와의 안정적 상호작용 -- 이 기존에는 모델 가중치(weights)나 컨텍스트 윈도우에 의존하는 방식으로 처리되어 왔다.
가중치 기반 방식은 지식 업데이트가 어렵고 감사 가능성(auditability)이 낮으며, 사용자별 개인화가 불가능하다.
단일 사실(예: 한 국가의 현 지도자)을 업데이트하려면 재훈련이나 knowledge editing이 필요하며, 이는 다른 능력에 부작용을 초래할 위험이 있다.
컨텍스트 기반 방식은 유한한 토큰 예산, "lost in the middle" 현상으로 인한 성능 저하, 세션 간 상태 소멸(ephemeral amnesia) 문제를 겪는다.
컨텍스트 길이가 2K에서 100K+ 토큰으로 확장되었음에도, 선택적 큐레이션의 필요성은 줄어들지 않았으며 과도한 컨텍스트 적재는 오히려 성능을 저하시킨다.
기존 서베이들은 RAG, 도구 학습, 에이전트 아키텍처, 프로토콜 상호운용성 등 개별 영역을 다루지만, 이들이 왜 하나의 공통 메커니즘으로 수렴하고 있는지를 통합적으로 설명하지 못한다.
CoALA가 가장 가까운 개념적 다리를 제공하지만, 메모리-스킬-프로토콜-하네스의 통합적 외재화(externalization) 관점은 여전히 미개발 상태였다.

---

## Motivation

이 논문의 핵심 통찰은 Donald Norman의 인지적 아티팩트(cognitive artifact) 이론에서 비롯된다.
Norman에 따르면, 외부 도구는 인간의 내재적 능력을 단순히 증폭하는 것이 아니라 과제 자체의 구조를 변환한다.
예컨대 쇼핑 목록은 기억 능력을 확장하는 것이 아니라, 어려운 회상(recall) 문제를 쉬운 인식(recognition) 문제로 바꾼다. 지도는 내비게이션을 "더 강하게" 만드는 것이 아니라, 숨겨진 공간 관계를 가시적 구조로 변환한다.
저자들은 이와 동일한 논리가 LLM 에이전트 설계에도 적용된다고 주장한다.
인류 문명의 역사가 인지적 외재화의 역사(언어 → 문자 → 인쇄 → 디지털 컴퓨팅)로 읽힐 수 있듯이, LLM 에이전트의 발전도 가중치(weights) → 컨텍스트(context) → 하네스(harness)로의 외재화 과정으로 이해할 수 있다.
실용적으로, 많은 시스템에서 가장 큰 신뢰성 향상은 기반 모델을 변경하지 않고 주변 환경을 변경함으로써 달성되었다는 관찰이 이 관점을 뒷받침한다.
즉, "모델이 얼마나 유능한가?"라는 질문에서 "어떤 부담이 외재화되어 모델이 매번 내부적으로 해결할 필요가 없어졌는가?"라는 질문으로 전환이 일어나고 있다.
이 프레임워크는 메모리가 recall을 retrieval로, 스킬이 즉흥적 생성을 구성(composition)으로, 프로토콜이 임시적 조정을 구조화된 계약으로 변환하는 것을 하나의 통합된 설계 원리로 설명한다.

---

## Method

이 서베이는 **외재화(externalization)**를 통합 렌즈로 사용하여 LLM 에이전트 인프라를 3개 외재화 차원 + 1개 통합 계층의 분류 체계로 조직한다.

**축 1: 메모리 (외재화된 상태)**
외재화되는 내용을 4가지 차원으로 분류한다: (1) 작업 컨텍스트(working context) -- 현재 태스크의 중간 상태, 열린 파일, 임시 변수, 활성 가설, 부분 계획, 실행 체크포인트, (2) 에피소드 경험(episodic experience) -- 과거 실행의 결정점, 도구 호출, 실패, 결과, 반성 기록, (3) 의미적 지식(semantic knowledge) -- 도메인 사실, 일반 휴리스틱, 프로젝트 관례 등 에피소드를 초월하는 추상화, (4) 개인화 메모리(personalized memory) -- 사용자별 선호, 습관, 반복적 제약, 과거 상호작용.
아키텍처 측면에서는 Monolithic Context → Context with Retrieval Storage → Hierarchical Memory and Orchestration → Adaptive Memory Systems의 4단계 진화를 추적한다.
- Monolithic Context: 모든 이력을 프롬프트에 직접 유지하나, 세션과 함께 상태가 소멸
- Context with Retrieval Storage: 외부 저장 + 검색(GraphRAG, ENGRAM, SYNAPSE 등)
- Hierarchical Memory: 추출/통합/망각의 관리형 생명주기(MemGPT, Mem0, Memory-R1, MemoryOS 등)
- Adaptive Memory Systems: RL, MoE 게이팅 등으로 검색 전략 자체를 학습(MemRL, MemEvolve, MemVerse 등)

**축 2: 스킬 (외재화된 전문지식)**
스킬의 내용을 3가지 구성요소로 분류한다: (1) 운영 절차(operational procedure), (2) 의사결정 휴리스틱(decision heuristics), (3) 규범적 제약(normative constraints).
진화 단계로는 Atomic Execution Primitives(Toolformer) → Large-scale Primitive Selection(Gorilla, ToolLLM, ToolNet) → Skill as Packaged Expertise(Voyager, SkillsBench)의 3단계를 제시한다.
스킬 외재화 과정은 명세(specification), 발견(discovery), 점진적 공개(progressive disclosure), 실행 바인딩(execution binding), 합성(composition)의 5가지 메커니즘으로 구성된다.
스킬 습득 경로로는 전문가 저작(authored), 궤적 기반 증류(distilled), 환경 탐험 기반 발견(discovered), 기존 스킬의 합성(composed)의 4가지를 식별한다.

**축 3: 프로토콜 (외재화된 상호작용)**
프로토콜이 외재화하는 내용을 4가지 차원 -- 호출 문법(invocation grammar), 생명주기 의미론(lifecycle semantics), 권한/신뢰 경계(permission and trust boundaries), 발견 메타데이터(discovery metadata) -- 으로 분류한다.
프로토콜 패밀리는 Agent-Tool (MCP 등), Agent-Agent (A2A, ACP, ANP 등), Agent-User (A2UI, AG-UI), 도메인 특화(UCP, AP2)로 구분된다.

**통합 계층: 하네스 엔지니어링**
하네스는 메모리, 스킬, 프로토콜을 통합하는 런타임 환경으로, 6가지 분석 차원으로 특성화된다: (1) 에이전트 루프 및 제어 흐름, (2) 샌드박싱 및 실행 격리, (3) 인간 감독 및 승인 게이트, (4) 관측 가능성 및 구조화된 피드백, (5) 구성/권한/정책 인코딩, (6) 컨텍스트 예산 관리.
또한 교차 분석에서 모듈 간 6가지 상호작용 흐름(메모리→스킬: 경험 증류, 스킬→메모리: 실행 기록, 스킬→프로토콜: 역량 호출, 프로토콜→스킬: 역량 생성, 메모리→프로토콜: 전략 선택, 프로토콜→메모리: 결과 동화)을 체계적으로 매핑한다.
시스템 수준 동학으로 자기강화 사이클(better memory → better skills → richer traces → better memory), 컨텍스트 예산 경쟁, 시간 스케일 차이를 규명한다.

---

## Key Contribution

1. **통합적 외재화 프레임워크 제시**: 메모리(상태), 스킬(전문지식), 프로토콜(상호작용)을 인지적 아티팩트 이론 기반의 단일 외재화 논리로 통합한 최초의 시스템 수준 리뷰. 기존 서베이들이 개별 컴포넌트에 집중한 것과 차별화된다.
2. **Weights → Context → Harness 역사적 진화 추적**: 2022년부터 2026년까지 LLM 에이전트 커뮤니티의 무게중심이 어떻게 외부 인프라로 이동해 왔는지를 3계층 모델로 체계화하였다.
3. **모듈 간 상호작용 맵 제공**: 메모리-스킬-프로토콜 간 6가지 양방향 결합(coupling) 관계를 명시적으로 분석하고, 컨텍스트 예산 경쟁, 시간 스케일 차이, 자기강화 사이클 등 시스템 수준 동학을 규명하였다.
4. **하네스 엔지니어링의 개념적 정립**: "에이전트 엔지니어링 = 하네스 엔지니어링"이라는 관점을 제시하고, OpenAI Codex와 Claude Code 같은 독립적으로 개발된 시스템들이 동일한 6가지 하네스 차원에 수렴함을 보여 구조적 필연성을 논증하였다.
5. **6가지 미래 방향 제시**: 파라메트릭/외재화 경계의 동적 이동, 디지털→체화(embodied) 외재화 확장, 자기 진화 하네스, 비용/위험/거버넌스, 사적 스캐폴딩→공유 인프라 전환, 외재화 품질 측정 방법론 등을 체계적으로 제안하였다.

---

## Experiment & Results

이 서베이 논문은 실험 대신 포괄적 문헌 분석을 수행한다.
참고문헌 목록에 약 150편 이상의 논문 및 기술 문서를 포함하며, 2020년부터 2026년까지의 시간 범위를 다룬다.
- 3개 외재화 축(메모리, 스킬, 프로토콜) + 1개 통합 계층(하네스)의 분류 체계를 기준으로 문헌을 조직
- 2022~2026년의 시간축을 따라 Weights, Context, Harness 3개 계층의 연구 주제 변화를 시각적으로 추적

주요 커버리지 분석 결과:
- **메모리 영역**: 4단계 아키텍처 진화를 MemGPT, Mem0, GraphRAG, MemRL, MemEvolve, MemVerse, ENGRAM, SYNAPSE 등 20편 이상의 논문으로 추적
- **스킬 영역**: 3단계 진화를 Toolformer, Gorilla, ToolLLM, ToolNet, Voyager, SkillsBench, PolySkill 등으로 매핑
- **프로토콜 영역**: MCP, A2A, ACP, ANP, A2UI, AG-UI, UCP, AP2 등 8개 이상의 프로토콜을 4가지 패밀리로 분류
- **하네스 실천 분석**: OpenAI Codex, Claude Code 등 상용 시스템이 6가지 하네스 차원에 독립적으로 수렴하는 패턴을 확인

핵심 발견:
- 컨텍스트 윈도우가 2K에서 100K+ 토큰으로 확장되었음에도 선택적 큐레이션의 필요성은 줄어들지 않았다
- 독립적으로 개발된 에이전트 시스템들이 동일한 6가지 하네스 차원에 수렴한다는 점은 외재화된 에이전시의 구조적 필연성을 시사한다
- LLM의 입/출력 경계에서 메모리는 contextual input, 스킬은 instructional input, 프로토콜은 action schema로 기능하며, 이 삼분 구조가 분리 가능한 디버깅을 가능하게 한다

---

## Limitation

- **하네스 개념의 미성숙**: 하네스 개념이 아직 통합(consolidating) 단계에 있어, 이 논문의 특성화는 현재 시스템의 반복 패턴 종합에 가까우며 폐쇄적(closed) 정의가 아니다.
- **벤치마크의 체계적 과소측정**: 현행 벤치마크가 외재화된 인프라의 기여를 체계적으로 과소측정하여 모델 지능으로 귀속시키는 문제를 지적하면서도, 구체적 평가 방법론은 미래 방향으로 제안하는 데 그친다.
- **기술적 깊이 부재**: 서베이 특성상 각 모듈에 대한 깊이 있는 기술적 비교(예: 메모리 시스템 간 정량적 성능 비교, 프로토콜 간 레이턴시/처리량 비교)가 부재하다.
- **비용의 정량적 분석 부족**: 외재화의 비용 측면을 정성적으로 논의하지만, over-retrieval로 인한 컨텍스트 오염이나 tool sprawl의 구체적 정량 분석은 포함되지 않는다.
- **텍스트 기반 에이전트 편향**: 분류 체계가 주로 텍스트 기반 에이전트에 초점을 맞추고 있어, 체화(embodied) 시스템이나 멀티모달 에이전트에 대한 논의는 미래 방향으로만 다루어진다.
- **최적 분할 기준의 정성적 한계**: 파라메트릭 vs. 외재화 경계의 최적 분할 기준이 정성적 차원에 머물러 있어, 실무 적용 시 구체적 가이드라인으로 활용하기 어렵다.
- **보안 위협의 제한적 분석**: 메모리 포이즈닝, 악성 스킬 주입, 프로토콜 스푸핑 등의 보안 위협을 식별하지만, 방어 메커니즘이나 구체적 완화 전략에 대한 심층 분석은 제공하지 않는다.

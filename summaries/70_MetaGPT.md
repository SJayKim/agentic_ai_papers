# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

> **논문 정보**: Sirui Hong, Mingchen Zhuge, Jiaqi Chen 외 (DeepWisdom, KAUST, Xiamen University, CUHK-Shenzhen, Nanjing University, UPenn, UC Berkeley, IDSIA)
> **arXiv**: 2308.00352 (2023.08, v7 2024.11) | **학회**: ICLR 2024
> **코드**: https://github.com/geekan/MetaGPT

---

## Problem

기존 LLM 기반 다중 에이전트 시스템은 단순한 대화형 태스크는 해결할 수 있으나, 복잡한 소프트웨어 개발과 같이 논리적 일관성이 요구되는 문제에서는 심각한 한계를 드러낸다.
에이전트들을 순진하게 LLM으로 체이닝(naively chaining)하면, 한 에이전트의 환각(hallucination)이 다음 에이전트의 입력으로 전파되어 **캐스케이딩 환각(cascading hallucinations)** 을 유발하고 결과적으로 전체 태스크가 붕괴한다.
기존 롤플레이 프레임워크(CAMEL, ChatDev 등)는 자유 형식의 자연어 대화에만 의존하기 때문에, "Hi, hello and how are you?" 같은 비생산적 잡담(idle chatter)이 토큰 예산을 소비하고 실제 산출물의 품질을 떨어뜨린다.
자연어는 범용적이지만 "전화 게임(Chinese whispers)"처럼 여러 라운드를 거치면 원본 정보가 왜곡되어, 상류 단계의 요구사항이 하류 단계의 코드 구현에 정확히 반영되지 않는다.
또한 기존 프레임워크는 코드 생성 후 실제 실행 가능한 피드백(executable feedback) 메커니즘이 없어, 컴파일 오류나 런타임 오류를 자가 교정하지 못한 채 불완전한 결과물을 반환한다.
이러한 구조적 문제로 인해 HumanEval, MBPP 같은 코드 생성 벤치마크와 실제 소프트웨어 개발 시나리오 모두에서 단일 LLM 혹은 경량 협업 프레임워크 대비 품질 향상이 제한적이었다.

---

## Motivation

인류는 오랜 협업 경험을 통해 각 도메인마다 **표준 운영 절차(Standardized Operating Procedures, SOPs)** 를 확립해 왔고, 이는 태스크 분할, 역할 간 책임 분배, 중간 산출물의 품질 기준을 규정하는 방식으로 복잡한 작업을 성공적으로 수행하게 한다.
예를 들어 소프트웨어 회사에서 Product Manager는 경쟁 분석과 사용자 요구 조사를 바탕으로 표준화된 구조의 PRD(Product Requirements Document)를 작성하여 후속 개발 프로세스를 가이드한다.
이러한 인간 팀의 SOP를 LLM 에이전트에 프롬프트 시퀀스로 인코딩하면, 각 에이전트가 자신의 역할에 특화된 **구조화된 중간 산출물(structured intermediate outputs)** 만 생성하도록 강제할 수 있다.
구조화된 문서 기반 통신은 자유 대화보다 모호성과 오류를 크게 줄이며, 한 에이전트의 환각이 다른 에이전트로 전파되기 전에 스키마 수준에서 차단할 수 있다.
또한 "프로그래밍을 위한 프로그래밍(programming to program)"이라는 **메타 프로그래밍** 관점에서, 전문화된 에이전트 집단이 자동으로 요구사항 분석, 시스템 설계, 코드 생성, 수정, 실행, 디버깅을 수행하는 파이프라인을 구축할 수 있다.
저자들은 이에 더하여 런타임 실행 피드백을 통합한 **자가 교정 메커니즘**을 설계함으로써, 생성된 코드의 실제 실행 가능성을 보장하는 방향으로 한 걸음 더 나아갔다.

---

## Method

### 1. SOP 기반 역할 특화 (Specialization of Roles)
소프트웨어 회사 메타포를 따라 **Product Manager, Architect, Project Manager, Engineer, QA Engineer** 다섯 가지 전문 역할을 정의한다.
각 에이전트는 이름(name), 프로필(profile), 목표(goal), 제약조건(constraints)을 포함하는 역할 명세와 역할별 도구(예: Product Manager는 웹 검색, Engineer는 코드 실행)를 부여받는다.

### 2. ReAct 스타일 행동 루프
모든 에이전트는 Yao et al. (2022)의 ReAct 패턴을 따라 환경(=메시지 풀)을 지속적으로 관찰하고, 중요한 관찰(예: 다른 에이전트의 새 메시지)을 감지하면 이를 트리거로 다음 액션을 수행한다.

### 3. 어셈블리 라인 워크플로우
SOP에 따라 에이전트들이 순차적으로 동작한다: 사용자 요구 → Product Manager가 User Stories와 Requirement Pool을 포함한 PRD 작성 → Architect가 File List, Data Structure, Interface Definition으로 변환 → Project Manager가 태스크 분배 → Engineer가 클래스/함수 구현 → QA Engineer가 테스트 케이스 작성.

### 4. 구조화된 통신 인터페이스 (Structured Communication Interfaces)
각 역할마다 출력 스키마와 포맷을 사전 정의하여, 에이전트는 자유 대화 대신 **문서와 다이어그램** 형태의 구조화된 산출물로 통신한다 (예: Architect는 system interface design과 sequence flow diagram 두 가지를 생성).

### 5. 공유 메시지 풀 (Shared Message Pool)
전역 메시지 풀을 도입하여 모든 에이전트가 구조화된 메시지를 **publish**하고, 다른 에이전트가 직접 retrieve하도록 한다.
이는 1:1 대화 토폴로지의 복잡성과 비효율을 제거하며, 응답 대기 없이 필요 정보를 즉시 획득할 수 있게 한다.

### 6. 구독 메커니즘 (Subscription Mechanism)
정보 과부하를 방지하기 위해, 각 에이전트는 역할 프로필 기반의 관심사(role-specific interests)로 필요한 메시지만 선별 수신한다.
모든 선행 의존성(prerequisite dependencies)이 수신된 뒤에만 해당 에이전트의 액션이 활성화되어, 엄격한 선후관계를 보장한다.

### 7. 런타임 실행 피드백 (Executable Feedback)
Engineer 에이전트는 초기 코드 생성 후 실제로 실행(run)하여 오류를 감지한다.
오류 발생 시 메모리에 저장된 과거 PRD, 시스템 설계, 코드 파일을 참조하여 원인을 분석하고 디버깅한다.

### 8. 유닛 테스트 반복 루프
Engineer는 단위 테스트 케이스를 작성·실행하여 결과를 피드백으로 수집하고, 통과할 때까지 코드 수정과 재실행을 반복한 뒤 다음 개발 단계로 진입한다.

### 9. 자가 개선 메커니즘 (Self-Improvement, Outlook)
각 프로젝트 종료 시 handover feedback action으로 경험을 요약하여 장기 메모리에 저장하고, 새 프로젝트 시작 시 각 에이전트가 이 피드백을 검토하여 자신의 constraint prompt를 재귀적으로 수정한다 (현재는 역할 특화 부분만 수정, 통신 프로토콜은 미포함).

---

## Key Contribution

1. **SOP의 LLM 다중 에이전트 시스템 통합**: 인간 팀의 표준 운영 절차를 프롬프트 시퀀스로 인코딩한 **선구적 메타 프로그래밍 프레임워크**를 제시하여, 복잡한 소프트웨어 개발 태스크를 5개 전문 역할로 분해하고 어셈블리 라인 방식으로 처리.
2. **구조화된 통신으로 캐스케이딩 환각 억제**: 역할별 스키마 기반 문서/다이어그램 산출물을 강제함으로써, 자유 대화에서 발생하는 환각 전파와 비생산적 잡담을 원천적으로 차단하고 산출물의 일관성 확보.
3. **Publish-Subscribe 메시지 풀 메커니즘**: 전역 공유 메시지 풀과 역할 기반 구독 시스템을 도입하여 1:1 통신 토폴로지의 복잡성을 제거하고, 선행 의존성이 충족되어야만 액션이 트리거되도록 설계.
4. **런타임 실행 피드백을 통한 자가 교정**: 코드 실행 → 오류 감지 → 메모리 기반 디버깅 → 유닛 테스트 반복 루프를 통합하여 HumanEval Pass@1 +4.2%p, MBPP Pass@1 +5.4%p 개선.
5. **SoftwareDev 벤치마크 신규 제안**: 기존 HumanEval/MBPP가 커버하지 못하는 실제 엔지니어링 측면을 평가하는 70개 대표 소프트웨어 개발 태스크 데이터셋 공개 (미니게임, 이미지 처리, 데이터 시각화 등).
6. **최첨단 성능 달성**: HumanEval 85.9%, MBPP 87.7% Pass@1로 ICLR 2024 당시 SOTA 달성하고 GPT-4 단독 대비 +18.9%p 향상.
7. **재귀적 자가 개선 비전 제시**: Outlook에서 handover feedback 기반 constraint prompt 진화 메커니즘과 AgentStore의 Economy of Minds 개념을 제시하여 후속 연구 방향 제안.

---

## Experiment

**벤치마크 구성**:
- HumanEval: 164개 수작업 프로그래밍 태스크 (함수 스펙, 설명, 레퍼런스 코드, 테스트 포함).
- MBPP: 427개 Python 태스크 (핵심 개념과 표준 라이브러리 중심).
- SoftwareDev: 저자들이 신규 구축한 70개 소프트웨어 개발 태스크 (비교 실험에는 대표 7개 선정).

**HumanEval / MBPP 코드 생성 성능 (Pass@1)**:
- MetaGPT: **HumanEval 85.9%, MBPP 87.7%** 로 SOTA 달성.
- GPT-4 단독: HumanEval 67.0% (MetaGPT 대비 **-18.9%p**).
- Codex+CodeT: MBPP 67.7% (MetaGPT 대비 **-20.0%p**).
- MetaGPT w/o Feedback: HumanEval 81.7%, MBPP 82.3% → 실행 피드백이 각각 **+4.2%p, +5.4%p** 개선.
- CodeGeeX-Mono(16.1B): HumanEval 32.9%, MBPP 38.6%.

**SoftwareDev 벤치마크 (vs ChatDev)**:
- Executability (1~4점): MetaGPT **3.75** vs ChatDev 2.25 (4점=flawless에 근접).
- Running Time: MetaGPT **541초** (w/o feedback 503초) vs ChatDev **762초**.
- Token Usage: MetaGPT 31,255 (w/o 24,613) vs ChatDev 19,292 (MetaGPT가 더 많지만 코드 규모가 훨씬 큼).
- Code Files: MetaGPT **5.1개** vs ChatDev 1.9개.
- Lines per File: MetaGPT **49.3** vs ChatDev 40.8.
- Total Code Lines: MetaGPT **251.4줄** vs ChatDev 77.5줄 (약 **3.2배** 복잡한 산출물).
- Productivity (tokens/line): MetaGPT **124.3** vs ChatDev 248.9 (토큰 효율 **약 2배**).
- Human Revision Cost: MetaGPT **0.83회** vs ChatDev 2.5회 (**67% 감소**).

**역할 Ablation (Table 3)**:
- Engineer 단독(1 에이전트): 83.0 lines, $0.915, Revisions 10회, Executability 1.0.
- Engineer+Product(2 에이전트): 112.0 lines, $1.059, Revisions 6.5회, Executability 2.0.
- +Architect(3 에이전트): 143.0 lines, $1.204, Revisions 4.0회, Executability 2.5.
- +Project(3 에이전트): 205.0 lines, $1.251, Revisions 3.5회, Executability 2.0.
- 4 에이전트(Engineer+Product+Architect+Project): 191.0 lines, $1.385, Revisions 2.5회, **Executability 4.0** (완벽).
- 역할 추가 시 비용은 소폭 증가하나 revisions 75% 감소, executability 4배 향상.

**능력 비교 (Table 2)**: MetaGPT만이 PRD 생성, 기술 설계 생성, API 인터페이스 생성, Precompilation execution, Role-based task management, Code review 모든 항목을 지원 (AutoGPT/LangChain은 코드 생성만, AgentVerse/ChatDev는 일부만 지원).

---

## Limitation

SOP가 **소프트웨어 개발 도메인에 특화**되어 설계되었기에, 의료·법률·과학 연구 등 다른 도메인에 확장하려면 해당 도메인의 SOP를 새로 정의하고 역할·산출물 스키마·워크플로우를 재설계해야 한다는 이식성(portability) 문제가 남아 있다.
역할을 1개에서 4개로 늘렸을 때 비용이 $0.915 → $1.385로 약 **51% 증가**하며, 더 많은 역할을 추가할수록 토큰 비용과 응답 지연이 선형 이상으로 커진다.
현재 워크플로우는 엄격한 **순차 어셈블리 라인 구조**이기 때문에, 병렬화 가능한 독립 태스크들에도 불필요한 직렬 대기를 강제하여 실행 효율이 떨어진다.
평가가 HumanEval, MBPP, SoftwareDev 등 주로 **코딩 중심 벤치마크**에 한정되어 있어, 자연어 기반 추론·창의적 글쓰기·과학 연구 같은 비코딩 협업 시나리오에서의 일반성은 검증되지 않았다.
자가 개선(self-improvement) 메커니즘은 Outlook에 비전으로 제시되었을 뿐, 현재 구현은 **역할 특화(Specialization) 부분의 constraint prompt만 수정**할 수 있고 통신 프로토콜(communication protocol)은 고정되어 있어 완전한 재귀적 자가 개선에는 이르지 못했다.
구조화된 스키마에 강하게 의존하기 때문에 스키마 설계가 부실하거나 사용자 요구가 기존 스키마로 잘 포착되지 않는 경우, 오히려 자유 대화 대비 유연성을 잃을 위험이 있다.

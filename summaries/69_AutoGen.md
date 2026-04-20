# AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

> **논문 정보**: Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu 외 (Microsoft Research, Penn State, UW)
> **arXiv**: 2308.08155 (2023.08) | **학회**: COLM 2024
> **코드**: https://github.com/microsoft/autogen

---

## Problem

LLM을 활용한 복잡한 작업 수행 시 단일 에이전트 패러다임은 추론, 사실성 검증, 도구 활용, 인간 개입을 통합적으로 지원하는 데 한계가 있다.
다수의 에이전트를 협업시키는 것이 유망한 스케일업 방식이지만, 이를 범용적으로 구현할 표준화된 추상화 계층이 부재하다.
기존 다중 에이전트 시스템(BabyAGI, CAMEL, MetaGPT)은 대부분 특정 시나리오에 특화되어 있거나 정적(static) 대화 패턴만 지원해 유연성이 떨어진다.
AutoGPT, LangChain Agents, Transformers Agent 같은 프레임워크는 단일 에이전트 패러다임을 따르며 에이전트 간 협업을 기본적으로 지원하지 않는다.
복잡도가 다른 다양한 애플리케이션이 요구하는 단일/다중 턴 대화, 정적/동적 플로우, 상이한 인간 개입 모드를 모두 수용하는 통일된 인터페이스가 필요하다.
또한 개발자가 자연어와 프로그래밍 언어를 혼합해 에이전트 상호작용을 프로그래밍할 수 있는 표현력 높은 패러다임이 없었다.
기존 프레임워크 대부분은 LLM/도구/인간 조합으로 이뤄지는 다양한 역할 혼합 에이전트 생성, 재사용, 확장을 일관되게 지원하지 못한다.
따라서 수학·코딩·QA·의사결정·최적화·오락 등 폭넓은 도메인에 적용 가능한 일반 다중 에이전트 대화 프레임워크가 요구된다.

---

## Motivation

최근 chat-optimized LLM(예: GPT-4)은 피드백 수용 능력이 뛰어나, 에이전트들이 대화를 통해 추론·관찰·비평·검증을 주고받는 협업이 가능해졌다.
단일 LLM이 프롬프트·추론 설정에 따라 다양한 역량을 드러낼 수 있으므로, 서로 다르게 구성된 에이전트 간 대화는 이들 역량을 모듈형으로 결합하는 수단이 된다.
LLM은 작업을 하위 태스크로 분해할 때 성능이 향상되는 경향이 있고, 다중 에이전트 대화는 이러한 분할·통합을 자연스럽게 구현한다.
선행 연구는 다중 에이전트가 발산적 사고(Liang 2023), 사실성·추론 개선(Du 2023), 검증(Wu 2023)을 촉진한다는 증거를 제시했다.
저자들은 이러한 관찰을 통합해 두 가지 핵심 설계 질문을 던진다: (1) 재사용·커스터마이즈 가능하고 협업에 효과적인 개별 에이전트를 어떻게 설계할 것인가, (2) 다양한 대화 패턴을 수용하는 단순·통일된 인터페이스를 어떻게 구축할 것인가.
이 두 질문을 해결함으로써 개발 비용을 낮추면서도 다양한 복잡도의 LLM 애플리케이션을 하나의 추상화로 제작할 수 있다.
또한 자연어 제어(LLM 프롬프트)와 프로그래밍 제어(Python) 사이의 전환이 매끄러우면 개발자가 상황에 따라 가장 효과적인 제어 수단을 선택할 수 있다.

---

## Method

1. **ConversableAgent 최상위 추상화**: 모든 에이전트는 메시지 송수신을 위한 통일 인터페이스(`send`, `receive`, `generate_reply`)를 갖고, 내부 컨텍스트를 메시지 이력 기반으로 유지한다.
2. **역량 구성요소 조합**: 에이전트 역량을 LLM 백엔드, 인간 입력, 도구(코드/함수 실행) 세 축의 조합으로 정의하며 각 축을 독립적으로 활성/비활성화하여 역할별 에이전트를 구성한다.
3. **AssistantAgent 프리셋**: LLM 기반 AI 어시스턴트로 기본 시스템 메시지에 "Python 코드를 제안하고 오류 발생 시 재작성하라"는 자연어 지시를 포함하여 LLM 추론만으로 교정 루프를 구현한다.
4. **UserProxyAgent 프리셋**: 인간/도구 기반 프록시로 `human_input_mode` 파라미터(ALWAYS/TERMINATE/NEVER)로 인간 개입 빈도를 조절하며, LLM이 제안한 코드/함수를 기본적으로 실행한다.
5. **GroupChatManager**: 역할극 스타일 프롬프트로 현재 대화 맥락에 맞는 화자를 동적으로 선택하고, 응답을 수집·방송(broadcast)하는 3단계를 반복하는 동적 그룹 채팅 전용 에이전트.
6. **Auto-reply 메커니즘**: 에이전트가 메시지를 수신하면 종료 조건이 충족되기 전까지 자동으로 `generate_reply`를 호출해 응답을 돌려보내며, 별도의 제어 평면(control plane) 없이 분산적으로 워크플로우가 진행된다.
7. **Conversation-centric computation**: 모든 계산이 "대화 맥락에 대한 함수"로 수행되며, 그 결과 메시지 패싱이 후속 대화를 유발하는 이벤트-드리븐 구조를 취한다.
8. **Conversation-driven control flow**: 어떤 에이전트에게 메시지를 보낼지, 어떤 계산을 수행할지가 대화 내용의 함수로 결정되어 복잡한 워크플로우를 "에이전트 행위 + 메시지 패싱"으로 직관적으로 추론할 수 있다.
9. **자연어 제어**: LLM 기반 에이전트의 시스템 메시지에 "모든 태스크 완료 시 TERMINATE를 응답하라" 같은 자연어 지시를 기록해 종료 조건과 출력 구조를 제어한다.
10. **프로그래밍 언어 제어**: Python으로 최대 자동 응답 횟수, 종료 조건, 도구 실행 로직, 커스텀 auto-reply 함수를 명세해 결정론적 제어 흐름을 구현한다.
11. **자연어↔코드 전환**: 커스텀 `generate_reply`에서 LLM 추론을 호출(코드→자연어)하거나 LLM의 function calling으로 코드를 호출(자연어→코드)하여 두 제어 모드 간을 자유롭게 오간다.
12. **정적 패턴**: 1:1 양방향 대화, 순차 파이프라인, 사전 정의된 순서의 에이전트 체인을 기본 제공.
13. **동적 패턴**: 커스텀 `generate_reply`로 서브 대화를 개시하는 nested chat, LLM function call로 분기되는 대화, GroupChatManager 기반 동적 화자 선택을 지원.
14. **Human-in-the-loop 통합**: 별도 모듈 없이 `human_input_mode` 한 파라미터로 "항상 개입", "종료 시점에만 개입", "개입 없음"을 통일적으로 처리하며 인간은 입력 skip도 가능하다.
15. **Enhanced LLM inference layer**: 결과 캐싱, 오류 처리, 메시지 템플릿화 등을 포함해 실사용에서의 신뢰성과 비용 효율을 개선.

---

## Key Contribution

1. **범용 다중 에이전트 대화 프레임워크**: 수학, 코딩, RAG, 의사결정, 최적화, 체스 등 이질적인 도메인을 단일 추상화(ConversableAgent + GroupChatManager)로 커버하는 최초의 범용 오픈소스 인프라.
2. **Conversation Programming 패러다임 정립**: "계산(computation)"과 "제어 흐름(control flow)"을 모두 대화 중심으로 정의하는 새로운 프로그래밍 모델을 제안하여, 복잡한 워크플로우를 에이전트 행동 + 메시지 패싱으로 추론할 수 있도록 한다.
3. **Auto-reply 기반 분산 제어**: 별도의 오케스트레이터 없이 각 에이전트가 메시지 수신 시 자동 응답하는 메커니즘으로 모듈적이고 확장 가능한 대화 흐름을 실현.
4. **자연어·프로그래밍 언어 혼합 제어**: 시스템 프롬프트와 Python을 모두 활용하고 LLM function calling으로 양자를 매끄럽게 전환하는 하이브리드 제어 방식을 표준화.
5. **정적+동적 대화 패턴 모두 지원**: Table 1 비교에서 BabyAGI/CAMEL/MetaGPT가 static만 지원하는 반면 AutoGen만이 static+dynamic을 모두 지원하는 유일한 프레임워크로 포지셔닝.
6. **통일된 Human-in-the-loop**: `human_input_mode` 단일 파라미터로 인간 개입 수준을 조정하고 skip 옵션을 제공해 개발·운영 모두에 유연성 부여.
7. **실증적 성능 우위**: 수학·RAG·ALFWorld·OptiGuide 네 벤치마크에서 vanilla GPT-4, ChatGPT+Code Interpreter, ReAct, DPR, Multi-Agent Debate 등 기존 기법을 모두 앞서는 성과로 프레임워크의 효과성을 입증.

---

## Experiment

**A1: 수학 문제 풀이 (MATH, GPT-4)**:
120개 무작위 추출 Level-5 문제에서 AutoGen은 **52.5%** 성공률을 기록하여 ChatGPT+Code Interpreter 48.33%, ChatGPT+Plugin(Wolfram) 45.0%, vanilla GPT-4 30.0%, Multi-Agent Debate 26.67%, LangChain ReAct 23.33%를 모두 상회했다.
전체 테스트셋 평가에서도 AutoGen **69.48%** vs ChatGPT+Code Interpreter 55.18%로 **+14.3%p** 격차를 벌렸다.

**A2: Retrieval-Augmented Q&A (Natural Questions, GPT-3.5)**:
AutoGen Retrieval-augmented Chat은 F1 **25.88%**, Recall **66.65%**로 DPR 기준선(F1 22.79%, Recall 62.59%)을 능가.
Interactive retrieval 기능(검색 결과 부족 시 "UPDATE CONTEXT" 자동 발화)을 제거한 ablation에서는 F1 **15.12%**, Recall **58.56%**로 급락하여 대화 기반 재검색 메커니즘의 기여도가 F1 **+10.76%p**, Recall **+8.09%p**임을 입증.

**A3: ALFWorld 의사결정 (134개 unseen 태스크, GPT-3.5-turbo)**:
2-에이전트(Assistant+Executor) 구성은 평균 **54%** 성공률(ReAct와 동등)이었으나 Grounding Agent를 추가한 3-에이전트 구성은 평균 **69%**(+15%p), Best-of-3 기준 **77%** vs 2-에이전트 **63%**, ReAct **66%**로 최고 성능.
Grounding agent가 "물체를 검사하려면 먼저 찾아 집어야 한다"와 같은 상식 지식을 루프 초기에 주입해 에러 루프 고착을 방지.

**A4: OptiGuide 다중 에이전트 코딩 (공급망 최적화)**:
Multi-GPT4(Commander+Writer+Safeguard) F1 **96%** / Recall **98%**로 Single-GPT4 F1 88% / Recall 78% 대비 F1 +8%p, Recall +20%p 향상.
GPT-3.5도 Multi-GPT3.5 F1 **83%** / Recall **72%** vs Single-GPT3.5 48% / 32%로 Recall +40%p의 큰 이득.
코드베이스 크기가 **430줄 → 100줄로 77% 감소**하고 사용자 작업 시간이 약 **3배** 절감되며 사용자 상호작용 수도 감소.

**A5 Dynamic Group Chat**: 수작업 제작한 12개 복잡 태스크 파일럿에서 역할극 스타일 화자 선택 프롬프트가 태스크 기반 프롬프트 대비 더 높은 성공률과 더 적은 LLM 호출 수를 달성.

**A6 Conversational Chess**: 보드 에이전트(grounding)를 제거한 ablation에서 불법 수(illegal moves)로 인한 게임 중단이 빈발하여, 단순 프롬프트("합법 수만 두세요")로는 grounding을 대체할 수 없음을 확인.

---

## Limitation

복잡한 다중 에이전트 상호작용의 디버깅이 어려워, 예상치 못한 루프나 에러 전파 경로를 추적하기 위한 관측 도구가 추가로 필요하다.
워크플로우를 여전히 수동으로 정의해야 하며, 에이전트 토폴로지·대화 패턴의 자동 최적화는 본 연구 범위 밖이다.
에이전트 수와 대화 턴이 증가할수록 컨텍스트 창 사용량과 LLM 호출 비용이 선형 이상으로 증가해 실서비스 비용 부담이 커진다.
에이전트가 외부 환경에 코드 실행이나 패키지 설치 등 쓰기 작업을 수행할 경우 예기치 않은 부작용과 보안 위험이 존재하며 본 프레임워크는 샌드박싱을 네이티브로 강제하지 않는다.
자동화 수준과 인간 제어의 최적 균형, 어떤 토폴로지가 어떤 태스크에 가장 효과적인지에 대한 체계적 분석이 부족하다.
편향·공정성·책임성 같은 윤리적 이슈는 LLM 다중 에이전트 환경에서 증폭될 수 있으며 프레임워크 차원의 안전장치는 개발자에게 위임되어 있다.
본 연구는 초기 실험 단계로, 에이전트 수가 크게 늘어날 때 발생할 수 있는 안전성·신뢰성 문제에 대한 전면적 검증이 부재하다.

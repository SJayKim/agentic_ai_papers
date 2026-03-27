# AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

> **논문 정보**: Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu 외 (Microsoft Research, Penn State, UW)
> **arXiv**: 2308.08155 (2023.08) | **학회**: COLM 2024
> **코드**: https://github.com/microsoft/autogen

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 다중 에이전트 애플리케이션 구축이 복잡하고, 에이전트 간 대화 패턴을 유연하게 정의·관리하는 표준화된 프레임워크가 부재하다. 단일 에이전트는 복잡한 태스크에서 추론, 사실성, 검증에 한계. |
| **Motivation** | 다중 에이전트 대화는 발산적 사고, 사실성 개선, 상호 검증을 가능케 하지만 이를 구현하는 범용 프레임워크가 없었다. 자연어와 코드를 혼합하여 워크플로우를 프로그래밍할 수 있는 추상화 계층이 필요하다. |
| **Limitation** | 복잡한 에이전트 상호작용의 디버깅이 어려움. 수동 워크플로우 정의 필요, 자동 최적화 미지원. 긴 세션에서 컨텍스트 창 비용 선형 증가. 에이전트 수 증가 시 안전 문제. |

---

## Method

### 1. Conversable Agents
- **ConversableAgent**: `send`, `receive`, `generate_reply` 통합 인터페이스
- 역량은 LLM, 인간 입력, 도구(코드/함수 실행)의 조합으로 구성, 독립 활성화/비활성화
- **AssistantAgent**: LLM 기반 AI 어시스턴트, 오류 시 코드 재작성 기본 시스템 메시지
- **UserProxyAgent**: 인간/도구 기반, `human_input_mode` ALWAYS/TERMINATE/NEVER
- **GroupChatManager**: 역할극 스타일 프롬프트로 동적 화자 선택
- 자동 응답(auto-reply): 종료 조건 미충족 시 자동 `generate_reply` 호출 → 별도 제어 평면 없이 분산적 워크플로우

### 2. Conversation Programming
- **대화 중심 연산**: 모든 행동이 대화 맥락 기반으로 수행
- **대화 주도 제어 흐름**: 메시지 수신자·계산 유형이 대화 내용의 함수로 결정
- **자연어·코드 혼합 제어**: LLM 지시 또는 Python으로 종료 조건·입력 모드·툴 로직 명세
- **동적 대화 패턴**: 커스텀 `generate_reply`로 서브 대화 개시, LLM 함수 호출로 동적 분기

### 3. 지원 패턴
- 1:1 양방향, 순차 파이프라인, 중첩 대화(nested chat), 동적 그룹 채팅
- Human-in-the-loop은 `human_input_mode` 하나로 통합

---

## Key Contribution

1. **범용 다중 에이전트 대화 프레임워크**: 수학, 코딩, 의사결정, RAG 등 폭넓은 도메인을 하나의 추상화로 커버
2. **Conversation Programming 패러다임**: 자연어와 코드를 혼합하여 워크플로우를 직관적으로 프로그래밍
3. **자동 응답 메커니즘**: 별도 오케스트레이터 없이 분산적 대화 흐름 제어
4. **사실상 표준 프레임워크**: 50K+ GitHub stars, 학계·산업 광범위 채택

---

## Experiment & Results

**A1: 수학 (MATH Level-5, GPT-4)**:
- AutoGen **52.5%** vs ChatGPT+Code Interpreter 48.33%, vanilla GPT-4 30.0%, LangChain ReAct 23.33%
- 전체 데이터셋: AutoGen **69.48%** vs ChatGPT+CI 55.18%

**A2: RAG Q&A (Natural Questions, GPT-3.5)**:
- AutoGen Recall **66.65%** / F1 **25.88%** vs DPR 62.59% / 22.79%
- Interactive Retrieval 제거 시 Recall 58.56% / F1 15.12%로 하락

**A3: ALFWorld (134개 unseen 태스크)**:
- 3-에이전트 Average **69%**, Best of 3 **77%** vs 2-에이전트 54%
- Grounding agent 추가로 **+15%p** 향상

**A4: OptiGuide (Multi-Agent Coding)**:
- Multi-GPT4 F1 **96%** / Recall **98%** vs Single-GPT4 88% / 78%
- 코드 430줄 → 100줄 (77% 감소), 사용자 작업 시간 3배 절감

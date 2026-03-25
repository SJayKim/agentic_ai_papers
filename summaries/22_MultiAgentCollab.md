# Multi-Agent Collaboration Mechanisms: A Survey of LLMs

> **논문 정보**: Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O'Sullivan, Hoang D. Nguyen (University College Cork, Pusan National University, Trinity College Dublin)
> **arXiv**: 2025
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 다중 에이전트 시스템(MAS)이 급성장하지만, 에이전트 간 협업의 메커니즘(유형, 구조, 전략, 조율)에 대한 포괄적 분석이 부족하다. 기존 서베이들은 단일 에이전트에 집중하거나, 협업의 특정 측면만 다루며, 체계적 프레임워크를 제공하지 못한다. |
| **Motivation** | 인간 사회의 집단 지성(society of mind, theory of mind)에서 영감을 받아, AI 에이전트도 협업을 통해 개별 능력을 넘어서는 문제를 해결할 수 있다. MAS는 지식 기억 분산, 장기 계획, 효과적 일반화, 상호작용 효율성에서 단일 에이전트를 크게 초과한다. 이를 체계화하는 프레임워크가 필요하다. |
| **Limitation** | (1) LLM 기반 MAS가 빠르게 발전하여 출판 시점 이후의 연구를 반영하지 못함. (2) 협업 메커니즘의 분류가 일부 경계 사례에서 모호할 수 있음. (3) 실제 배포 환경에서의 협업 효율성에 대한 정량적 비교가 제한적. (4) 보안·프라이버시·확장성 등 실용적 도전과제의 깊이 있는 분석이 부족. |

---

## Method

이 서베이는 LLM 기반 MAS의 협업 메커니즘을 **5개 차원**으로 체계화하는 확장 가능한 프레임워크를 제안한다.

1. **Actors (행위자)**
   - 협업에 참여하는 에이전트의 구성: 동질적(같은 LLM) vs 이질적(다른 LLM/역할)
   - 역할 특화: 리더, 비평가, 연구자, 코더 등

2. **Types (협업 유형)**
   - **Cooperation (협력)**: 공동 목표를 위해 협력 — 가장 보편적
   - **Competition (경쟁)**: 토론/디베이트를 통해 더 나은 해결책 도출
   - **Coopetition (협경)**: 협력과 경쟁의 혼합 — 일부 에이전트는 협력하고 다른 에이전트와 경쟁

3. **Structures (구조)**
   - **Peer-to-peer**: 평등한 에이전트 간 직접 소통
   - **Centralized**: 중앙 관리자가 조율 (예: Manager-Worker)
   - **Distributed**: 분산된 의사결정, 공유 메시지 풀
   - **Hierarchical**: 다층 구조 (예: 전략-전술-실행 레벨)

4. **Strategies (전략)**
   - **Role-based**: 에이전트에 역할/페르소나 할당 (예: Generative Agents, ChatDev)
   - **Rule-based**: 규칙 기반 턴제/투표 메커니즘 (예: LLM Debate의 라운드 제한)
   - **Model-based**: LLM이 동적으로 전략 결정 (예: 자동 역할 할당, 적응적 소통)

5. **Coordination Protocols (조율 프로토콜)**
   - 메시지 형식, 턴 순서, 종료 조건, 합의 메커니즘
   - 동기식 vs 비동기식 소통
   - 공유 메모리/블랙보드 vs 직접 메시지

---

## Key Contribution

1. **5차원 협업 프레임워크**: Actors, Types, Structures, Strategies, Coordination Protocols로 MAS 협업을 체계적으로 분류하는 확장 가능한 프레임워크.
2. **기존 서베이 대비 포괄성**: 기존 서베이들이 간과한 경쟁·협경(coopetition) 유형과 조율 프로토콜을 포함하여 가장 포괄적인 협업 분석.
3. **다양한 응용 도메인 분석**: 5G/6G 네트워크, Industry 5.0, QA, 사회·문화 시뮬레이션 등 실세계 응용 사례 리뷰.
4. **미래 연구 방향 제시**: 인간-AI 협업, 신뢰성, 확장성, 문화적 맥락 등 열린 문제와 연구 방향 식별.

---

## Experiment & Results

서베이 논문으로서 자체 실험 대신 **체계적 문헌 분석**을 수행:

- **분석 대상**: LLM 기반 MAS 관련 100편 이상의 논문을 5차원 프레임워크로 분류
- **주요 발견**:
  - Cooperation이 가장 보편적인 협업 유형이나, Competition(디베이트)이 추론 품질 향상에 효과적
  - Centralized 구조가 가장 흔하나, Distributed 구조가 확장성에서 유리
  - Role-based 전략이 압도적으로 많이 사용됨 — ChatDev, Generative Agents 등
  - 대부분의 MAS가 동기식 턴 기반 소통을 사용하며, 비동기식 접근은 아직 초기 단계

- **응용 도메인별 분석**:
  - 소프트웨어 개발: ChatDev, MetaGPT — centralized, role-based cooperation
  - 사회 시뮬레이션: Generative Agents — distributed, cooperation
  - 과학 연구: 다중 전문가 에이전트 — hierarchical cooperation
  - 5G/6G: 분산 자원 관리 — distributed coopetition

- **열린 문제**: (1) 에이전트 수 확장 시 소통 비용 폭발, (2) 이질적 LLM 간 상호운용성, (3) MAS의 안전성·정렬 문제, (4) 동적 팀 구성과 역할 재할당

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Taxonomy/분류 체계** | **5차원 분류**: (1) Actors — 동질적/이질적, (2) Types — Cooperation/Competition/Coopetition, (3) Structures — Peer-to-peer/Centralized/Distributed/Hierarchical, (4) Strategies — Role-based/Rule-based/Model-based, (5) Coordination — 메시지 형식/턴 순서/종료 조건/합의 메커니즘 |

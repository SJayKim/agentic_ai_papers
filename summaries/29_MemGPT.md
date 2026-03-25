# MemGPT: Towards LLMs as Operating Systems

> **논문 정보**: Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez (UC Berkeley)
> **arXiv**: 2310.08560 (2023.10)
> **코드**: https://research.memgpt.ai

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM의 고정 길이 컨텍스트 윈도우(8k~128k 토큰)는 장기 대화와 대규모 문서 분석을 심각하게 제한한다. 컨텍스트를 직접 확장하면 self-attention의 이차 복잡도로 비용이 급증하고, 최근 연구는 긴 컨텍스트 모델조차 중간 부분의 정보를 효과적으로 활용하지 못함을 보여준다(Lost in the Middle). |
| **Motivation** | 법률/재무 문서(100만+ 토큰), 수백 회의 대화 세션 등 실제 애플리케이션은 현재 모델의 컨텍스트 한계를 훨씬 초과한다. 단순한 컨텍스트 스케일링의 수확 체감(diminishing returns)을 고려하면, 고정 컨텍스트 모델에서 무한 컨텍스트의 환상을 제공하는 대안적 접근이 필요하다. |
| **Limitation** | 저자 언급: MemGPT가 검색 결과를 끝까지 페이징하지 않고 조기 종료하는 경향, 기반 모델의 function calling 능력에 크게 의존. 독자 관점: 메모리 관리 결정이 전적으로 LLM의 판단에 의존하여 중요 정보 유실 가능성 존재. 컨텍스트 관리의 오버헤드(추가 LLM 호출)가 크며, 실시간 시스템에서의 지연 비용 미분석. 오픈소스 모델에서의 성능 검증 부족. |

---

## Method

1. **OS 영감의 계층적 메모리 아키텍처**
   - **Main Context (RAM)**: LLM의 프롬프트 토큰 공간. 세 영역으로 구성:
     - *System Instructions*: 읽기 전용 — MemGPT 시스템 프롬프트, 메모리 계층 설명, 함수 스키마
     - *Working Context*: 읽기/쓰기 — 에이전트가 함수 호출로 직접 수정하는 핵심 정보 저장소
     - *FIFO Queue*: 읽기/쓰기 — 최근 메시지와 함수 결과가 큐에 적재
   - **External Context (Disk)**: 프롬프트 외부의 영구 저장소
     - *Recall Storage*: 전체 대화 이력을 시간순으로 저장 (검색 가능)
     - *Archival Storage*: 임의 길이의 텍스트 데이터 저장 (문서, 지식 등)

2. **가상 컨텍스트 관리 (Virtual Context Management)**
   - LLM이 function call로 Main Context ↔ External Context 간 데이터를 자율적으로 페이징
   - **Memory Pressure 경고**: FIFO 큐가 컨텍스트 윈도우의 70%에 도달하면 시스템 경고 → LLM이 중요 정보를 Working Context나 Archival Storage로 이동
   - **Queue Flush**: 100% 도달 시 큐의 50%를 축출, 축출된 메시지로 재귀적 요약 생성, 원본은 Recall Storage에 보존

3. **이벤트 기반 제어 흐름 & Function Chaining**
   - 이벤트(사용자 메시지, 시스템 경고, 타이머 등)가 LLM 추론을 트리거
   - `request_heartbeat=true` 플래그로 함수 호출을 연쇄 실행 — 다중 검색, 다중 소스 정보 수집 가능
   - 플래그 미지정 시 yield → 다음 외부 이벤트까지 대기

4. **자기 주도적 메모리 편집**
   - LLM이 자율적으로 Working Context를 append/replace/삭제하여 진화하는 이해를 반영
   - 함수 실행 결과(오류 포함)가 피드백 루프로 재전달되어 행동 조정

---

## Key Contribution

1. **OS 가상 메모리 개념의 LLM 적용**: 물리 메모리(컨텍스트 윈도우)와 디스크(외부 저장소) 간 페이징 개념을 LLM에 이식하여, 고정 컨텍스트에서 무한 컨텍스트의 환상을 제공하는 최초의 체계적 설계
2. **자율적 메모리 관리 에이전트**: LLM이 function calling으로 자신의 컨텍스트를 능동적으로 관리(읽기/쓰기/검색/축출)하는 self-directed editing 패러다임 제시
3. **두 도메인에서의 실증**: 장기 대화(멀티세션 채팅)와 대규모 문서 분석에서 고정 컨텍스트 baseline 대비 압도적 성능 향상 입증

---

## Experiment & Results

- **평가 도메인**: (1) 대화형 에이전트 — Multi-Session Chat(MSC) 데이터셋, (2) 문서 분석 — NaturalQuestions-Open, KV 검색
- **Baseline**: GPT-3.5 Turbo, GPT-4, GPT-4 Turbo (고정 컨텍스트)

**Deep Memory Retrieval (DMR)** — 이전 대화 세션의 구체적 정보 회상:
- GPT-4: 32.1% → MemGPT+GPT-4: **92.5%** (+60.4%), ROUGE-L: 0.296 → 0.814
- GPT-4 Turbo: 35.3% → MemGPT: **93.4%**, ROUGE-L: 0.827

**Conversation Opener** — 이전 대화 기반 자연스러운 대화 개시:
- MemGPT+GPT-3.5: SIM-H 0.817로 인간 작성 opener(1.000)에 근접, 일부 메트릭에서 인간 초과

**Document QA** — 대규모 문서에서 질문 응답:
- 고정 컨텍스트 baseline은 검색된 문서 수 증가에 따라 성능 포화
- MemGPT는 반복적 archival storage 검색으로 검색 문서 수에 무관하게 안정적 성능 유지

**Nested KV Retrieval** — 다중 홉 키-값 조회:
- GPT-3.5: nesting 1에서 0% 정확도
- GPT-4 Turbo: nesting 2 이상에서 급격한 성능 하락
- MemGPT+GPT-4: nesting 3까지 일관된 성능 유지 — 유일하게 다중 홉 완수

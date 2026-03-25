# BUTTON: Facilitating Multi-Turn Function Calling for LLMs via Compositional Instruction Tuning

> **논문 정보**: Mingyang Chen, Haoze Sun, Tianpeng Li, Fan Yang, Hao Liang, Keer Lu, Bin Cui, Wentao Zhang, Zenan Zhou, Weipeng Chen (Baichuan Inc., Peking University)
> **arXiv**: ICLR 2025
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM function calling 연구가 단일 턴(single-turn)에 집중하여, 복합적 실세계 쿼리를 다단계로 분해하고 순차적으로 함수를 호출하는 멀티턴 능력이 부족하다. 실세계 태스크는 본질적으로 조합적(compositional)이며 계획이 필요하다. |
| **Motivation** | "The Great Gatsby 저자의 생일은?" 같은 질문은 (1) 저자 검색 → (2) 생일 검색의 순차적 함수 호출이 필요하다. 이런 조합적 instruction tuning 데이터를 수집하기 어렵고, 기존 합성 데이터 파이프라인은 조합성·호환성·다턴 궤적 품질을 보장하지 못한다. |
| **Limitation** | (1) Sequential과 Parallel-then-Sequential 두 가지 조합 전략만 사용하여, 더 복잡한 조합 패턴(조건부 분기 등)은 미포함. (2) 함수 정의가 합성되어 실제 API와의 호환성이 불확실. (3) 8K 데이터포인트로 규모가 제한적. (4) 함수 실행이 시뮬레이션되어 실제 API 호출 오류 처리는 미검증. |

---

## Method

BUTTON은 **Bottom-Up(상향식) 지시 구성**과 **Top-Down(하향식) 궤적 생성**의 2단계 파이프라인으로 멀티턴 function calling 데이터를 합성한다.

1. **Bottom-Up Instruction Construction**
   - **Atomic Task Construction**: 실세계 시나리오에서 단순·명확·단일 단계로 해결 가능한 원자 태스크 생성
   - **Compositional Task Construction**: 원자 태스크를 두 가지 전략으로 조합
     - **Sequential Composition**: 원자 태스크 → 결과에 의존하는 후속 태스크 생성 → 결합
     - **Parallel-then-Sequential**: 원자 태스크 + 병렬 태스크 → 두 결과에 의존하는 후속 태스크 → 결합
   - **Function Generation**: 조합 태스크와 원자 태스크 분해를 참조하여 함수 정의 생성 (태스크 먼저, 함수 나중)
   - 원자 태스크의 존재가 함수 생성 시 힌트로 작용 — 기존 방법(함수 먼저 → 태스크)보다 현실적

2. **Top-Down Trajectory Generation**
   - 3-에이전트 시뮬레이션 환경: User Agent, Assistant Agent, Tool Agent
   - User Agent: 조합적 쿼리 제시 + 추가 정보 제공
   - Assistant Agent: ReAct 형식으로 사고+함수 호출, 최종 답변 생성
   - Tool Agent: 함수 정의에 기반하여 실행 결과 시뮬레이션
   - 일관성 보장: 각 assistant 행동을 다수 생성 후 일관된 결정만 채택

3. **BUTTONInstruct 데이터셋**: GPT-4o로 생성, 8,000개 멀티턴 function calling 데이터포인트

---

## Key Contribution

1. **Bottom-Up Then Top-Down 파이프라인**: 원자 태스크에서 조합 태스크를 구성하여 조합성을 보장하고, 하향식으로 궤적을 생성하여 다턴 계획을 학습할 수 있는 데이터 합성 방법론.
2. **태스크 우선 함수 생성**: 기존의 함수 우선 접근과 반대로, 태스크를 먼저 구성한 후 함수를 생성하여 더 현실적이고 다양한 시나리오 보장.
3. **8K 데이터로 SOTA**: 소규모 합성 데이터만으로도 다양한 LLM의 멀티턴 function calling 능력을 크게 향상.

---

## Experiment & Results

**모델**: Llama-3-8B-Instruct, Llama-3-70B-Instruct, Mistral-7B-Instruct 등에 BUTTONInstruct로 파인튜닝

**벤치마크**: BFCL (Berkeley Function Calling Leaderboard), API-Bank, ToolBench 등

**데이터 통계**: 평균 3-4턴/궤적, 평균 2-3 function call/궤적, 턴이 진행될수록 FC 수 증가

**주요 결과**:
- BUTTONInstruct로 파인튜닝된 모델이 기존 function calling 데이터(Gorilla, ToolAlpaca 등)로 학습된 모델을 일관되게 초과
- 멀티턴 function calling에서 특히 큰 개선 — 조합적 태스크에서의 계획 능력 향상
- 기존 합성 데이터 파이프라인 대비 조합성·다양성·정확성에서 우위

**Ablation**: Sequential과 Parallel-then-Sequential 조합 전략이 각각 다른 유형의 멀티턴 능력에 기여. 두 전략을 함께 사용했을 때 최고 성능.

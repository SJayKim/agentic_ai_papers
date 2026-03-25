# ToolACE: Winning the Points of LLM Function Calling

> **논문 정보**: Weiwen Liu, Xu Huang, Xingshan Zeng 외 다수 (Huawei Noah's Ark Lab, SJTU, USTC, Tsinghua, CUHK)
> **arXiv**: ICLR 2025
> **코드**: https://huggingface.co/Team-ACE

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM의 function calling 능력을 위한 고품질·다양한 학습 데이터가 부족하다. 실제 function calling 데이터 수집·주석이 어렵고, 기존 합성 데이터 파이프라인은 API 커버리지가 제한적이고 복잡한 시나리오(nested, parallel, dependent 호출)를 충분히 다루지 못한다. |
| **Motivation** | 실세계 function calling은 다양한 API와 복잡한 호출 패턴(병렬, 의존적, 중첩 파라미터)을 요구한다. 기존 도구(Gorilla 1,645 API, ToolLLM 16,464 API)보다 훨씬 넓은 커버리지와 정확한 데이터가 필요하며, 모델 능력에 맞춰 데이터 복잡도를 조절해야 한다. |
| **Limitation** | (1) Self-evolution으로 생성된 합성 API가 실제 API와 동작이 다를 수 있다. (2) 데이터 생성에 frontier LLM을 사용하여 비용이 상당. (3) 8B 모델에서의 결과가 주로 보고되어, 더 큰/작은 모델에서의 효과는 제한적으로 검증. (4) DLV의 규칙 기반 검증이 모든 오류 유형을 커버하지 못할 수 있다. |

---

## Method

ToolACE는 **자기 진화 API 합성(TSS)**, **자기 안내 대화 생성(SDG)**, **이중 검증(DLV)**의 3모듈로 정확하고 다양하고 복잡한 function calling 데이터를 자동 생성한다.

1. **Tool Self-Evolution Synthesis (TSS)**
   - **Speciation (종분화)**: 사전학습 데이터에서 API 도메인·기능을 추출하여 계층적 API Context Tree 구축
   - **Adaptation (적응)**: 서브트리에서 경로를 샘플링하여 API의 도메인·다양성 수준 지정
   - **Evolution (진화)**: 기존 API 예시를 기반으로 새 API 정의 생성, 반복적 self-evolution으로 API 풀 확장
   - 결과: **26,507개 다양한 API**, 390개 도메인 — 기존 최대(ToolLLM 16,464) 대비 60% 이상 확장
   - Nested 파라미터(리스트의 리스트, 딕셔너리 리스트) 지원

2. **Self-Guided Dialog Generation (SDG)**
   - **Multi-Agent Generator**: User/Assistant/Tool 3-에이전트 역할극으로 4가지 대화 유형 생성
     - Single function call, Parallel function calls, Dependent function calls, Non-tool-use
   - **Complexity Evaluator**: 학습 대상 LLM 자체가 데이터 복잡도를 평가
     - 너무 쉬운/어려운 데이터는 동적으로 조정 — 모델 능력에 맞춘 최적 복잡도
   - Self-guided complication: User 에이전트가 점진적으로 요구 복잡도 증가

3. **Dual-Layer Validation (DLV)**
   - **Rule Checker**: 타입 체킹, 값 제약 조건, 형식 검증, 일관성 검사
   - **Model Checker**: LLM 기반 의미적 검증 + 인간 검증 샘플링
   - 이중 검증으로 실행 가능성과 정확성 보장

---

## Key Contribution

1. **자기 진화 API 풀**: 사전학습 데이터에서 시작하여 26,507개 API를 자동 생성하는 TSS 모듈. 기존 대비 가장 넓은 API/도메인 커버리지.
2. **모델 인식 복잡도 조절**: 학습 대상 모델이 직접 데이터 복잡도를 평가하여, 모델 능력에 최적화된 학습 데이터 생성.
3. **포괄적 function calling 지원**: Nested 파라미터, Parallel/Dependent 호출, Multi-type 대화를 모두 지원하는 유일한 파이프라인.
4. **8B 모델로 GPT-4급 성능**: 합성 데이터로 학습된 8B 모델이 BFCL 리더보드에서 GPT-4 수준 달성.

---

## Experiment & Results

**벤치마크**: BFCL-v3 (Berkeley Function Calling Leaderboard), API-Bank

**주요 결과**:
- ToolACE-8B: BFCL-v3 Overall **59.22%** (3위, GPT-4급)
- API-Bank: Call Accuracy **75.94%**
- 기존 오픈소스 도구 학습 모델(Gorilla, ToolLLM, xLAM 등)을 크게 초과

**Ablation - 데이터 구성요소별 효과**:
- **Accuracy (DLV)**: 검증 제거 시 성능 하락 — 데이터 정확성의 중요성
- **Complexity (SDG)**: self-guided 복잡도 조절 제거 시 성능 하락 — 적절한 난이도가 핵심
- **Diversity (TSS)**: API 다양성 감소 시 zero-shot 일반화 저하

**API 풀 비교 (Table 1)**:
- ToolACE: 26,507 API, 390 도메인, Nested ✓, Parallel ✓, Dependent ✓, Multi-type ✓
- ToolLLM: 16,464 API, 49 도메인, Dependent만 ✓
- Gorilla: 1,645 API, 3 도메인
- 모든 차원에서 ToolACE가 가장 포괄적

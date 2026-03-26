# ToolLLM: Facilitating Large Language Models to Master 16000+ Real-World APIs

> **논문 정보**: Yujia Qin, Shihao Liang, Yining Ye 외 (Tsinghua University, OpenBMB, Yale, Tencent)
> **arXiv**: 2307.16789 (2023.07)
> **코드**: https://github.com/OpenBMB/ToolBench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 오픈소스 LLM(LLaMA 등)은 인스트럭션 튜닝이 기본 언어 태스크에 집중되어 도구 사용 능력이 심각하게 부족하다. 기존 도구 학습 연구는 소수의 비현실적 API만 다루거나, 단일 도구 시나리오에 국한되며, 추론 전략이 CoT/ReAct에 머물러 있다. |
| **Motivation** | ChatGPT/GPT-4는 뛰어난 도구 사용 능력을 보이지만 폐쇄적이다. 16,000+ 실제 REST API를 다루는 대규모 도구 학습 데이터셋과 더 강력한 추론 전략이 필요. |
| **Limitation** | 저자 언급: RapidAPI의 API 품질이 불균일하고 일부 API가 다운되는 문제. 독자 관점: ChatGPT로 생성한 학습 데이터의 품질 상한이 ChatGPT 수준. DFSDT의 높은 탐색 비용. |

---

## Method

1. **ToolBench 데이터셋 구축 (3단계)**
   - **API Collection**: RapidAPI Hub에서 49개 카테고리, 16,464개 실제 REST API 수집
   - **Instruction Generation**: ChatGPT로 단일도구/카테고리내 멀티도구/컬렉션간 멀티도구 시나리오의 다양한 지시문 생성
   - **Solution Path Annotation**: ChatGPT가 DFSDT로 유효한 솔루션 경로(API 호출 체인) 탐색

2. **DFSDT (Depth-First Search Decision Tree)**
   - ReAct의 선형 추론을 트리 구조로 확장
   - 각 추론 단계에서 여러 분기를 탐색하고, 실패 시 백트래킹
   - 탐색 공간을 효율적으로 확장하여 복잡한 멀티도구 지시문 해결

3. **ToolLLaMA**: ToolBench로 LLaMA를 파인튜닝. 신경망 API 검색기로 적절한 API를 자동 추천

4. **ToolEval**: Pass Rate(태스크 완수율) + Win Rate(ChatGPT 대비 승률)의 자동 평가 체계

---

## Key Contribution

1. **16,000+ 실제 API 기반 대규모 도구 학습**: REST API 생태계를 포괄하는 최초의 대규모 벤치마크/학습 데이터
2. **DFSDT 추론 전략**: ReAct 대비 더 넓은 탐색 공간으로 복잡한 멀티도구 태스크 해결
3. **오픈소스 모델의 도구 사용 능력 민주화**: ToolLLaMA가 ChatGPT에 필적하는 성능 달성

---

## Experiment & Results

- **모델**: ToolLLaMA (LLaMA 기반), ChatGPT, GPT-4, Claude-2, Text-Davinci-003
- **평가**: ToolEval (Pass Rate + Win Rate vs ChatGPT-ReAct)

**주요 결과**:
- ToolLLaMA-DFSDT: Pass Rate ~65%, Win Rate ~50% (ChatGPT-ReAct 대비 동등)
- GPT-4-DFSDT가 최고 성능, ToolLLaMA가 그 다음으로 Claude-2를 초과
- DFSDT가 ReAct 대비 모든 모델에서 일관된 개선 (Pass Rate +5~15%)
- 미학습 API(APIBench)에서도 강한 zero-shot 일반화

# ToolLLM: Facilitating Large Language Models to Master 16000+ Real-World APIs

> **논문 정보**: Yujia Qin, Shihao Liang, Yining Ye 외 (Tsinghua University, OpenBMB, Yale, Tencent)
> **arXiv**: 2307.16789 (2023.07)
> **코드**: https://github.com/OpenBMB/ToolBench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 오픈소스 LLM(LLaMA 등)은 인스트럭션 튜닝이 기본 언어 태스크에 집중되어 도구 사용 능력이 심각하게 부족하다. 기존 도구 학습 연구는 소수의 비현실적 API만 다루거나 단일 도구 시나리오에 국한되며, CoT/ReACT 기반 추론은 오류 전파와 탐색 공간 제한으로 복잡한 다중 도구 태스크를 해결하지 못한다. |
| **Motivation** | ChatGPT/GPT-4는 뛰어난 도구 사용 능력을 보이지만 폐쇄적이다. 16,000+ 실제 REST API를 다루는 대규모 도구 학습 데이터셋과 트리 기반 탐색 추론 전략이 필요하다. |
| **Limitation** | (1) RapidAPI의 API 품질이 불균일하고 일부 API가 런타임 중 다운되는 문제. (2) ChatGPT로 생성한 학습 데이터의 품질 상한이 ChatGPT 수준으로 제한됨. (3) DFSDT는 ReACT 대비 API 호출 횟수가 많아 추론 비용이 높음. (4) 평가 체계(ToolEval)가 ChatGPT 기반이므로 평가자 편향 가능성 존재. |

---

## Method

### 1. ToolBench 데이터셋 구축 (3단계)

**1-1. API Collection**
- RapidAPI Hub에서 49개 카테고리, 3,451개 고품질 도구, 16,464개 실제 REST API 수집
- 초기 10,853개 도구(53,190개 API)에서 엄격한 필터링 (404 에러, 비응답 API 제거)
- 각 API에 이름, 설명, HTTP 메서드, 필수/선택 파라미터, 코드 스니펫, 예시 응답 포함

**1-2. Instruction Generation**
- ChatGPT로 세 시나리오의 지시문 자동 생성:
  - I1: 단일 도구 (87,413개), I2: 카테고리 내 멀티 도구 (84,815개), I3: 컬렉션 간 멀티 도구 (25,251개)
- 인간 전문가 작성 시드 예시를 in-context learning으로 활용

**1-3. Solution Path Annotation (DFSDT)**
- 각 지시문에 대해 ChatGPT가 유효한 API 호출 체인을 탐색
- 최종 126,486개 (instruction, solution path) 쌍 확보

### 2. DFSDT (Depth-First Search Decision Tree)

- ReACT의 두 핵심 문제 해결: **오류 전파**(잘못된 액션이 이후 추론을 오염)와 **탐색 제한**(단일 경로만 탐색)
- 각 추론 단계에서 여러 분기를 생성하고, 실패 노드에서 백트래킹 후 새로운 노드 확장
- BFS 대신 DFS 채택: 하나의 유효 경로만 찾으면 완료되므로 API 호출 비용 절감
- ChatGPT+DFSDT: ReACT Pass Rate 35.3% → DFSDT 63.8%

### 3. ToolLLaMA 모델

- LLaMA-2 7B를 ToolBench의 instruction-solution 쌍으로 파인튜닝
- Positional interpolation으로 컨텍스트 4096 → 8192 확장
- 신경망 API 검색기 결합: 16,000+ API 풀에서 상위 5개 API 자동 추천 (NDCG@5=84.9)

### 4. ToolEval 자동 평가

- Pass Rate: 제한된 예산 내 성공 완수 비율
- Win Rate: ChatGPT-ReACT 대비 솔루션 경로 품질 승률

---

## Key Contribution

1. **16,000+ 실제 API 기반 대규모 벤치마크**: REST API 생태계를 포괄하는 최초의 대규모 벤치마크 (기존 최대: APIBench 1,645개)
2. **DFSDT 추론 전략**: 트리 기반 탐색으로 ReACT 대비 Pass Rate 최대 35%p 향상
3. **오픈소스 도구 사용 능력 민주화**: ToolLLaMA-DFSDT가 Text-Davinci-003, Claude-2를 초과하고 ChatGPT에 필적
4. **신경망 API 검색기**: Ground Truth API보다 더 나은 Pass Rate 달성

---

## Experiment & Results

- **모델**: ToolLLaMA (LLaMA-2 7B), ChatGPT, GPT-4, Claude-2, Vicuna, Alpaca
- **평가**: 6개 설정 (I1-Inst., I1-Tool, I1-Cat., I2-Inst., I2-Cat., I3-Inst.)

**메인 결과 (ToolBench)**:
- ToolLLaMA-DFSDT: 평균 Pass Rate 66.7%, Win Rate 60.0%
- ToolLLaMA-DFSDT-Retriever: Pass Rate 67.3%, Win Rate 63.1%
- ChatGPT-DFSDT: Pass Rate 64.8%, Win Rate 64.3% — ToolLLaMA와 동등
- GPT-4-DFSDT: Pass Rate 71.1%, Win Rate 70.4% — 전체 최고
- Claude-2-DFSDT: Pass Rate 22.6% / Vicuna·Alpaca: 0.0%

**DFSDT vs ReACT (ChatGPT)**:
- ReACT 35.3% → DFSDT 63.8% (평균 Pass Rate)
- I3(멀티 도구): ReACT 27.6% → DFSDT 62.8% (+35.2%p)

**API 검색기**: BM25 NDCG@5=17.0 / Ada 45.4 / 본 연구 84.9

**OOD 일반화 (APIBench)**: ToolLLaMA+Retriever가 Gorilla-ZS+BM25 대비 HuggingFace AST 16.77 vs 10.51, TorchHub 51.16 vs 44.62로 우세

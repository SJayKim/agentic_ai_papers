# MASS: Multi-Agent System Search — Optimizing Agents with Better Prompts and Topologies

> **논문 정보**: Han Zhou, Xingchen Wan, Ruoxi Sun, Hamid Palangi, Shariq Iqbal, Ivan Vulić, Anna Korhonen, Sercan Ö. Arık (Google, University of Cambridge)
> **arXiv**: 2502.02533v2 (2026.01, ICLR 2026)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 멀티에이전트 시스템(MAS) 설계 시 프롬프트와 토폴로지를 동시에 최적화해야 하지만, 프롬프트 민감성의 복합 효과와 조합적 탐색 공간의 폭발로 인해 수동 설계가 극도로 비효율적이다. 기존 자동화 방법(ADAS, AFlow 등)은 토폴로지 탐색에만 집중하고 프롬프트 최적화를 간과하여 MAS 성능이 제한된다. |
| **Motivation** | 단일 에이전트에서도 프롬프트의 사소한 변경이 성능을 크게 좌우하는데, MAS에서는 에이전트 간 종속성으로 이 효과가 증폭된다. 분석 결과, 프롬프트 최적화가 에이전트 수 확장(SC, Reflect, Debate)보다 토큰 효율성 면에서 훨씬 우수하며, 유효한 토폴로지는 전체 탐색 공간의 극히 일부에 불과함을 발견. |
| **Limitation** | (1) 토폴로지 구성 순서가 고정 규칙([summarize, reflect, debate, aggregate])에 의존하여 순서 자체의 최적화가 빠져 있음. (2) 검증/테스트 셋이 원본에서 랜덤 샘플링한 소규모 서브셋(50~200개)이라 대규모 평가에서의 안정성이 불확실. (3) 최적화 비용이 약 $5(24M input/11M output tokens)로, 태스크마다 별도 최적화가 필요하여 범용 적용 시 비용 부담. (4) sparse communication 등 추가 토폴로지 통합 여지가 남아 있음. |

---

## Method

MASS는 프롬프트와 토폴로지를 **local-to-global로 인터리빙 최적화**하는 3단계 프레임워크다.

1. **설계 공간 정의**
   - **빌딩 블록**: Aggregate(병렬 예측 앙상블), Reflect(자기 반성), Debate(다중 에이전트 토론), Summarize(긴 입력 요약), Tool-use(외부 도구 사용)
   - 블록들의 연결로 워크플로우 토폴로지 구성
   - 블록별 최적화 가능한 프롬프트: instruction + few-shot exemplar

2. **Stage 1: Block-level Prompt Optimization (1PO)**
   - 각 빌딩 블록에 대해 개별적으로 프롬프트 최적화 수행
   - MIPRO를 사용하여 instruction과 exemplar를 동시 최적화
   - 각 블록의 incremental influence(검증 성능 향상도)를 측정
   - 핵심 원칙: "에이전트를 로컬에서 먼저 최적화한 후 토폴로지를 확장"

3. **Stage 2: Workflow Topology Optimization (2TO)**
   - 1단계에서 측정한 influence 기반으로 Softmax 확률을 계산하여 탐색 공간 pruning
   - 유효 토폴로지가 전체의 소수임을 활용 — 부정적 영향 블록 배제
   - Rejection sampling으로 유효한 토폴로지 후보를 생성하고 평가
   - 규칙 기반 순서([summarize, reflect, debate, aggregate])로 워크플로우 구성

4. **Stage 3: Workflow-level Prompt Optimization (3PO)**
   - 최적 토폴로지가 결정된 후, 전체 MAS를 하나의 통합 시스템으로 보고 모든 에이전트의 프롬프트를 동시에 재최적화
   - 에이전트 간 상호의존성을 반영하여 글로벌 최적화
   - 1PO에서 찾은 프롬프트를 초기화로 사용하여 수렴 가속

---

## Key Contribution

1. **MAS 설계 공간 심층 분석**: 프롬프트가 토폴로지만큼 중요하며, 유효 토폴로지가 전체의 소수임을 실증적으로 밝힘. "프롬프트 먼저, 토폴로지 나중" 원칙 도출.
2. **3단계 인터리빙 최적화**: local(블록별) → global(워크플로우) 순서로 프롬프트와 토폴로지를 교대 최적화하여 조합 폭발 문제 해결.
3. **8개 벤치마크 SOTA**: 기존 수동/자동 MAS 설계를 큰 폭으로 초과하는 성능 달성.
4. **MAS 설계 원칙 도출**: MASS가 발견한 최적 MAS 구조로부터 태스크 유형별 효과적인 토폴로지 패턴 제시.

---

## Experiment & Results

**모델**: Gemini 1.5 Pro, Gemini 1.5 Flash, Claude 3.5 Sonnet, Mistral Nemo

**벤치마크 8개**: MATH, DROP, MBPP, HumanEval, LiveCodeBench(LCB), HotpotQA, MMLU, ARC-C

**Gemini 1.5 Pro 결과 (8개 태스크 평균)**:
- MASS: **78.79%** vs CoT 65.28%, Multi-Agent Debate 70.26%, ADAS 69.72%
- 태스크별: MATH **84.67%**(CoT 71.67%), DROP F1=**90.52**(CoT 70.59%), MBPP **86.50%**(CoT 68.33%), HumanEval **91.67%**(CoT 86.67%), LCB **82.33%**(CoT 66.33%)

**교차 모델 결과**:
- Gemini 1.5 Flash 평균 **74.30%** (CoT 60.87%)
- Claude 3.5 Sonnet 평균 **72.43%** (CoT 60.21%)
- Mistral Nemo 평균 **55.9%** (CoT 40.4%)

**단계별 Ablation**: Base 63.5% → +APO 68.0% → +1PO 74.2% → +2TO 77.3% → +3PO 78.8%. 1PO가 가장 큰 기여(+6%p).

**비용 효율**: 쿼리당 $0.0014로 ADAS($0.0016)와 비슷하면서 성능은 크게 우수(81.0% vs 72.7%).

**MASS 발견 패턴**: 추론 태스크(MATH, DROP)는 Aggregate(병렬 탐색) 선호, 멀티홉(HotpotQA)은 Debate 선호, 코딩은 Reflect+Tool-use 조합 선호.

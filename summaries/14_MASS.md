# MASS: Multi-Agent System Search — Optimizing Agents with Better Prompts and Topologies

> **논문 정보**: Han Zhou, Xingchen Wan, Ruoxi Sun, Hamid Palangi, Shariq Iqbal, Ivan Vulić, Anna Korhonen, Sercan Ö. Arık (Google, University of Cambridge)
> **arXiv**: 2502.02533 | **학회**: ICLR 2026
> **코드**: 미공개

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)은 복잡한 태스크에서 단일 에이전트보다 뛰어난 성능을 보이지만, 효과적인 MAS 설계는 극도로 어렵다. 개별 에이전트의 프롬프트 민감성(prompt sensitivity) 문제가 MAS에서는 에이전트가 캐스케이드로 연결되면서 복합적으로 증폭된다. 프롬프트 설계와 토폴로지(에이전트 간 연결 구조) 설계를 동시에 최적화해야 하는데, 이 결합 탐색 공간은 조합적 폭발을 야기한다. 기존 자동화 연구(DSPy, ADAS, AFlow)는 프롬프트 최적화 또는 토폴로지 최적화 중 하나에만 집중하여, 프롬프트와 토폴로지 간의 상호작용이 간과되었다. ADAS는 프롬프트 최적화 없이 복잡한 토폴로지를 생성하고, AFlow는 사전 정의 연산자의 프롬프트를 최적화하지 않아 성능 한계가 존재한다.

---

## Motivation

저자들은 MAS 설계 공간에 대한 심층 분석을 먼저 수행하여, 프롬프트 최적화가 토폴로지 확장보다 토큰 효율성 측면에서 훨씬 효과적이라는 사실을 밝혔다. 단순히 에이전트 수를 늘리는 Self-Consistency나 Debate보다 프롬프트를 최적화한 단일 에이전트가 더 적은 토큰으로 더 높은 정확도를 달성했다. 또한 토폴로지 분석에서 유익한 토폴로지는 전체 탐색 공간의 극히 일부에 불과하며, 일부 토폴로지는 오히려 성능을 저하시킨다는 점을 확인했다. 이러한 통찰은 NAS 연구에서 탐색 방법보다 탐색 공간 설계가 더 중요하다는 발견과 유사하다. 따라서 "개별 에이전트를 먼저 최적화한 후 토폴로지를 구성하라"는 원칙과, 영향력 있는 토폴로지만 선별하여 가지치기된 탐색 공간에서 탐색하라는 설계 철학이 도출되었다.

---

## Method

MASS는 local-to-global, prompt-to-topology 순서로 3단계 인터리빙 최적화를 수행한다.

1. **탐색 공간 — 5가지 빌딩 블록**: Aggregate(병렬 예측 + 다수결), Reflect(검증자 기반 반복 개선), Debate(다자 토론), Summarize(장문맥 요약), Tool-use(외부 도구 사용).

2. **Stage 1 — Block-level Prompt Optimization (1PO)**: 먼저 초기 Predictor에 대해 단일 에이전트 APO(MIPRO 활용)를 수행한다. 이어서 각 빌딩 블록을 최소 에이전트 구성으로 개별 프롬프트 최적화. 각 블록의 검증 성능과 증분 영향력(Incremental Influence) I = E(a*_i) / E(a*_0)을 계산한다.

3. **Stage 2 — Workflow Topology Optimization (2TO)**: 각 블록의 영향력 기반으로 선택 확률 p = Softmax(I, t)를 산출(t=0.05로 샤프닝). 확률 기반 가지치기로 유의미한 토폴로지만 남긴 탐색 공간에서 Rejection Sampling으로 10개 후보를 생성, 각각 검증셋에서 3회 평가하여 최적 워크플로우를 선정한다.

4. **Stage 3 — Workflow-level Prompt Optimization (3PO)**: 최적 토폴로지에 대해 전체 에이전트를 하나의 통합 엔티티로 간주하고 joint prompt optimization을 수행하여 에이전트 간 상호의존성을 모델링한다.

---

## Key Contribution

1. **MAS 설계 공간의 최초 체계적 분석**: 프롬프트 최적화가 에이전트 수 확장보다 토큰 효율적이며, 유익한 토폴로지는 전체 공간의 극소 비율임을 실증.
2. **3단계 인터리빙 최적화 프레임워크 MASS**: block-level PO → topology optimization → workflow-level PO의 local-to-global 구조.
3. **영향력 기반 탐색 공간 가지치기**: 증분 영향력 측정과 Softmax 가중 확률적 가지치기로 탐색 효율 향상.
4. **플러그앤플레이 설계**: 임의의 프롬프트 옵티마이저와 커스텀 토폴로지 블록을 자유롭게 통합 가능.
5. **MAS 설계 원칙 도출**: (a) 개별 에이전트를 먼저 최적화하라, (b) 영향력 있는 토폴로지만 조합하라, (c) 워크플로우 수준에서 상호의존성을 최적화하라.

---

## Experiment & Results

**평가 설정**: Gemini 1.5 Pro/Flash, Claude 3.5 Sonnet, Mistral Nemo. 8개 벤치마크 — MATH, DROP, HotpotQA, MuSiQue, 2WikiMQA, MBPP, HumanEval, LiveCodeBench.

**Gemini 1.5 Pro 평균**: MASS **78.79%** vs Multi-Agent Debate 70.26% vs ADAS 69.72% vs CoT 65.28%. 기존 수동 MAS 대비 +8.5%p, ADAS 대비 +9.1%p.
- MATH: **84.67%** (CoT 71.67%, ADAS 80.00%)
- DROP: **90.52%** F1 (CoT 70.59%, ADAS 72.96%)
- MBPP: **86.50%** pass@1 (CoT 68.33%, ADAS 73.00%)
- LiveCodeBench: **82.33%** (CoT 66.33%)

**Gemini 1.5 Flash 평균**: MASS **74.30%** vs Multi-Agent Debate 65.91% vs ADAS 64.75%. 더 작은 모델에서도 +8.4%p 이상 향상.

**단계별 기여도**: CoT → APO +4.5%p, APO → 1PO **+6.2%p**, 1PO → 2TO **+3.1%p**, 2TO → 3PO **+1.5%p**. 가지치기 없이 토폴로지 탐색 시 약 3%p 하락 확인.

**비용 효율성**: 추론 토큰 동일 수준으로 통제 시 MASS가 ADAS·AFlow 대비 더 안정적인 최적화 궤적. Claude 3.5 Sonnet과 Mistral Nemo에서도 일관된 향상.

---

## Limitation

- 3단계 최적화 전체를 수행하려면 상당한 검증 세트 평가와 LLM API 호출이 필요하며, 대규모 실시간 배포에 부담이 될 수 있다.
- 토폴로지 후보를 사전 정의된 규칙으로 조합하므로, 완전히 자유로운 그래프 구조의 에이전트 연결은 탐색하지 못한다.
- MIPRO를 기본 옵티마이저로 사용하며, 옵티마이저 자체의 성능 한계가 MASS의 상한을 제약한다.
- 각 태스크마다 검증 분할이 필요하며, 레이블이 없는 태스크에는 직접 적용이 어렵다.
- 빌딩 블록이 5개로 한정되어 계층적 위임, 동적 역할 전환 등은 다루지 않는다.
- 동일 모델을 모든 에이전트에 사용하며, 이종(heterogeneous) 모델 조합의 최적화는 탐구하지 않았다.

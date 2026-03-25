# AgentSquare: Automatic LLM Agent Search in Modular Design Space

> **논문 정보**: Yu Shang, Yu Li, Keyu Zhao, Likai Ma, Jiahe Liu, Fengli Xu, Yong Li (Tsinghua University)
> **arXiv**: 2410.06153 (2024.10, ICLR 2025)
> **코드**: https://github.com/tsinghua-fib-lab/AgentSquare

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 현재 LLM 에이전트 연구는 태스크별 수동 설계에 의존하여, 새로운 태스크에 대한 적응력이 제한적이다. 기존 자동화 연구(ADAS 등)는 전체 에이전트를 코드 공간에서 탐색하지만, 서로 다른 코드베이스에 있는 기존 에이전트 모듈의 강점을 명시적으로 재결합하지 못한다. |
| **Motivation** | 에이전트 아키텍처 연구에서 Planning(CoT, ToT), Reasoning(CoT, SoT), Tool Use(Toolformer), Memory(Generative Agents, Voyager) 등 성공적인 모듈이 각각 발견되었지만, 이들의 최적 조합을 찾는 것은 수동으로 불가능하다. 표준화된 모듈 설계 공간과 자동 탐색이 필요하다. |
| **Limitation** | (1) 4개 모듈(Planning/Reasoning/Tool Use/Memory)의 분류가 일부 에이전트에서는 경계가 모호할 수 있다. (2) 성능 예측기가 in-context surrogate 모델에 의존하여, 도메인 외 예측 정확도가 떨어질 수 있다. (3) 초기 모듈 풀이 수동으로 구성된 16개 에이전트에서 출발하므로, 풀의 품질에 의존. (4) 단일 에이전트 설계에 집중하여, 다중 에이전트 상호작용 최적화는 범위 밖. |

---

## Method

AgentSquare는 LLM 에이전트를 **4개 모듈의 모듈화된 설계 공간**에서 **진화와 재결합**으로 자동 탐색하는 프레임워크다.

1. **모듈화된 설계 공간 (4개 모듈)**
   - **Planning**: 태스크를 하위 태스크로 분해 — CoT, ToT, DEPS 등
   - **Reasoning**: 하위 태스크를 순차 해결 — CoT, ToT, SoT, ReAct 등
   - **Tool Use**: 외부 도구 선택·호출 — Toolformer, ToolBench 등
   - **Memory**: 과거 관찰·경험 저장·검색 — Generative Agents, Voyager, Dilu 등
   - 각 모듈에 표준화된 IO 인터페이스 정의 → 모듈 간 자유로운 교체·조합 가능
   - 16개 기존 에이전트에서 추출한 모듈로 초기 풀 구성 → 1,050개 가능 조합

2. **Module Evolution (모듈 진화)**
   - 진화 메타 프롬프트로 LLM이 기존 모듈을 코드 수준에서 수정하여 새 모듈 생성
   - 실행 오류 발생 시 피드백 기반 자동 수정
   - 새 모듈은 모듈 풀에 추가되어 향후 탐색에 활용

3. **Module Recombination (모듈 재결합)**
   - LLM이 경험 풀(이전 에이전트 + 성능 기록)을 분석하여 유망한 모듈 조합 추론
   - 4개 모듈의 직교적 결합으로 새로운 에이전트 구성
   - 단순 프롬프트 재작성보다 넓은 탐색 공간 커버

4. **Performance Predictor (성능 예측기)**
   - In-context surrogate 모델: 경험 풀의 (에이전트 설명, 성능) 쌍을 컨텍스트로 제공
   - 새 에이전트의 예상 성능을 LLM이 예측 → 유망하지 않은 설계를 사전 필터링
   - 실제 평가 비용을 대폭 절감

5. **워크플로우**: 초기화(16개 에이전트 시드) → 반복적으로 진화·재결합 → 성능 예측으로 필터링 → 실제 평가 → 경험 풀 업데이트

---

## Key Contribution

1. **MoLAS 문제 정의**: Modularized LLM Agent Search라는 새로운 연구 문제를 정의하고, 4모듈(Planning/Reasoning/Tool Use/Memory) 표준 IO 인터페이스로 설계 공간 체계화.
2. **진화+재결합 이중 메커니즘**: 코드 수준 모듈 진화로 새 모듈 발견 + 경험 기반 재결합으로 최적 조합 탐색. 단독으로는 도달하기 어려운 해공간을 효과적으로 커버.
3. **In-context 성능 예측기**: LLM 기반 surrogate 모델로 평가 비용을 대폭 절감하면서 탐색 효율 유지.
4. **해석 가능한 설계 인사이트**: 발견된 에이전트의 모듈 구성에서 태스크 유형별 효과적인 아키텍처 패턴을 도출.

---

## Experiment & Results

**벤치마크 6개**: Webshop(웹), ALFWorld(체화), SciWorld(과학), M3ToolEval(도구), TravelPlanner(계획), TextCraft(게임)

**모델**: GPT-4o

**주요 결과 (인간 설계 대비 평균 +17.2%)**:
- Webshop: AgentSquare가 최고 수동 설계 대비 향상
- ALFWorld: 기존 최고(Voyager 기반) 대비 개선
- 6개 벤치마크 전체에서 알려진 최고 수동 설계를 일관되게 초과

**모듈별 분석**:
- 웹 태스크: Reasoning 모듈의 영향이 가장 큼
- 체화 태스크: Memory 모듈이 핵심 (환경 지식 축적)
- 도구 사용 태스크: Tool Use 모듈의 최적화가 결정적

**Ablation**:
- Module Evolution만: 기존 모듈 조합보다 향상, 하지만 재결합 없으면 탐색 범위 제한
- Module Recombination만: 기존 모듈의 최적 조합 발견, 하지만 새 모듈 발견 불가
- Evolution + Recombination: 가장 높은 성능 — 두 메커니즘이 상호 보완적
- Performance Predictor: 평가 비용 50% 이상 절감하면서 성능 유지

**해석 가능성**: AgentSquare가 발견한 최적 에이전트의 모듈 구성을 분석하여, 태스크별 어떤 모듈 조합이 효과적인지 설명 가능한 인사이트 생성.

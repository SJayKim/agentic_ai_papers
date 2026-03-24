# MemEvolve: Meta-Evolution of Agent Memory Systems

> **논문 정보**
> - 제목: MemEvolve: Meta-Evolution of Agent Memory Systems
> - 저자: Guibin Zhang, Haotian Ren 외 (OPPO AI Agent Team, LV-NUS lab)
> - 날짜: December 23, 2025 (arXiv:2512.18746v1)
> - 코드: https://github.com/bingreeky/MemEvolve

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 에이전트의 메모리 시스템은 수동으로 설계된 고정된 아키텍처(encode → store → retrieve → manage 파이프라인)를 사용한다. 에이전트가 경험을 쌓으면서 메모리 내용은 축적되지만, 메모리 아키텍처 자체는 변하지 않는다. 이로 인해 특정 태스크 도메인에 최적화된 메모리 설계를 찾지 못하는 근본적인 한계가 존재한다. 예를 들어 웹 브라우징에 최적화된 API 기반 메모리는 수학·과학 추론에 효과가 낮고, 자기 비평(self-critique) 기반 메모리는 코딩·도구 사용 시나리오에서 성능이 떨어진다. |
| **Motivation** | 최고 성능 인간 학습자는 단순히 정보를 축적하는 것이 아니라, 과목에 따라 학습 전략 자체를 바꾼다(문학은 암기, 수학은 풀이 템플릿 추상화). 현재 에이전트 메모리 시스템은 '능숙한(skillful) 학습자'를 모델링하지만, '적응하는(adaptive) 학습자'에는 도달하지 못한다. 실제 실험 결과, ExpeL은 GAIA·xBench·WebWalkerQA 모든 벤치마크에서 No-Memory 기준선보다 성능이 낮았고, Dynamic Cheatsheet는 WebWalkerQA에서는 +1.76% 향상되었지만 GAIA와 xBench에서는 성능이 오히려 하락하는 등, 기존 메모리 시스템이 태스크 전반에 걸쳐 일관된 향상을 제공하지 못함이 실증되었다. |
| **Method** | **이중 진화(Dual-Evolution) 프레임워크**를 제안한다. (1) **내부 루프(Inner Loop, Experience Evolution)**: 고정된 메모리 아키텍처 Ω 하에서 에이전트가 태스크를 수행하며 메모리 내용(경험)을 축적한다. 각 후보 메모리 시스템은 60개 궤적(신규 40개 + 이전 반복에서 재사용 20개)으로 평가되며, 성능(task success), API 비용(token consumption), 지연 시간(latency) 3차원 피드백 벡터를 생성한다. (2) **외부 루프(Outer Loop, Architectural Evolution)**: Meta-Evolver가 성능 요약을 바탕으로 **진단-설계(Diagnose-and-Design)** 방식으로 새로운 메모리 아키텍처를 생성한다. 선택 단계에서는 파레토 비지배 정렬(Pareto non-dominated sorting)로 후보를 순위화하여 상위 K개(K=1)를 부모로 선택하고, 각 부모마다 S=3개의 변형 자손을 생성한다. 전체 반복은 K_max=3회 수행된다. **메모리 설계 공간**은 네 가지 모듈로 분해된다: ♣Encode(경험→구조화 표현), ♦Store(영속 저장), ♥Retrieve(문맥 인식 회상), ♠Manage(통합·망각). 이 공간을 균일한 프로그래밍 인터페이스로 구현한 코드베이스인 **EvolveLab**을 통해 12개의 대표적인 메모리 시스템을 재구현하여 MemEvolve의 초기화 기반 및 공정한 비교 실험 환경으로 활용한다. |
| **Key Contribution** | ① **통합 코드베이스 EvolveLab**: encode/store/retrieve/manage 4개 컴포넌트를 기반으로 12개의 자기진화 메모리 시스템(Voyager, ExpeL, Generative, DILU, AWM, Mobile-E, Cheatsheet, SkillWeaver, G-Memory, Agent-KB, Memp, EvolveR)을 단일 추상 베이스 클래스(BaseMemoryProvider)로 통합 구현. ② **메타 진화 프레임워크**: 기존 연구가 메모리 내용만 진화시킨 것과 달리, MemEvolve는 에이전트의 경험 축적(1차 진화)과 메모리 아키텍처 자체(2차 진화)를 동시에 진화시키는 최초의 이중 진화 방식. ③ **Diagnose-and-Design 메타 진화 연산자**: 궤적 수준의 실행 증거를 기반으로 메모리 병목(retrieval failure, 비효율적 추상화, 저장 비효율)을 진단하고, 모듈화된 설계 공간 내에서 구조적으로 제약된 새로운 아키텍처를 설계. |
| **Experiment/Results** | **4개 벤치마크**: GAIA(165개 태스크, Level 1~3), WebWalkerQA(170개 샘플, 680개 실제 쿼리), xBench-DeepSearch(100개 태스크), TaskCraft(300개 쿼리 중 120개 메타진화에 사용). **주요 수치**: • SmolAgent+GPT-5-mini 기준: xBench pass@1이 51% → 57%로 +6% 향상, pass@3은 68.0%까지 상승. • Flash-Searcher+GPT-5-mini 기준: GAIA 69.09% → 73.33%, xBench 69.0% → 74.0%, WebWalkerQA 71.18% → 74.71%. **API 비용은 유지**: GAIA에서 No-Memory $0.086 vs MemEvolve $0.085로 비용 증가 없이 성능 향상 달성. **교차 태스크 일반화**: TaskCraft에서 진화된 메모리를 WebWalkerQA/xBench-DS에 그대로 전이했을 때 일관된 성능 향상(WebWalkerQA+SmolAgent: 58.82%→61.18%, xBench+Flash-Searcher: 69.0%→74.0%). **교차 LLM 일반화**: GPT-5-mini로 메타진화한 메모리를 Kimi K2에 적용 시 WebWalkerQA에서 **+17.06%** 향상, TaskCraft에서 +10.0% 향상. DeepSeek V3.2 적용 시 WebWalkerQA에서 69.41%→72.35%로 향상. **교차 프레임워크 일반화**: TaskCraft에서 진화된 메모리를 CK-Pro, OWL 등 이질적인 다중 에이전트 프레임워크에 전이 시 일관된 성능 향상. Flash-Searcher pass@3: GAIA 80.61% 달성, OWL Workforce·CK-Pro 등 강력한 다중 에이전트 시스템 능가. |
| **Limitation** | ① **저자 언급**: TaskCraft와 같은 특정 태스크 패밀리에서 진화된 메모리 시스템은, 환경·행동 공간·도구 집합이 근본적으로 다른 태스크 패밀리(예: 체화 행동 로봇 제어)로의 전이에는 한계가 있을 수 있다고 명시. ② **읽으면서 파악된 한계**: 메타 진화 자체에 GPT-5-mini와 같은 강력한 LLM을 사용해야 하며, 메타 진화 연산자 F(·)의 구현에 상당한 계산 비용(각 반복마다 60개 궤적 실행)이 소요될 가능성이 높음. ③ 현재 결과가 단일 에이전트 및 멀티에이전트 프레임워크 모두에서 평가되었지만, 메모리 진화의 수렴 안정성은 아직 충분히 검증되지 않음(Figure 5에서 초기 단계 높은 분산 확인). ④ 메타 진화 연산자가 LLM 기반이므로, 아키텍처 탐색이 LLM의 언어적 편향에 영향받을 수 있음. |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | Flash-Searcher+GPT-5-mini 기반으로 7개 메모리 시스템과 비교(Table 3). GAIA 성능: No-Memory 69.09%, Generative 66.67%, Voyager 69.70%, DILU 66.67%, ExpeL 66.06%, AWM 67.27%, Mobile-E 69.09%, Cheatsheet 68.48%, **MemEvolve 73.33%**. xBench: No-Memory 69.0%, Voyager 68.0%, AWM 71.0%, **MemEvolve 74.0%**. WebWalkerQA: No-Memory 71.18%, Voyager 73.53%, **MemEvolve 74.71%**. MemEvolve는 세 벤치마크 전반에 걸쳐 3.54%~5.0%의 일관된 향상을 달성한 유일한 방법. GAIA Level 1 기준 최고 성능: Flash-Searcher+MemEvolve pass@3에서 94.34% 달성. |
| **Ablation Study** | 명시적 Ablation Study 섹션은 없으나, 메타 진화 경로 분석(Section 5.4, Figure 6)을 통해 각 컴포넌트의 기여를 간접적으로 확인. AgentKB 스타일의 초기 메모리(인코딩·저장 동결)에서 출발하여 1차 진화에서 LLM 기반 메타-가드레일 검색을 추가한 "Meta Memory System"이 승자가 됨. 3차 진화에서는 텍스트 인사이트 외에 재사용 가능한 도구 추출 및 주기적 데이터베이스 유지 관리(Cerebra 시스템)를 추가로 학습. Lightweight 시스템(최소 few-shot 궤적 메모리에서 진화)은 태스크 단계별로 적응적 메모리 콘텐츠(계획 단계: 고수준 가이던스, 실행 단계: 세밀한 도구 사용 추천 + 작업 메모리)를 제공. |

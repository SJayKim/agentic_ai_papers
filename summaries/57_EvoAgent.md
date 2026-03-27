# EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms

> **논문 정보**: Siyu Yuan, Kaitao Song, Jiangjie Chen, Xu Tan, Dongsheng Li, Deqing Yang (Fudan University, Microsoft Research Asia)
> **arXiv**: 2406.14228 (2024.06)
> **코드**: https://evo-agent.github.io

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 다중 에이전트 시스템(MAS) 구축 시 에이전트 역할, 수, 상호작용 패턴을 수동으로 설계해야 하며, 새 태스크마다 재설계가 필요하다. AgentVerse, AutoAgents 등도 고정 파이프라인에 묶여 확장성과 유연성이 제한된다. |
| **Motivation** | 생물학적 진화가 환경 적응적 개체를 만들듯, 진화 알고리즘(돌연변이, 교차, 선택)으로 단일 에이전트에서 자동으로 MAS를 생성할 수 있다면, 어떤 기존 프레임워크(MetaGPT, AutoGen 등)에도 인간 재설계 없이 적용 가능하다. |
| **Limitation** | (1) 다수 에이전트 생성으로 토큰 비용 증가. (2) AgentVerse·AutoAgents 외 다른 MAS 프레임워크와의 광범위한 비교 미수행. (3) 생성된 에이전트 품질의 인간 평가 미실시. (4) 긴 궤적 태스크에서는 멀티 에이전트의 컨텍스트 부담으로 향상이 제한적. |

---

## Method

EvoAgent는 기존 에이전트 프레임워크를 초기 개체로 간주하고, 진화 연산자를 반복 적용하여 전문 에이전트 집단을 자동 생성하는 파이프라인이다.

1. **Initialization**: 기존 프레임워크(MetaGPT, AutoGen 등)를 초기 에이전트 A(0,0)로 설정. 진화 대상(역할, 스킬, 프롬프트)을 정의

2. **Crossover**: 부모 에이전트가 사용자 요청에 대한 결과를 생성. LLM이 부족한 스킬을 파악하고 새 자식 에이전트를 생성 (예: 여행 계획에서 숙박 정보 부족 → 숙박 전문 에이전트 생성)

3. **Mutation**: LLM이 자식 에이전트를 수정하여 부모와 뚜렷이 구별되면서도 태스크 해결 능력 유지. N개 부모로부터 N′(>N)개 자식 생성하여 다양성 확보

4. **Selection**: LLM 기반 Quality-Check 모듈이 후보를 평가 — 부모 특성 계승 여부, 차별화 정도를 검사하여 N개 우수 에이전트 선별. 중복 유형 폐기

5. **Results Update**: 선별된 자식 에이전트들이 후보 결과 생성 → LLM이 이전 결과와 통합하여 최종 결과 도출. T회 반복하여 에이전트 집단이 점진적으로 진화

- 기본 설정: EVOAGENT(1, 3) — 3회 이터레이션, 각 1개 신규 에이전트
- MetaGPT, AutoGen, Camel 등에 추가 설계 없이 바로 적용 가능

---

## Key Contribution

1. **진화적 MAS 자동 생성**: 수동 설계 없이 단일→다중 에이전트 자동 확장. 어떤 프레임워크에도 적용 가능
2. **진화 파이프라인 형식화**: Crossover → Mutation → Selection → Results Update의 체계적 프로세스
3. **광범위한 벤치마크 검증**: NLP, 멀티모달, 인터랙티브 과학, 실세계 계획 등 다양한 태스크에서 일관된 향상

---

## Experiment & Results

**NLP/멀티모달 (GPT-4)**:
- Logic Grid Puzzle: EVOAGENT **77.00%** vs AutoAgents 69.00% (+8.0%p), Direct 60.50% (+16.5%p)
- Trivia Creative Writing: EVOAGENT **84.40%** vs AutoAgents 82.00%
- Codenames Collaborative: EVOAGENT **84.53%** vs AutoAgents 83.56%
- LLaMA2-13B Logic: EVOAGENT **35.50%** vs AgentVerse 10.00%, AutoAgents 16.00%

**ScienceWorld (인터랙티브 과학)**:
- GPT-4: EVOAGENT **30.42** vs baseline 27.97 (+2.45)
- GPT-4 Short: **48.67** vs baseline 42.41 (+6.26)

**TravelPlanner (실세계 계획, GPT-4)**:
- Commonsense Macro: **31.4%** (Direct 27.5% 대비 +3.9%p)
- Hard Constraint Macro: **18.9%** (Direct 16.1% 대비 +2.8%p)
- Final Pass Rate: **7.2%** (Direct 2.2% 대비 +5.0%p)
- GPT-3.5: Final Pass Rate **1.1%** (Direct 0.0%)

**Ablation**:
- Quality-Check 적용 시 Hard Constraint 일관 향상 (N>1 설정에서 12.7%→15.2%)
- SPP는 약한 LLM에서 Logic 0.0% → EVOAGENT 35.50%

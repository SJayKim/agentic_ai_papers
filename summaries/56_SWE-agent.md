# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

> **논문 정보**: John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press (Princeton University)
> **arXiv**: 2405.15793 (2024.05)
> **코드**: https://github.com/SWE-agent/SWE-agent

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM이 실제 소프트웨어 엔지니어링 태스크(GitHub 이슈 해결)를 수행하려면 대규모 코드베이스를 탐색하고 수정해야 하지만, 기존 인터페이스는 LLM에 최적화되지 않아 효율적 상호작용이 불가능하다. |
| **Motivation** | HCI(인간-컴퓨터 상호작용)에서 좋은 인터페이스가 인간 생산성을 높이듯, ACI(에이전트-컴퓨터 인터페이스)를 잘 설계하면 LLM 에이전트의 소프트웨어 엔지니어링 능력을 크게 향상시킬 수 있다. |
| **Limitation** | 저자 언급: 복잡한 멀티파일 수정에서 여전히 한계. 독자 관점: 쉘 기반 인터페이스가 GUI 상호작용이 필요한 태스크에 부적합. |

---

## Method

1. **ACI(Agent-Computer Interface) 설계 원칙**: LLM이 코드베이스와 효율적으로 상호작용할 수 있도록 특화된 명령어 세트와 피드백 형식 설계
2. **쉘 기반 상호작용 환경**: 파일 탐색, 검색, 편집을 위한 커스텀 명령어 제공
3. **자율적 이슈 해결**: 에이전트가 이슈를 읽고 → 관련 코드를 찾고 → 패치를 생성하는 전 과정을 자율 수행

---

## Key Contribution

1. **ACI 개념 도입**: 에이전트-컴퓨터 상호작용을 위한 인터페이스 설계 원칙을 최초로 체계화
2. **SWE-bench에서 당시 SOTA**: 12.29% 해결률 (이후 후속 연구들의 기반)

---

## Experiment & Results

- **벤치마크**: SWE-bench (2,294개 실제 GitHub 이슈)
- SWE-agent: 12.29% 해결률 (당시 SOTA)
- 좋은 ACI 설계가 기본 프롬프팅 대비 큰 성능 차이를 만듦을 실증

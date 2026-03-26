# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

> **논문 정보**: Sirui Hong, Mingchen Zhuge, Jiaqi Chen 외 (DeepWisdom, KAUST, FoundationAgents)
> **arXiv**: 2308.00352 (2023.08)
> **코드**: https://github.com/geekan/MetaGPT

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 기반 다중 에이전트 시스템은 에이전트 간 대화가 비구조적이어서 환각이 연쇄적으로 전파되고(cascading hallucinations), 복잡한 태스크에서 논리적 불일치가 발생한다. |
| **Motivation** | 인간 팀은 SOP(표준 운영 절차)를 통해 역할을 정의하고 산출물 형식을 표준화하여 협업 오류를 줄인다. LLM 에이전트에도 SOP를 도입하면 환각 전파를 억제하고 구조화된 협업이 가능. |
| **Limitation** | 저자 언급: SOP가 소프트웨어 개발에 특화되어 다른 도메인으로의 확장 시 재설계 필요. 독자 관점: 역할 간 구조화된 산출물이 과도한 오버헤드를 유발할 수 있음. |

---

## Method

1. **SOP 기반 역할 할당**: Product Manager, Architect, Engineer, QA 등 인간 팀의 역할을 에이전트에 할당
2. **구조화된 산출물**: PRD(요구사항 문서), 설계 문서, 플로우차트, 인터페이스 스펙 등 중간 산출물의 형식을 표준화
3. **어셈블리 라인 패러다임**: 각 에이전트가 순서대로 구조화된 산출물을 생성하고, 다음 에이전트가 이를 검증·활용
4. **실행 피드백 메커니즘**: 생성된 코드를 런타임에 디버그·실행하여 품질 향상

---

## Key Contribution

1. **SOP의 LLM MAS 도입**: 인간의 표준 운영 절차를 에이전트 협업에 적용한 선구적 프레임워크
2. **구조화된 산출물로 환각 억제**: 비구조적 대화 대신 형식화된 문서 전달로 연쇄 환각 방지
3. **HumanEval 85.9%, MBPP 87.7% Pass@1** 달성 (당시 SOTA)

---

## Experiment & Results

- **벤치마크**: HumanEval, MBPP, 복잡 소프트웨어 프로젝트
- HumanEval Pass@1: 85.9%, MBPP: 87.7% (당시 SOTA)
- 소프트웨어 프로젝트: 100% 태스크 완료율
- AutoGPT, LangChain, ChatDev 대비 더 높은 수준의 소프트웨어 복잡성 처리

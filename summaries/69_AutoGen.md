# AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

> **논문 정보**: Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu 외 (Microsoft Research)
> **arXiv**: 2308.08155 (2023.08)
> **코드**: https://github.com/microsoft/autogen

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 다중 에이전트 애플리케이션 구축이 복잡하고, 에이전트 간 대화 패턴을 유연하게 정의하고 관리하는 프레임워크가 부재하다. |
| **Motivation** | 다중 에이전트 대화를 통해 복잡한 태스크를 해결하는 것이 효과적임이 입증되었지만, 이를 구현하는 프레임워크가 표준화되지 않았다. 커스터마이즈 가능한 대화형 에이전트 프레임워크가 필요. |
| **Limitation** | 저자 언급: 복잡한 에이전트 간 상호작용의 디버깅 어려움. 독자 관점: 수동 워크플로우 정의가 여전히 필요하며, 자동 최적화 미지원. |

---

## Method

1. **커스터마이즈 가능한 대화형 에이전트**: 각 에이전트의 역할, 도구, LLM 설정을 유연하게 정의
2. **유연한 대화 패턴**: 자연어와 코드를 결합한 에이전트 간 통신. 1:1, 그룹, 순차, 중첩 대화 지원
3. **인간 참여 지원**: Human-in-the-loop을 대화 흐름에 자연스럽게 통합
4. **코드 실행 통합**: 에이전트가 코드를 생성하고 자동 실행하여 결과를 활용

---

## Key Contribution

1. **가장 널리 배포된 멀티 에이전트 프레임워크**: 학계와 산업에서 사실상 표준으로 자리잡음
2. **유연한 대화 패턴 추상화**: 다양한 에이전트 상호작용 유형을 통합적으로 지원

---

## Experiment & Results

- **학회**: COLM 2024 (Microsoft Research)
- 수학, 코딩, 의사결정, 검색 등 다양한 태스크에서 단일 에이전트 대비 일관된 성능 향상
- 오픈소스 프로젝트로 50K+ GitHub stars, 활발한 커뮤니티

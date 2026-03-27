# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

> **논문 정보**: Sirui Hong, Mingchen Zhuge, Jiaqi Chen 외 (DeepWisdom, KAUST, FoundationAgents)
> **arXiv**: 2308.00352 (2023.08) | **학회**: ICLR 2024
> **코드**: https://github.com/geekan/MetaGPT

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 다중 에이전트 시스템은 비구조적 자연어 대화로만 통신하여 환각이 연쇄 전파(cascading hallucinations)되고 복잡한 태스크에서 논리적 불일치가 빈번하다. |
| **Motivation** | 인간 팀의 SOP(표준 운영 절차)를 LLM 에이전트에 도입하면, 역할별 구조화된 산출물로 통신을 제한하여 환각 전파를 억제하고 체계적 협업이 가능하다. |
| **Limitation** | SOP가 소프트웨어 개발에 특화되어 다른 도메인 확장 시 재설계 필요. 역할 증가 시 토큰 비용 ~51% 증가. 순차적 구조가 병렬 처리에 비효율적. 비코딩 도메인 평가 부족. |

---

## Method

### 1. SOP 기반 역할 특화
- Product Manager, Architect, Project Manager, Engineer, QA Engineer 5가지 역할
- 각 에이전트는 이름·프로필·목표·제약 조건 명세, 역할별 도구 사용
- ReAct 스타일 행동 루프

### 2. 구조화된 통신 프로토콜
- 역할별 스키마 기반 구조화된 산출물로 통신 (PRD, 시스템 설계, 인터페이스 스펙, 코드, 테스트)
- **공유 메시지 풀(Publish-Subscribe)**: 모든 에이전트가 구조화된 메시지를 게시, 역할 기반으로 관련 메시지만 구독
- 불필요한 1:1 통신 제거, 선행 의존성 수신 후에만 액션 활성화

### 3. 실행 가능한 피드백 메커니즘
- 코드 생성 후 실제 런타임 실행으로 오류 감지
- 메모리의 과거 메시지(PRD, 설계, 코드) 참조하여 디버깅
- 유닛 테스트 통과까지 반복

---

## Key Contribution

1. **SOP의 LLM MAS 통합**: 표준 운영 절차를 프롬프트로 인코딩한 선구적 메타프로그래밍 프레임워크
2. **구조화된 통신으로 환각 전파 억제**: 역할별 스키마 기반 문서로 연쇄 환각 방지
3. **Publish-Subscribe 메시지 풀**: 역할 관련 정보만 선택적 수신
4. **런타임 실행 피드백**: HumanEval +4.2%, MBPP +5.4% 향상
5. **HumanEval 85.9%, MBPP 87.7% Pass@1** (ICLR 2024 당시 SOTA)

---

## Experiment & Results

- **벤치마크**: HumanEval (164개), MBPP (427개), SoftwareDev (70개, 7개 대표 비교)

**코드 생성**:
- **HumanEval Pass@1: 85.9%** (GPT-4 단독 67.0% 대비 +18.9%p)
- **MBPP Pass@1: 87.7%** (Codex+CodeT 67.7% 대비 +20.0%p)
- w/o feedback: HumanEval 81.7%, MBPP 82.3% → 피드백으로 +4.2%, +5.4% 향상

**SoftwareDev**:
- Executability: MetaGPT **3.75** vs ChatDev 2.25 (4점 만점)
- 코드 생산성: MetaGPT **124.3** tokens/line vs ChatDev 248.9 (절반)
- 코드 규모: MetaGPT **251.4** lines vs ChatDev 77.5 (3.2배 복잡)
- Human Revision: MetaGPT **0.83회** vs ChatDev 2.5회 (67% 감소)

**Ablation**: Engineer만 → Executability 1.0, Revisions 10회 / 4-에이전트 → Executability 4.0, Revisions 2.5회

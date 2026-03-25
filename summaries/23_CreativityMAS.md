# Creativity in LLM-based Multi-Agent Systems: A Survey

> **논문 정보**: Yi-Cheng Lin, Kang-Chieh Chen, Zhe-Yan Li, Tzu-Heng Wu, Tzu-Hsuan Wu, Kuan-Yu Chen, Hung-yi Lee, Yun-Nung Chen (National Taiwan University)
> **arXiv**: 2505.21116 (2025.05)
> **코드**: https://github.com/MiuLab/MultiAgent-Survey

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 MAS 서베이들이 인프라와 협업 메커니즘에 집중하면서, **창의성(creativity)** 차원 — 새로운 출력의 생성·평가, 창의적 페르소나 설계, 창의적 워크플로우 조율 — 을 간과하고 있다. |
| **Motivation** | 단일 에이전트는 익숙한 패턴에 수렴하여 개방형 창의 공간을 탐색하기 어렵다. MAS는 비평 루프, 경쟁적 인센티브, 연합 형성 등 다양한 역학을 통해 설계자가 예상하지 못한 창발적 창의적 결과를 만들어낼 수 있다. 이 분야를 체계화하는 최초의 서베이가 필요하다. |
| **Limitation** | (1) 텍스트와 이미지 생성에 초점을 맞추어, 음악·비디오·3D 등 다른 모달리티는 미포함. (2) 창의성 평가 표준이 통일되지 않아 연구 간 비교가 어려움. (3) 편향 완화, 조율 갈등 등의 문제가 지적되었으나 해결책은 제한적. |

---

## Method

이 서베이는 MAS에서의 창의성을 **에이전트 주체성(Proactivity)**, **생성 기법**, **평가 방법**의 3축으로 분류한다.

1. **MAS 워크플로우와 주체성 스펙트럼**
   - 창의적 워크플로우를 Planning → Process → Decision Making 3단계로 분해
   - 각 단계에서 에이전트의 주체성(initiative + control)을 반응적(reactive) ↔ 능동적(proactive) 연속체로 위치
   - 높은 주체성: 에이전트가 자율적으로 서브골 설정·태스크 분배·자기 평가
   - 낮은 주체성: 인간이 매 단계 지시, 에이전트는 실행만

2. **페르소나 설계**
   - 역할 기반: Writer, Editor, Actor 등 특화된 역할 할당
   - 개인화: 특정 문화·배경·관점을 반영한 페르소나로 다양성 확보
   - 동적 페르소나: 상호작용 중 페르소나가 진화

3. **생성 기법**
   - **Divergent Exploration**: 각 에이전트가 독립적으로 다른 방향 탐색 → 아이디어 공간 확장
   - **Iterative Refinement**: 비평-수정 루프를 통한 점진적 품질 향상
   - **Collaborative Synthesis**: 여러 에이전트의 기여를 통합하여 최종 산출물 생성

4. **평가 방법**
   - 주관적 평가: 인간 판단 (novelty, usefulness, surprise)
   - 객관적 평가: 자동 메트릭 (다양성, 새로움, 유용성 점수)
   - 관련 데이터셋과 벤치마크 정리

---

## Key Contribution

1. **MAS 창의성 최초 전용 서베이**: 기존 MAS 서베이가 간과한 창의성 차원을 전문적으로 다루는 최초의 연구.
2. **주체성 스펙트럼 프레임워크**: 에이전트의 주체성을 Planning/Process/Decision Making 각 단계별로 연속체로 분석.
3. **주요 도전과제 식별**: 일관되지 않은 평가 표준, 불충분한 편향 완화, 조율 갈등, 통합 벤치마크 부재 등 핵심 문제를 식별하고 로드맵 제시.

---

## Experiment & Results

서베이 논문으로서 문헌 분석 중심:
- **분석 범위**: 텍스트·이미지 생성에서의 MAS 창의성 관련 연구들을 체계적으로 분류
- **주요 발견**: (1) 대부분의 MAS가 Planning에서 낮은 주체성(인간 의존), Process에서 높은 주체성 경향. (2) 과도한 AI 주도 제안이 아이디어 공간을 축소시킬 수 있음 (Collaborative Canvas 연구). (3) 에이전트 주체성 증가가 아이디어 양은 늘리나 사용자 만족·신뢰는 감소 (Co-Quest 연구).

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Taxonomy/분류 체계** | **3축**: (1) 워크플로우 단계별 주체성 스펙트럼 (Planning/Process/Decision Making × Reactive↔Proactive), (2) 생성 기법 (Divergent Exploration/Iterative Refinement/Collaborative Synthesis), (3) 평가 (주관적/객관적 메트릭 + 데이터셋) |

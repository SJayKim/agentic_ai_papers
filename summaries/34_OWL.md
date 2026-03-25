# OWL: Optimized Workforce Learning for General Multi-Agent Assistance in Real-World Task Automation

> **논문 정보**: Mengkang Hu, Yuhang Zhou, Wendong Fan, Yuzhou Nie 외 (HKU, CAMEL-AI.org, Eigent.AI, UCSB, KAUST)
> **arXiv**: 2505.23885 (2025.05)
> **코드**: https://github.com/camel-ai/owl

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 현존 다중 에이전트 시스템은 도메인 특화 설계에 의존하여, 새 도메인 적용 시 (1) 추론 측면에서 전체 아키텍처 재설계가 필요하고, (2) 학습 측면에서 모든 컴포넌트의 재학습이 필요하여 교차 도메인 전이가 극도로 제한된다. |
| **Motivation** | MetaGPT의 SOP는 소프트웨어 공학에 특화되어 다른 분야 확장이 어렵고, MALT는 Generator-Verifier-Refiner 파이프라인 전체를 재학습해야 한다. 범용 AI 어시스턴트를 위해서는 전략 계획(도메인 무관)과 실행(도메인 특화)을 분리하는 모듈형 아키텍처가 필요하다. |
| **Limitation** | 저자 언급: GAIA 벤치마크에 특화된 평가로 다른 실세계 태스크 일반화 검증 부족. 독자 관점: Planner의 RL 학습이 수집한 태스크 분포에 의존하며, 학습 데이터에 없는 완전히 새로운 도메인으로의 제로샷 전이 성능 미검증. Worker 노드의 도구 구성이 수동적. |

---

## Method

1. **WORKFORCE: 계층적 다중 에이전트 추론 프레임워크**
   - **Planner Agent (도메인 무관)**: 고수준 목표를 분석하여 추상적 서브태스크로 분해. 도메인 지식 불필요
   - **Coordinator Agent**: 서브태스크를 적절한 Worker에 할당, 태스크 의존 관계 관리, 중간 결과 통합
   - **Worker Nodes (도메인 특화)**: 웹 에이전트, 문서 에이전트, 추론 에이전트 등 특화 도구를 갖춘 실행 에이전트. 도메인별 플러그앤플레이 교체/추가 가능

2. **Task Channel 기반 통신**
   - 공유 태스크 채널을 중앙 허브로 사용
   - Coordinator가 태스크를 게시하고 Worker가 최종 결과만 반환 — 실행 컨텍스트는 격리
   - 태스크 상태: OPEN → RUNNING → DONE

3. **OWL: 최적화된 인력 학습 (RL 기반 Planner 학습)**
   - **Stage 1 — SFT**: 커스텀 태스크 데이터셋에서 Planner 초기화
   - **Stage 2 — RL (GRPO)**: 실세계 피드백(태스크 성공/실패)으로 Planner 강화 학습
   - Planner만 학습하고 Worker는 학습하지 않음 → 최소 재학습으로 교차 도메인 전이
   - 보상 설계: 태스크 완료 정확도 기반

4. **모듈형 도메인 전이**: 새 도메인 적응 시 Worker 노드만 추가/교체, Planner와 Coordinator는 그대로 유지

---

## Key Contribution

1. **계획-실행 분리 아키텍처**: 도메인 무관 Planner + 도메인 특화 Worker의 모듈형 설계로, 추론과 학습 모두에서 교차 도메인 전이를 가능하게 함
2. **OWL RL 학습**: Planner만 강화 학습하는 효율적 패러다임으로 Qwen2.5-32B가 +16.37% 향상, GPT-4o 수준 달성
3. **오픈소스 SOTA**: GAIA 벤치마크에서 69.70%로 OpenAI Deep Research(55.15%)를 14.55%p 초과하는 오픈소스 최고 성능

---

## Experiment & Results

- **벤치마크**: GAIA (범용 AI 어시스턴트 평가, 다중 도메인, 멀티모달)
- **비교 대상**: OpenAI Deep Research, HuggingFace Open Deep Research, GPT-4o-mini, Qwen2.5-72B

**WORKFORCE 추론 성능**:
- GAIA 전체: **69.70%** (Level 1: 78.7%, Level 2: 71.7%, Level 3: 42.3%)
- OpenAI Deep Research: 55.15%, 이전 오픈소스 SOTA: 67.4%
- Level 3(가장 어려운 태스크)에서 42.3%로 OpenAI 30.8% 대비 +11.5%p

**OWL 학습 효과 (Qwen2.5-32B)**:
- 학습 전: 36.36% → OWL 학습 후: **52.73%** (+16.37%p)
- GPT-4o-mini (47.27%) 초과, Qwen2.5-72B (49.09%) 수준 달성
- Level 2: 51.16% (학습 전 19.23%), Level 3: 19.23% (학습 전 동일 — 난이도 한계)

**도메인 전이**: GAIA 데이터 미사용으로 학습 후에도 다양한 도메인에서 일반화 확인

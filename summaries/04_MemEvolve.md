# MemEvolve: Meta-Evolution of Agent Memory Systems

> **논문 정보**: OPPO AI Agent Team, LV-NUS lab (Guibin Zhang 등)
> **arXiv**: 2512.18746 (2025.12)
> **코드**: https://github.com/bingreeky/MemEvolve

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 자기진화(self-evolving) 메모리 시스템은 에이전트의 경험 축적은 지원하지만, 메모리 아키텍처 자체는 사전에 수동 설계되어 고정된다. 메모리가 에이전트 진화를 촉진하더라도, 메모리 구조 자체는 다양한 태스크 컨텍스트에 메타 적응하지 못한다. |
| **Motivation** | 인간 학습자 비유로, "mediocre learner"(경험 활용 못함) → "skillful learner"(고정 방식으로 경험 추출) → "adaptive learner"(학습 전략 자체를 동적 조정)로의 진화가 필요. 수학은 풀이 템플릿을, 문학은 암기를 우선하듯, 태스크에 따라 메모리 구조가 달라야 한다. 단일 고정 메모리 아키텍처로는 이 다양성을 커버할 수 없다. |
| **Limitation** | (1) 외부 루프 진화에 LLM 기반 코드 생성이 필요하므로 메타 진화 비용이 상당하다. (2) 현재 3회 반복으로 제한된 outer loop에서 수렴 보장이 불확실하다. (3) EvolveLab의 12개 메모리 시스템이 설계 공간의 초기화를 결정하므로, 커버되지 않는 참신한 패러다임은 발견이 어려울 수 있다. (4) 벤치마크가 주로 웹 검색·심층 연구 태스크에 집중되어, 다른 도메인(로보틱스 등)으로의 일반화는 미검증. |

---

## Method

MemEvolve는 에이전트의 경험(내부 루프)과 메모리 아키텍처(외부 루프)를 **동시에 진화**시키는 이중 최적화 프레임워크다.

1. **EvolveLab: 통합 코드베이스**
   - 12개 대표 메모리 시스템(Voyager, ExpeL, AWM, SkillWeaver, G-Memory 등)을 4개 모듈 설계 공간으로 통일: **Encode**(경험 인식/포맷), **Store**(정보 커밋), **Retrieve**(문맥 기반 회상), **Manage**(통합/망각)
   - `BaseMemoryProvider` 추상 클래스를 통해 모든 메모리 아키텍처가 동일 인터페이스 상속
   - Online/Offline 평가 모드 지원

2. **Inner Loop (경험 진화, 1차)**
   - 고정된 메모리 시스템 Ω(k)_j 하에서, 에이전트가 태스크 스트림을 처리하며 메모리 상태 M(k)를 업데이트
   - 각 후보 아키텍처의 성능을 태스크 성공률·토큰 비용·지연시간의 3차원 벡터 F(k)_j로 집계

3. **Outer Loop (아키텍처 진화, 2차)**
   - **Architectural Selection**: 후보 아키텍처를 F(k)_j 기반 비지배 정렬(Pareto ranking)로 순위화, 성능 우선으로 상위 K개 선택
   - **Diagnose-and-Design (D&D) Evolution**:
     - **Diagnosis**: 선택된 부모 아키텍처의 trajectory를 분석하여 구조적 결함 프로파일 D(Ω) 생성 (검색 실패, 비효율적 추상화, 저장 비효율 등)
     - **Design**: 결함 프로파일에 기반하여 4개 모듈의 구현을 수정/재조합하여 S개 변이 아키텍처 생성
   - K=1 생존, S=3 자손, 3회 반복

4. **이중 진화 순환**
   - 매 반복: 빈 메모리에서 시작 → 내부 루프로 경험 축적 → 외부 루프로 아키텍처 갱신
   - 향상된 아키텍처 → 더 나은 학습 효율 → 더 높은 품질 trajectory → 더 정밀한 적합도 신호의 선순환

---

## Key Contribution

1. **메타 진화 프레임워크**: 에이전트 경험과 메모리 아키텍처를 동시에 진화시키는 최초의 bilevel 최적화 프레임워크. 기존의 고정 아키텍처 + 경험 축적 패러다임을 근본적으로 확장.
2. **EvolveLab 통합 코드베이스**: 12개 대표 메모리 시스템을 4모듈 설계 공간(Encode/Store/Retrieve/Manage)으로 통일하여 공정한 비교와 모듈 수준 진화를 가능하게 함.
3. **Diagnose-and-Design 진화 연산**: trajectory 분석 기반 구조적 결함 진단 후 타겟팅된 아키텍처 수정으로, 무작위 탐색 대비 효율적 진화.
4. **교차 일반화**: 발견된 메모리 아키텍처가 다른 벤치마크와 다른 LLM 백본에도 효과적으로 전이됨을 실증.

---

## Experiment & Results

**벤치마크**: WebWalkerQA, xBench-DS, TaskCraft, GAIA (Level 1/2/3)

**프레임워크**: SmolAgent(경량 2-에이전트) + Flash-Searcher(고성능 단일 에이전트) 위에 MemEvolve 통합

**주요 결과 (Flash-Searcher + GPT-5-mini, pass@3)**:
- MemEvolve: WebWalkerQA **81.18%**, xBench-DS **78.0%**, TaskCraft **79.33%**, GAIA **80.61%**
- Flash-Searcher 단독 (pass@1): 71.18%, 69.0%, 69.67%, 69.09%
- Agent KB (pass@3): 73.53%, 68.0%, 75.33%, 73.94%

**SmolAgent 위 개선**: SmolAgent 기존 55.75% (GAIA) → MemEvolve 적용 후 최대 +17.06% 향상

**교차 LLM 일반화**: GPT-5-mini에서 발견된 아키텍처를 Kimi K2 (69.41%), DeepSeek V3.2 (72.35%)에 전이 시에도 Flash-Searcher 단독 대비 향상

**Ablation (Table 3)**: 메모리 없음 < 기존 수동 설계 < MemEvolve. Encode·Store·Retrieve·Manage 각 모듈이 진화 과정에서 태스크에 맞게 특화됨을 확인 (Figure 3 시각화).

**비용**: 메모리 진화 3회 반복이 추가 비용을 발생시키나, 발견된 아키텍처의 재사용으로 장기적 효율성 확보.

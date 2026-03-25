# Preference-Aware Memory Update for Long-Term LLM Agents

> **논문 정보**: Haoran Sun, Zekun Zhang, Shaoning Zeng
> **arXiv**: 2025.10
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 메모리 시스템은 저장·검색·조직에 집중하면서, 메모리 업데이트 메커니즘이 부족하다. 특히 사용자 선호도가 시간에 따라 변화하는 상황을 감지하고 메모리에 반영하는 동적 업데이트가 결여되어 있다. |
| **Motivation** | 실제 장기 대화에서 사용자의 어조 선호, 응답 길이, 감정 톤, 정보 밀도, 격식 수준 등이 점진적으로 또는 갑작스럽게 변화한다. 이러한 선호 변화를 추적하지 못하면 에이전트의 응답이 사용자 의도와 괴리되어 장기 개인화가 실패한다. |
| **Limitation** | (1) LoCoMo 데이터셋에서만 검증되어 다른 장기 대화 시나리오에 대한 일반화가 미확인. (2) 선호 차원이 5개(어조, 길이, 감정, 밀도, 격식)로 고정되어, 더 세밀하거나 도메인 특화된 선호를 커버하지 못한다. (3) 소형 모델(Qwen 2.5 1.5B/3B, LLaMA 3.2 1B/3B)에서만 실험되어, 대형 모델에서의 효과는 미검증. (4) 독립 메모리 시스템이 아닌 기존 방법의 플러그인으로만 평가되어, 독립적 기여도 분리가 어렵다. |

---

## Method

PAMU(Preference-Aware Memory Update)는 다차원 사용자 선호를 실시간으로 추적하고, 이를 프롬프트에 반영하여 개인화된 응답을 생성하는 메커니즘이다.

1. **Preference Extractor (선호 추출기)**
   - 매 대화 턴마다 5차원 선호 벡터 `P = {p_1, ..., p_D}` 추출
   - **어조 스타일**: RoBERTa 인코더 + 다중 클래스 분류 헤드 → 카테고리 확률 분포
   - **응답 길이**: 최근 K턴의 평균 토큰 수, [0,1]로 정규화
   - **감정 톤**: 감정 분류 모델로 주요 감정 카테고리와 확률 추출
   - **정보 밀도**: 이전 응답의 트리플/토큰 비율로 측정
   - **격식 수준**: 격식 탐지 모델로 [0,1] 점수 추출

2. **Preference Change Perception (선호 변화 감지)**
   - **Sliding Window (SW)**: 최근 W턴의 선호 평균 — 단기 변동 포착
   - **Exponential Moving Average (EMA)**: `EMA_t = β·EMA_{t-1} + (1-β)·p_t` — 장기 추세 포착
   - **융합**: `w_t = λ·SW_t + (1-λ)·EMA_t` — 단기·장기 추정의 최적 가중 결합 (최소 분산 추정, Kalman 필터와의 수학적 대응 제시)
   - **변화 감지 신호**: `Δ = SW - EMA`, 정규화된 변화 점수 `C_t` > δ 시 프롬프트 재작성 트리거

3. **Preference-Guided Prompting**
   - 융합된 선호 벡터 `w_t`를 자연어 지시로 변환
   - 예: "Please answer in the style of: [Tone: humorous], [Emotion: relaxed], [Density: moderate], [Length: brief]"
   - 연속 차원은 의미 태그로 이산화 (예: 밀도 0~0.33 → "Sparse", 0.33~0.66 → "Moderate")
   - 모델 아키텍처 수정 없이 순수 프롬프트 엔지니어링으로 구현 — 모델 불가지론적

---

## Key Contribution

1. **동적 선호 추적**: SW와 EMA를 결합한 이중 시간 스케일 선호 모델링. 점진적 드리프트와 급격한 변화 모두 감지 가능.
2. **수학적 정당성**: 최소 분산 추정 이론과 Kalman 필터 근사로 SW-EMA 융합의 이론적 최적성 제시.
3. **플러그인 호환성**: 기존 메모리 시스템(ReadAgent, MemoryBank, MemGPT, A-MEM)에 독립적으로 추가 가능한 모듈형 설계.
4. **소형 모델 효과**: Qwen 2.5-1.5B/3B, LLaMA 3.2-1B/3B 등 소형 모델에서 유의미한 개선, 자원 제약 환경에서의 실용성 확보.

---

## Experiment & Results

**데이터셋**: LoCoMo — 50개 대화, 평균 300턴, 최대 35세션, 9K 토큰. Single-Hop(2,705), Multi-Hop(1,104), Temporal(1,547) 3개 카테고리.

**비교 방식**: 4개 베이스라인(ReadAgent/RA, MemoryBank/MB, MemGPT/MG, A-MEM/AM)에 PAMU를 플러그인으로 추가하여 전후 비교.

**Single-Hop (Qwen 2.5-1.5B, F1/BLEU-1)**:
- A-MEM: 17.24/11.35 → PAMU 적용: **17.93/15.73*** (+38.6% BLEU-1)
- MemGPT: 10.43/7.54 → PAMU 적용: **10.49/11.46*** (+52.0% BLEU-1)
- 모든 베이스라인에서 BLEU-1 유의미 향상 (p<0.05)

**Multi-Hop (LLaMA 3.2-3B, F1/BLEU-1)**:
- A-MEM: 19.35/13.27 → PAMU 적용: **20.14/23.14*** (+74.4% BLEU-1)
- MemGPT: 3.02/2.95 → PAMU 적용: **3.02/6.34*** (+114.9% BLEU-1)

**Temporal (LLaMA 7B, F1/BLEU-1)**:
- ReadAgent: 12.24/11.17 → PAMU 적용: **15.45*/15.67*** — F1과 BLEU-1 모두 유의미 향상
- Temporal 태스크에서 가장 큰 개선 → 시간적 선호 변화 감지가 특히 효과적

**전반적 패턴**: PAMU가 응답 품질(BLEU-1)에서 특히 큰 개선을 보여, 선호 정렬이 표면적 유창성에 직접 기여함을 시사.

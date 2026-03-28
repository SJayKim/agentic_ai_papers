# Preference-Aware Memory Update for Long-Term LLM Agents

> **논문 정보**: Haoran Sun, Zekun Zhang, Shaoning Zeng
> **arXiv**: 추정 2025 | **학회**: -
> **코드**: 미공개

---

## Problem

LLM 기반 에이전트의 장기 대화에서 사용자 선호(preference)는 시간에 따라 지속적으로 변화하지만, 기존 메모리 시스템은 저장(storage)과 검색(retrieval)에만 초점을 맞추고 있어 이러한 변화를 반영하지 못한다. MemoryBank, MemGPT, A-MEM 등 주요 메모리 프레임워크들은 사용자 행동이 정적(stationary)이거나 시간에 걸쳐 균일하게 분포한다는 가정에 의존한다. 이 정적 가정 하에서는 에이전트가 오래된(outdated) 선호 정보에 기반해 응답을 생성하게 되어, 대화 일관성과 사용자 만족도가 저하된다. 실제 배포 환경에서 사용자의 의도, 선호, 목표는 과업 맥락, 감정 상태, 상호작용 단계 등의 요인에 따라 점진적 변화 또는 급격한 전환을 겪는다. 동적 메모리 업데이트 메커니즘이 없으면 에이전트는 사용자와 정렬되지 않은(misaligned) 응답을 생성하게 되며, 이는 사용자 신뢰도 하락으로 이어진다.

---

## Motivation

인간의 대화 행동은 본질적으로 비정상적(non-stationary)이며, 톤 스타일·감정 상태·정보 밀도·형식성 등 다차원적 선호가 대화 진행에 따라 동적으로 변화한다. 시계열 모델링에서 Sliding Window Average(SW)는 단기 변동에 민감하고, Exponential Moving Average(EMA)는 장기 추세를 안정적으로 추적하는 상보적 특성을 갖는다. 이 두 기법을 결합하면 단기 선호 변화와 장기 사용자 경향을 동시에 포착하는 융합 표현(fused representation)을 구축할 수 있다. 또한 SW와 EMA 간의 괴리(divergence)를 변화 감지 신호로 활용하면, 사용자 선호의 급변 시점을 해석 가능하게(interpretable) 탐지할 수 있다. 이러한 통찰에 기반하여, 모델 아키텍처나 디코더를 수정하지 않고 프롬프트 엔지니어링만으로 유연한 행동 제어를 달성하는 경량 메커니즘을 설계한다.

---

## Method

PAMU(Preference-Aware Memory Update) 메커니즘은 다음 단계로 구성된다:

1. **Preference Extractor**: 매 대화 턴마다 사용자 선호 벡터 P = {p₁, p₂, ..., p_D}를 5개 차원에서 추출한다.
   - **Tone Style**: RoBERTa 기반 다중 클래스 분류기가 사용자 발화의 스타일 확률 분포를 산출
   - **Response Length**: 과거 K턴의 평균 응답 길이를 [0, 1]로 정규화
   - **Emotional Tone**: 감정 분류 모델이 사용자·어시스턴트 발화에서 지배적 감정 카테고리를 식별
   - **Information Density**: OpenIE 모델로 (주어, 술어, 목적어) 트리플을 추출하고, ID_t = K_t / L_t (트리플 수 / 단어 수)로 정의
   - **Degree of Formality**: 사전학습된 형식성 분류기가 [0, 1] 정규화 점수를 산출

2. **Preference Change Perception Module**: 추출된 선호 벡터에 대해 단기·장기 동적 모델링을 수행한다.
   - **연속 차원** (길이, 밀도, 형식성): 길이 W의 Sliding Window Average와 EMA를 각각 계산
   - **범주 차원** (톤, 감정): 카테고리 확률 분포에 대해 동일한 SW/EMA 연산을 적용하고, argmax로 현재 생성 제어 레이블을 선택
   - **융합**: ŵ_t = λ · SW_t + (1-λ) · EMA_t로 단기·장기 추정치를 결합

3. **Change Detection Signal**: SW와 EMA 간 편차 Δ_t를 계산하고, 정규화된 탐지 점수가 임계값 δ를 초과하면 프롬프트 재작성 또는 메모리 재구조화를 트리거한다.

4. **Preference-Guided Prompting**: 융합된 선호 벡터를 자연어 지시문으로 변환한다 (예: "[Tone: humorous], [Emotion: relaxed], [Information density: moderate], [Length: brief]"). 연속 차원은 구간별로 이산화하여 의미 태그로 매핑.

5. **프롬프트 주입**: 최종 선호 프롬프트를 각 베이스라인 메모리 시스템의 원본 입력 프롬프트에 append하여, 모델 아키텍처 수정 없이 응답 생성을 제어한다. ReadAgent, MemoryBank, MemGPT, A-MEM 등 다양한 프레임워크에 플러그인 방식으로 통합 가능하다.

---

## Key Contribution

1. **최초의 Preference-Aware Memory Update 메커니즘(PAMU)**: 사용자 선호의 시간적 변화를 실시간으로 추적·갱신하여, 기존 메모리 시스템의 정적 가정 한계를 극복.
2. **SW+EMA 융합 프레임워크**: 단기 변동과 장기 경향을 동시에 포착하는 이론적으로 정당화된(MVUE, Kalman 필터 근사) 프레임워크를 설계.
3. **경량·모듈식 접근**: 모델 아키텍처·디코더 수정 없이 프롬프트 엔지니어링만으로 선호 정렬을 달성, 기존 메모리 프레임워크에 플러그인 방식으로 통합 가능.
4. **해석 가능한 변화 감지 신호**: SW-EMA 간 divergence 기반으로 선호 급변 시점의 자동 탐지 및 적응적 프롬프트 재작성을 지원.
5. **범용성 검증**: 5개 베이스라인 × 3개 태스크에서 일관된 성능 향상을 실증.

---

## Experiment & Results

**데이터셋**: LoCoMo — 50개 대화, 평균 300턴/대화, 최대 35세션, ~9,000 토큰/대화. Single-hop(2,705쌍), Multi-hop(1,104쌍), Temporal reasoning(1,547쌍) 3개 태스크. 평가 지표는 F1 Score와 BLEU-1.

**베이스라인**: ReadAgent(RA), MemoryBank(MB), MemGPT(MG), A-MEM(AM). 각 베이스라인의 원본 vs PAMU 적용(†) 전후를 비교.

**Single-hop (Qwen 2.5-3B)**: A-MEM†이 F1 **13.23** (기존 12.52), BLEU-1 **13.24** (기존 9.24)로 가장 큰 BLEU-1 향상폭 (+4.00). MemGPT†는 BLEU-1 **8.65** (기존 4.28)로 +4.37 포인트 개선.

**Multi-hop (LLaMA 3.2-3B)**: A-MEM†이 F1 **20.14** (기존 19.35), BLEU-1 **23.14** (기존 13.27)로 최고 성능. MemoryBank†는 BLEU-1 **7.65** (기존 3.02)로 +4.63 향상.

**Temporal Reasoning (LLaMA-7B)**: A-MEM†: F1 **23.23** (기존 17.55, +5.68), BLEU-1 **21.46** (기존 14.67, +6.79). MemGPT†: F1 **17.54** (기존 11.14, +6.40), BLEU-1 **15.57** (기존 8.24, +7.33). MemoryBank†: F1 **19.76** (기존 14.56, +5.20).

**Ablation Study (Temporal Reasoning, LLaMA-7B, F1+BLEU-1 평균)**: Full PAMU가 A-MEM에서 **22.35**로 최고. w/o SW → 15.36, w/o EMA → 14.05, Equal Fusion → 20.34, w/o Detection → 16.24, w/o Prompt → 15.45, Single Pref → 18.95, Static Pref → 19.47. SW와 EMA 모두 제거 시 약 30-37% 성능 하락.

**정성 평가**: GPT-4 자동 채점 + 10인 인간 평가자. PAMU 적용 시 Style Consistency **92/94%** (w/o PAMU: 37/35%), Preference Detection **97/95%** (w/o PAMU: 48/45%). 사용자 선호 정렬 점수 **4.8/4.5** vs w/o PAMU **2.1/2.2** (5점 만점).

---

## Limitation

- 선호 추출기가 RoBERTa, 감정 분류기, OpenIE 등 다수의 외부 모델에 의존하여, 추론 시 계산 오버헤드와 파이프라인 복잡도가 증가한다. 이들 모델의 오류가 선호 벡터에 전파될 수 있다.
- 선호 차원이 톤·길이·감정·밀도·형식성의 5가지로 사전 정의되어 있어, 도메인 특화 선호(예: 코드 스타일, 시각적 선호)나 새로운 선호 유형으로의 확장이 수동적 재설계를 요구한다.
- 평가가 LoCoMo 단일 데이터셋에서만 수행되었으며, 실제 배포 환경이나 다른 장기 대화 벤치마크에서의 일반화 가능성이 검증되지 않았다.
- 융합 가중치 λ, 윈도우 크기 W, EMA 감쇠 계수 β, 변화 탐지 임계값 δ 등 하이퍼파라미터 민감도 분석이 부재하여, 최적 설정에 대한 가이드라인이 없다.
- 프롬프트 주입 방식은 모델에 따라 선호 지시문 해석 능력이 다를 수 있으며, 소형 모델(1.5B-3B)에서 상대적으로 낮은 베이스라인 성능이 이 한계를 시사한다.
- 다중 사용자 환경에서의 선호 충돌 처리나 프라이버시 관련 고려가 논의되지 않았다.

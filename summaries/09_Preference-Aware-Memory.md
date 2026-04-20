# Preference-Aware Memory Update for Long-Term LLM Agents

> **논문 정보**: Haoran Sun, Zekun Zhang, Shaoning Zeng
> **arXiv**: 추정 2025 | **학회**: -
> **코드**: 미공개

---

## Problem

LLM 기반 에이전트의 장기 대화에서 사용자 선호(preference)는 시간에 따라 지속적으로 변화한다.
그러나 기존 메모리 시스템은 저장(storage)과 검색(retrieval)에만 초점을 맞추고 있어 이러한 변화를 반영하지 못한다.
MemoryBank, MemGPT, A-MEM, MemInsight 등 주요 메모리 프레임워크들은 사용자 행동이 정적(stationary)이거나 시간에 걸쳐 균일하게 분포한다는 가정에 의존한다.
이 정적 가정 하에서 에이전트는 오래된(outdated) 선호 정보에 기반해 응답을 생성하게 되어, 대화 일관성과 사용자 만족도가 저하된다.
실제 배포 환경에서 사용자의 의도·선호·목표는 과업 맥락, 감정 상태, 상호작용 단계 등의 요인에 따라 점진적 변화 또는 급격한 전환을 겪는다.
동적 메모리 업데이트 메커니즘이 없으면 에이전트는 사용자와 정렬되지 않은(misaligned) 응답을 생성하게 되며, 이는 사용자 신뢰도 하락으로 이어진다.
특히 기본 프롬프트 연결(concatenation) 접근법은 LLM의 유한한 컨텍스트 윈도우 제약 때문에 장기 상호작용에서 효과가 제한적이다.
결론적으로 선호의 시간적 진화를 추적·반영하여 장기 개인화(long-term personalization)를 지원하는 메커니즘이 부재하다는 것이 핵심 문제다.

---

## Motivation

인간의 대화 행동은 본질적으로 비정상적(non-stationary)이며, 톤 스타일·감정 상태·정보 밀도·형식성 등 다차원적 선호가 대화 진행에 따라 동적으로 변화한다.
시계열 모델링에서 Sliding Window Average(SW)는 단기 변동에 민감하고, Exponential Moving Average(EMA)는 장기 추세를 안정적으로 추적하는 상보적 특성을 갖는다.
이 두 기법을 결합하면 단기 선호 변화와 장기 사용자 경향을 동시에 포착하는 융합 표현(fused representation)을 구축할 수 있다.
또한 SW와 EMA 간의 괴리(divergence)를 변화 감지 신호로 활용하면, 사용자 선호의 급변 시점을 해석 가능하게(interpretable) 탐지할 수 있다.
이 융합 구조는 이론적으로 MVUE(Minimum Variance Unbiased Estimator) 및 단순화된 Kalman 필터 근사로 정당화되어, 불확실성 하의 최적성이 뒷받침된다.
미세조정(fine-tuning) 기반 암묵적 모델링은 catastrophic forgetting과 추론 시간 적응성 부족이라는 한계를 가지므로, 프롬프트 엔지니어링으로 제어 가능한 경량 메커니즘이 필요하다.
이러한 통찰에 기반하여, 모델 아키텍처나 디코더를 수정하지 않고 프롬프트 주입만으로 유연한 행동 제어를 달성하는 모듈식 설계를 채택한다.
본 메커니즘은 ReadAgent, MemoryBank, MemGPT, A-MEM 등 다양한 기존 프레임워크에 플러그인 방식으로 통합 가능해 범용성을 확보한다.

---

## Method

PAMU(Preference-Aware Memory Update) 메커니즘은 다음 단계로 구성된다.

1. **Preference Extractor 구축**: 매 대화 턴마다 사용자 선호 벡터 P = {p₁, p₂, …, p_D}를 5개 차원(Tone/Length/Emotion/Density/Formality)으로 추출한다.
2. **Tone Style 추출**: RoBERTa 기반 다중 클래스 분류기가 사용자 발화의 스타일 확률 분포를 산출하고, 최고 확률 카테고리와 점수를 튜플 (c, q)로 표현한다.
3. **Response Length 추출**: 과거 K턴 응답의 평균 토큰 수를 계산하고 [0, 1] 범위로 정규화하여 길이 차원을 형성한다.
4. **Emotional Tone 추출**: 감정 분류 모델이 사용자·어시스턴트 발화에서 지배적 감정 카테고리를 식별하고 확률 벡터를 반환한다.
5. **Information Density 추출**: OpenIE 모델로 어시스턴트 응답에서 (subject, predicate, object) 트리플을 추출하고 ID_t = K_t / L_t (트리플 수 / 단어 수)로 정의한다.
6. **Degree of Formality 추출**: 사전학습된 형식성 분류기가 응답을 0(완전 구어체)~1(완전 문어체)의 정규화 점수로 평가한다.
7. **연속 차원 SW 계산**: 길이 W의 슬라이딩 윈도우로 SW_t^(d) = (1/W) Σ_{i=t-W+1}^{t} p_i^(d) 를 산출하여 단기 평균을 유지한다.
8. **연속 차원 EMA 계산**: EMA_t^(d) = β · EMA_{t-1}^(d) + (1-β) · p_t^(d) (β ∈ (0,1)) 공식으로 장기 경향을 추적한다.
9. **범주 차원 SW/EMA**: 카테고리 확률 분포 q^(d) 에 대해 동일한 SW/EMA 연산을 적용한 뒤, argmax로 현재 생성 제어 레이블 c_t^(d) 를 선택한다.
10. **융합(Fusion)**: 최종 인지 벡터를 ŵ_t^(d) = λ · SW_t^(d) + (1-λ) · EMA_t^(d) (λ ∈ [0,1])로 계산하여 단기·장기 추정치를 결합한다.
11. **Change Detection Signal**: SW와 EMA 간 편차 Δ_t^(d) = SW_t^(d) − EMA_t^(d) 를 계산하고, 정규화된 탐지 점수 C_t^(d) = Δ_t^(d) / (ϵ + √(Var(SW)+Var(EMA))) 를 사용한다.
12. **적응 트리거**: C_t^(d) 가 임계값 δ를 초과하면 프롬프트 재작성, 메모리 그래프 재구조화, 전략 조정 중 하나를 즉시 트리거한다.
13. **Preference-Guided Prompting**: 융합 선호 벡터를 자연어 지시문으로 변환한다 (예: "[Tone: humorous], [Emotion: relaxed], [Information density: moderate], [Length: brief]").
14. **이산화 매핑**: 연속 차원은 사전 정의된 구간(Sparse/Moderate/Dense 등)으로 양자화하여 해석 가능한 의미 태그로 매핑한다.
15. **프롬프트 주입**: 최종 선호 프롬프트를 각 베이스라인(ReadAgent, MemoryBank, MemGPT, A-MEM)의 원본 입력에 append하여 모델 아키텍처 수정 없이 응답 생성을 제어한다.

---

## Key Contribution

1. **최초의 Preference-Aware Memory Update 메커니즘(PAMU) 제안**: 사용자 선호의 시간적 변화를 실시간으로 추적·갱신하여, 기존 메모리 시스템의 정적 가정 한계를 극복한다.
2. **SW+EMA 융합 프레임워크 설계**: 단기 변동(SW)과 장기 경향(EMA)을 동시에 포착하며, MVUE 및 Kalman 필터 근사로 이론적 정당성을 확보했다.
3. **해석 가능한 변화 감지 신호 도입**: SW-EMA divergence 기반 정규화 탐지 점수로 선호 급변 시점을 자동 탐지하고 적응적 프롬프트 재작성을 지원한다.
4. **경량·모델 불가지론적 모듈 설계**: 모델 아키텍처·디코더 수정 없이 프롬프트 엔지니어링만으로 선호 정렬을 달성하여 기존 메모리 프레임워크에 플러그인 방식으로 통합 가능하다.
5. **5차원 다차원 선호 표현 정의**: Tone Style·Response Length·Emotional Tone·Information Density·Degree of Formality의 구조화된 선호 벡터를 제안했다.
6. **광범위한 범용성 실증**: 4개 베이스라인(RA, MB, MG, AM) × 3개 태스크(SH, MH, Temporal) × 4개 모델 스케일(1.5B~30B)에서 일관된 성능 향상을 입증했다.
7. **Ablation 기반 모듈 기여도 검증**: SW, EMA, Detection, Prompt 등 각 구성요소가 독립적이고 비중복적인 역할을 수행함을 체계적으로 보였다.

---

## Experiment

**데이터셋**: LoCoMo — 50개 대화, 평균 300턴/대화, 최대 35세션, ~9,000 토큰/대화.
Single-hop(2,705쌍), Multi-hop(1,104쌍), Temporal reasoning(1,547쌍)의 3개 태스크에서 평가한다.
평가 지표는 F1 Score와 BLEU-1이며, 각 결과는 3회 독립 실행 평균이고 paired t-test로 p<0.05 유의성을 검증했다.

**베이스라인 및 모델**: ReadAgent(RA), MemoryBank(MB), MemGPT(MG), A-MEM(AM) 4종을 원본 vs PAMU 적용(†)으로 비교한다.
Qwen 2.5-1.5B/3B, LLaMA 3.2-1.5B/3B, LLaMA-7B/30B 총 6개 모델 스케일에서 실험을 수행했다.

**Single-hop (Qwen 2.5-3B)**: A-MEM†이 F1 **13.23** (기존 12.52), BLEU-1 **13.24** (기존 9.24)로 BLEU-1 +4.00 향상.
MemGPT†는 BLEU-1 **8.65** (기존 4.28)로 +4.37 포인트 개선.
MemoryBank†는 BLEU-1 **7.35** (기존 3.39)로 +3.96 포인트 상승.

**Multi-hop (LLaMA 3.2-3B)**: A-MEM†이 F1 **20.14** (기존 19.35), BLEU-1 **23.14** (기존 13.27)로 최고 성능을 기록했다 (+9.87 포인트).
MemoryBank†는 BLEU-1 **7.65** (기존 3.02)로 +4.63 향상.
MemGPT†도 BLEU-1 **6.34** (기존 2.95)로 +3.39 개선.

**Temporal Reasoning (LLaMA-7B)**: A-MEM†: F1 **23.23** (기존 17.55, +5.68), BLEU-1 **21.46** (기존 14.67, +6.79).
MemGPT†: F1 **17.54** (기존 11.14, +6.40), BLEU-1 **15.57** (기존 8.24, +7.33).
MemoryBank†: F1 **19.76** (기존 14.56, +5.20), BLEU-1 **17.24** (기존 11.95, +5.29).
LLaMA-30B 스케일에서도 A-MEM† F1 **19.87** (기존 12.54)로 큰 폭 개선.

**Ablation (Temporal Reasoning, LLaMA-7B, F1+BLEU-1 평균)**: Full PAMU가 A-MEM에서 **22.35**로 최고.
w/o SW → 15.36, w/o EMA → 14.05, Equal Fusion(λ=0.5) → 20.34, w/o Detection → 16.24, w/o Prompt → 15.45, Single Pref → 18.95, Static Pref → 19.47.
SW·EMA 제거 시 30–37% 성능 하락으로 두 구성요소의 필수성이 확인됐다.

**정성 평가**: GPT-4 자동 채점 + 10인 인간 평가자(학사 학위, 2주간 AI 도구 미사용).
Style Consistency **92/94%** (w/o PAMU: 37/35%), Preference Detection **97/95%** (w/o PAMU: 48/45%).
사용자 선호 정렬 점수 **4.8/4.5** vs w/o PAMU **2.1/2.2** (5점 만점).
Turn 3에서 선호 급변 시 PAMU는 즉시 적응한 반면, w/o PAMU는 2라운드 지연 후에야 반응했다.

---

## Limitation

선호 추출기가 RoBERTa, 감정 분류기, OpenIE, 형식성 분류기 등 다수의 외부 모델에 의존하여 추론 시 계산 오버헤드와 파이프라인 복잡도가 증가한다.
이들 외부 모델의 오분류 오류가 선호 벡터로 전파되어 하류 생성 품질에 영향을 미칠 수 있다.
선호 차원이 톤·길이·감정·밀도·형식성의 5가지로 사전 정의되어 있어, 도메인 특화 선호(코드 스타일, 시각적 선호 등)나 새로운 선호 유형으로의 확장은 수동적 재설계를 요구한다.
평가가 LoCoMo 단일 데이터셋에서만 수행되었으며, 실제 배포 환경이나 다른 장기 대화 벤치마크에서의 일반화 가능성이 검증되지 않았다.
융합 가중치 λ, 윈도우 크기 W, EMA 감쇠 계수 β, 변화 탐지 임계값 δ 등 하이퍼파라미터에 대한 체계적 민감도 분석이 부재하여 최적 설정 가이드라인이 없다.
프롬프트 주입 방식은 모델에 따라 선호 지시문 해석 능력 편차가 크며, 소형 모델(1.5B~3B)에서 절대 점수가 낮은 베이스라인이 이 한계를 시사한다.
다중 사용자 환경에서의 선호 충돌(preference conflict) 처리나 프라이버시 관련 고려 사항이 논의되지 않았다.
정성 평가가 저자가 직접 설계한 단일 시뮬레이션 대화 시나리오에 의존하여, 실제 사용자 연구(user study)를 통한 생태적 타당성(ecological validity)이 확보되지 않았다.

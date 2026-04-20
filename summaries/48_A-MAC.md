# A-MAC: Adaptive Memory Admission Control for LLM Agents

> **논문 정보**: Guilin Zhang, Wei Jiang, Xiejiashan Wang, Aisha Behr, Kai Zhao, Jeffrey Friedman, Xu Chu, Amine Anoun (Workday AI)
> **arXiv**: 2603.04549 (2026.03)
> **코드**: https://github.com/GuilinDev/Adaptive_Memory_Admission_Control_LLM_Agents

---

## Problem

LLM 기반 에이전트는 멀티턴 상호작용과 장기 추론을 위해 컨텍스트 윈도우를 넘어서는 장기 메모리(long-term memory)를 핵심 아키텍처 구성요소로 채택하고 있다.
그러나 현행 메모리 시스템은 "무엇을 저장할 것인가"에 대한 체계적인 입장 제어(admission control) 메커니즘을 거의 제공하지 않는다.
무분별한(indiscriminate) 저장은 메모리 저장소의 bloat을 일으키고 검색 latency를 증가시키며, 환각(hallucinated)되거나 outdated된 정보를 보존하여 이후 상호작용에 오류를 전파한다.
반대로 지나치게 보수적인(overly conservative) 입장 정책은 장기 horizon 추론과 태스크 연속성에 필수적인 정보를 폐기할 위험이 있다.
기존 시스템은 대량의 대화 콘텐츠를 무비판적으로 축적하거나, 불투명(opaque)하고 전적으로 LLM에 의존하는 메모리 정책을 채택해 비용이 높고 감사(audit)가 어렵다.
결과적으로 메모리 입장(admission)은 에이전트 아키텍처에서 약하게 명세되고 약하게 통제된 구성요소로 남아 있다.
Huang et al.(2023) 등이 지적한 할루시네이션 문제는 에이전트 신뢰성의 근본적 도전 과제이지만, 기존 heuristic 및 LLM-native 방식 모두 이를 1차적(first-class) 관심사로 다루지 않는다.
따라서 메모리 입장 결정을 명시적 제어 문제로 격상시키는 프레임워크가 요구된다.

---

## Motivation

기존 메모리 관리 접근은 크게 두 범주로 나뉘며 각각 뚜렷한 한계를 가진다.
첫째, MemGPT와 MemoryBank 같은 heuristic 기반 방식은 recency·relevance·importance를 결합한 수작업 scoring function에 의존하는데, 계산은 효율적이지만 할루시네이션 방지 장치가 없고 미묘한 admission 결정에 취약하다.
둘째, A-mem과 Mem0 같은 LLM-native 방식은 구조화된 메모리 속성을 LLM이 직접 생성하여 recall은 우수하지만 다중 LLM 호출로 인한 높은 계산 비용과 낮은 interpretability 문제를 갖는다.
어느 쪽도 할루시네이션을 1급 관심사로 취급하지 않아 신뢰성 확보가 어렵다.
또한 MemoryBank 같은 고정 가중치(linear scoring) 방식은 도메인에 따라 적응하지 못하고 다양한 대화 맥락으로 일반화되지 않는다.
저자들은 메모리 입장 결정을 Utility·Confidence·Novelty·Recency·Type Prior의 5가지 상호 보완적이고 해석 가능한(interpretable) 차원으로 분해하면 투명하고 효율적이며 데이터 기반으로 학습 가능한 구조적 의사결정이 된다고 주장한다.
특히 LLM 추론은 의미론적 판단이 필수인 Utility에만 국한하고 나머지 4개 신호는 결정론적 규칙으로 계산하여 정확도-효율성 간 우월한 절충점을 달성할 수 있다.
이러한 hybrid 설계는 개발자가 개별 feature 점수와 가중치 기여도를 검사하여 특정 메모리의 admission·reject 이유를 이해하고 debug·audit할 수 있게 한다.

---

## Method

A-MAC은 장기 메모리의 명시적 admission-control 레이어로, 각 후보 메모리를 5개의 해석 가능한 가치 신호로 평가해 학습된 결정 규칙을 통과할 때만 수용한다.

1. **전처리(Normalization)**: 대화 히스토리 H = {t₁, ..., t_T}에 경량 정규화를 적용. (a) 단일 턴을 원자적 정보 단위로 분할, (b) 시간 표현과 coreference 해소로 후보를 self-contained하게 만듦, (c) 인사말·acknowledgment 같은 저가치 콘텐츠 필터링.
2. **Admission as Scalar Scoring**: 후보 m에 대해 합성 점수 S(m) = w₁·U(m) + w₂·C(m) + w₃·N(m) + w₄·R(m) + w₅·T(m)을 계산. 각 feature function은 [0,1]로 매핑되며 wᵢ ≥ 0, Σwᵢ = 1. S(m) ≥ θ일 때 입장 승인.
3. **Utility U(m)**: 후보가 향후 상호작용에서 actionable한지, follow-up 질문을 지원하는지, 지속적 사용자 제약·선호를 포착하는지를 LLM 단일 호출로 평가. temperature=0으로 결정적 출력을 보장하고 반복 후보는 점수 캐싱으로 API 비용 절감.
4. **Confidence C(m) = max_{s ∈ Support(m)} ROUGE-L(m, s)**: 대화 내 evidence 존재 여부를 longest-common-subsequence 기반 ROUGE-L로 측정. 근거 있는 겹침은 보상하고 fabricated 세부는 페널티화하여 할루시네이션 전파를 직접 억제.
5. **Novelty N(m) = 1 − max_{m' ∈ M} cos(φ(m), φ(m'))**: Sentence-BERT 임베딩 φ(·) 기반 코사인 유사도로 기존 메모리와의 중복을 측정. 기존 메모리 임베딩은 사전 계산해 후보당 1회 임베딩만 필요.
6. **Recency R(m) = exp(−λ·τ(m))**: 후보가 언급된 이후 경과 시간 τ(m)에 대한 지수 감쇠. λ=0.01/hour(반감기 ≈ 69시간)로 시간적 가치 하락 모델링.
7. **Type Prior T(m)**: POS(part-of-speech) 기반 규칙 매칭으로 정보 유형을 분류. 선호도·신원 진술 등 안정적 정보에는 높은 prior, 일시적 상태에는 낮은 prior 부여.
8. **정책 학습(Policy Learning)**: labeled training 대화로부터 5-fold cross-validation으로 F1을 최대화하는 가중치 ω* = [w₁,...,w₅]와 임계값 θ*를 grid search로 학습. θ 탐색 범위 [0.3, 0.6], 학습된 θ* = 0.55.
9. **Conflict Resolution**: 코사인 유사도 > 0.85이면서 내용이 다른 후보는 기존 메모리와 충돌로 판단. 더 높은 S를 받은 표현을 유지하고 Merge(m, m_conflict)로 장기 메모리를 compact하고 최신 상태로 유지.
10. **Algorithm 1 요약**: M' ← M, U·C·N·R·T를 병렬 계산 → S(m) ← ω·[U,C,N,R,T]ᵀ → S(m) ≥ θ이면 FindConflict → 승점 비교 후 Merge 또는 insert → 갱신된 M' 반환.

---

## Key Contribution

1. **메모리 입장 제어의 형식화**: 기존 heuristic/LLM-native 방식의 한계를 분석하고, memory admission을 LLM 에이전트의 under-specified control 문제로 식별 및 1급 결정 문제로 격상.
2. **5차원 해석 가능 프레임워크(A-MAC)**: Utility·Confidence·Novelty·Recency·Type Prior의 상호 보완적 차원으로 후보 메모리의 가치·신뢰성·지속성을 공동 포착하는 명시적 admission-control 레이어 제안.
3. **Hybrid 계산 설계**: 의미 판단이 필요한 Utility에만 LLM 단일 호출, 나머지 4개 feature는 rule-based(ROUGE-L, SBERT, exponential decay, POS rules)로 65ms 이내 처리해 해석성·정확도·효율성의 유리한 절충 달성.
4. **Cross-validated 정책 학습**: ground-truth admission label로부터 5-fold CV와 grid search로 도메인 적응형 가중치와 임계값을 자동 학습하여 수동 튜닝 없이 도메인 이동에 적응.
5. **할루시네이션 인식(admission-time) 필터링**: Confidence 요인을 통해 대화 내 근거 없는 fabricated 정보를 admission 단계에서 차단하여 기존 RAG 계열의 retrieval-time grounding을 보완.
6. **실증적 SOTA 달성**: LoCoMo에서 F1=0.583으로 A-mem 대비 +7.8% relative 개선 및 31% latency 감소, Type Prior가 가장 영향력 큰 feature임을 ablation으로 규명.

---

## Experiment

- **벤치마크**: LoCoMo (Maharana et al., 2024), 30개 대화, 각 15–40턴, 약 1,500개 ground-truth 레이블 후보 메모리. 개인 비서·기술 지원·연구 협업 대화 포함.
- **데이터 분할**: Train 70% / Val 15% / Test 15%(N=225).
- **구성**: Sentence-BERT 임베딩, Utility scoring은 로컬 LLM Qwen 2.5 사용.
- **Baselines**: Random(30% 확률), MemGPT, MemoryBank, Equal Weights, A-mem(SOTA).

**주요 결과(Table 1, N=225)**:
- A-MAC F1 = **0.583**, A-mem 0.541 대비 +7.8% relative, Equal Weights 0.476 대비 +22.4%, MemoryBank 0.452 대비 +29.0%, MemGPT 0.324 대비 +80%.
- Precision 0.417로 LLM 기반 방법 중 최고(A-mem 0.371 대비 +12.4%), Recall 0.972로 near-perfect.
- Latency 2644ms, A-mem 3831ms 대비 **31% 감소**.

**Ablation(Table 2, Full 0.583 대비 ΔF1)**:
- −Type Prior: 0.476 (ΔF1 = −0.107) — Equal Weights 수준으로 하락, 가장 큰 기여.
- −Novelty: 0.555 (−0.028), −Utility: 0.560 (−0.023), −Confidence: 0.568 (−0.015), −Recency: 0.570 (−0.013).

**Threshold sensitivity(Table 3)**: θ=0.30–0.40에서 Precision 0.360/Recall 1.000, θ*=0.55에서 Val F1 0.571 최고, θ=0.70에서는 Recall 0.444로 급락. θ=0.50–0.60 F1 plateau로 deployment 견고성 확보.

**Latency 분해(Table 4)**: Utility(LLM) 2580ms(97.6%), Novelty(SBERT) 32ms(1.2%), Confidence(ROUGE-L) 18ms(0.7%), Type Prior(Rules) 14ms(0.5%), Recency(Decay) <1ms. Rule-based 합계 65ms 미만.

**Cross-domain(Table 5)**: Personal(N=127) F1=0.482, Professional(N=98) F1=0.338, 도메인 간 σ=0.102. 동일 가중치로 retuning 없이 두 도메인에 전이 가능.

---

## Limitation

본 연구는 ICLR 2026 Workshop MemAgent에 게재된 예비적 검증에 해당하며 대규모·다중 벤치마크 검증이 제공되지 않는다.
LoCoMo 단일 벤치마크(30 대화, 225 테스트 샘플)로만 평가되어 산업 규모 배포 환경으로의 일반화 여부가 불명확하다.
5가지 admission 요인의 최적 가중치가 도메인에 따라 달라지며, Personal과 Professional 간 F1 편차(σ=0.102)로 인해 특히 Professional 도메인(F1 0.338)에서 implicit context와 domain-specific terminology를 충분히 포착하지 못한다.
Utility 계산이 전체 latency의 **97.6%(2580ms)**를 차지하는 단일 LLM 호출에 의존하여 여전히 비용 병목이며, rule-based 4개 feature의 효율(65ms 미만) 대비 비대칭 구조를 띤다.
가중치 학습이 ground-truth admission label이 있는 supervised 방식으로, 레이블이 없는 도메인이나 새로운 배포 환경에서의 bootstrapping 절차가 명시되지 않았다.
Confidence 신호가 ROUGE-L(순수 표면 문자열 LCS) 기반이라 의미적으로 등가하나 표현이 다른 evidence는 낮게 평가될 수 있어 paraphrastic grounding 검증에 한계가 있다.
Type Prior가 POS 기반 rule matching으로 구현되어 복잡한 의도나 도메인 특화 정보 카테고리를 포착하는 데 제한적이다.
마지막으로 threshold·weight 조합이 학습 시점에 고정되어 대화 누적에 따른 메모리 통계 drift에 대한 online adaptation 메커니즘이 부재하다.

# A-MAC: Adaptive Memory Admission Control for LLM Agents

> **논문 정보**: Guilin Zhang, Wei Jiang, Xiejiashan Wang, Aisha Behr, Kai Zhao, Jeffrey Friedman, Xu Chu, Amine Anoun (Workday AI)
> **arXiv**: 2603.04549 (2026.03)
> **코드**: https://github.com/GuilinDev/Adaptive_Memory_Admission_Control_LLM_Agents

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 장기 메모리 시스템은 "무엇을 저장할 것인가"에 대한 체계적 입장 제어(admission control)가 부재하다. 무분별한 저장은 환각(hallucination) 전파, 메모리 bloat, 검색 품질 저하를 유발하고, 반대로 과도하게 보수적인 정책은 장기 추론에 필요한 정보를 소실시킨다. |
| **Motivation** | 기존 heuristic 방식(MemGPT, MemoryBank)은 사실적 신뢰도 검증 없이 정적 규칙에 의존하고, LLM-native 방식(A-mem, Mem0)은 높은 계산 비용과 낮은 interpretability 문제를 갖는다. 메모리 입장 결정을 5가지 독립 요인으로 분해하면 투명하고 효율적인 구조적 의사결정이 가능하다. |
| **Limitation** | (1) ICLR 2026 Workshop 논문으로 예비적 검증에 그치며 대규모 실험 미제공. (2) 5가지 요인의 최적 가중치가 도메인에 따라 달라지며, Personal vs Professional 간 F1 편차(σ=0.102)가 크다. (3) Utility 계산이 전체 latency의 97.6%를 차지하는 LLM 호출에 의존하여 비용 병목. (4) 가중치 학습에 ground-truth admission label이 필요한 supervised 방식으로 레이블 없는 도메인 적용 시 한계 존재. |

---

## Method

A-MAC은 각 후보 메모리를 장기 저장소에 편입하기 전에 5개의 해석 가능한 신호로 평가하는 명시적 입장 제어 레이어를 도입한다.

**전처리 (Normalization)**
대화 히스토리에서 후보 메모리를 추출하기 전에 경량 정규화를 수행한다: (1) 단일 턴을 원자적 정보 단위로 분할, (2) 시간 표현과 coreference 해소, (3) 인사말·확인 발화 등 저가치 콘텐츠 필터링.

**5가지 입장 요인 (Admission Factors)**
각 후보 메모리 m에 대해 합성 점수 S(m) = w₁·U(m) + w₂·C(m) + w₃·N(m) + w₄·R(m) + w₅·T(m)을 계산한다 (wᵢ ≥ 0, Σwᵢ = 1).

1. **Utility U(m)**: 미래 상호작용에서 유용할 가능성을 LLM 단일 호출로 평가. temperature=0으로 결정적 출력 보장
2. **Confidence C(m)**: 할루시네이션 전파 방지를 위해 대화 내 근거 존재 여부를 ROUGE-L로 측정. C(m) = max_{s∈Support(m)} ROUGE-L(m, s)
3. **Novelty N(m)**: Sentence-BERT 임베딩 기반 코사인 유사도로 기존 메모리와의 중복 측정. N(m) = 1 − max_{m'∈M} cos(φ(m), φ(m'))
4. **Recency R(m)**: 지수 감쇠 R(m) = exp(−λ·τ(m)), λ=0.01/hour(반감기 약 69시간)로 시간적 가치 감소를 모델링
5. **Type Prior T(m)**: POS 기반 규칙 매칭으로 정보 유형을 분류. 선호도·신원 진술 등 안정적 정보에 높은 prior 부여

**정책 학습 (Policy Learning)**
5-fold cross-validation으로 F1을 최대화하는 가중치 벡터 ω*와 임계값 θ*를 grid search로 학습 (θ ∈ [0.3, 0.6], 학습된 θ* = 0.55). S(m) ≥ θ이면 입장 승인.

**충돌 해소 (Conflict Resolution)**
코사인 유사도 > 0.85이나 내용이 다른 후보는 기존 메모리와 충돌로 판단. 더 높은 점수를 받은 표현을 유지하고 Merge하여 최신·컴팩트 상태로 유지.

---

## Key Contribution

1. **메모리 입장 제어의 구조적 형식화**: "무엇을 기억할 것인가"를 Utility, Confidence, Novelty, Recency, Type Prior의 5가지 독립·해석 가능한 차원으로 명시적으로 분해
2. **Hybrid 아키텍처**: 의미론적 판단이 필요한 Utility에만 LLM 단일 호출, 나머지 4가지는 rule-based로 65ms 이내 처리
3. **Cross-validated 정책 학습**: ground-truth label로부터 도메인 적응형 가중치를 자동 학습
4. **할루시네이션 인식 설계**: Confidence 요인이 ROUGE-L 기반으로 근거 없는 정보를 입장 단계에서 필터링

---

## Experiment & Results

- **벤치마크**: LoCoMo (30개 대화, 각 15~40턴, ~1,500개 후보 메모리)
- **임베딩**: Sentence-BERT / Utility scoring: Qwen 2.5
- **비교 기준선**: Random, MemGPT, MemoryBank, Equal Weights, A-mem (SOTA)

**주요 결과 (LoCoMo test set, N=225)**:
- A-MAC F1=0.583 vs A-mem 0.541 (+7.8%), MemoryBank 0.452 (+29.0%), MemGPT 0.324 (+80%)
- Precision 0.417로 LLM 기반 방법 중 최고 (A-mem 0.371 대비 +12.4%)
- Latency 2644ms로 A-mem(3831ms) 대비 31% 감소

**Ablation (각 요인 제거 시 F1)**:
- Full: 0.583 / -Type Prior: 0.476 (−0.107) / -Novelty: 0.555 (−0.028) / -Utility: 0.560 (−0.023) / -Confidence: 0.568 / -Recency: 0.570
- Type Prior 제거 시 최대 영향 — 안정적 정보와 일시적 감정 구별이 가장 강력한 heuristic

**임계값 민감도**: θ=0.50~0.60 구간에서 F1 plateau, 배포 시 튜닝 민감도 낮음

**Latency 분해**: Utility(LLM) 2580ms (97.6%), Confidence 18ms, Novelty 32ms, Recency <1ms, Type Prior 14ms

**Cross-domain**: Personal F1=0.482 / Professional F1=0.338, 동일 가중치로 두 도메인에서 유효

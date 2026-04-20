# Towards Thinking-Optimal Scaling of Test-Time Compute for LLM Reasoning

> **논문 정보**: Wenkai Yang, Shuming Ma, Yankai Lin, Furu Wei (Renmin University of China, Microsoft Research)
> **arXiv**: 2502.18080 (2025.02, NeurIPS 2025)
> **코드**: https://github.com/RUCBM/TOPS

---

## Problem

OpenAI o1을 비롯한 최근 o1류 모델들은 긴 Chain-of-Thought(CoT)로 추론 토큰을 확장할수록 복잡한 추론 성능이 지속적으로 향상된다는 가정 아래 개발되고 있다.

그러나 QwQ-32B-Preview와 같은 후속 o1류 모델은 그들의 System-1 모델(Qwen2.5-32B-Instruct) 대비 훨씬 많은 토큰을 생성함에도 성능 향상은 제한적이며, 특히 쉬운 태스크에서 효율성이 급격히 나빠진다.

기존 동시대 연구들(O1-Pruner, Overthinking of o1-like LLMs)은 "overthinking"의 효율 문제(불필요한 토큰)를 다루지만, 긴 CoT가 실제로 "성능"을 저하시킬 수 있는지는 체계적으로 검증되지 않았다.

또한 o1류 모델마다 기반 모델이 달라 공정한 비교가 불가능하여, 동일 기반 모델에서 CoT 길이를 변화시켰을 때의 영향을 통제된 조건에서 측정한 연구가 부재하다.

태스크 난이도(GSM8K 초등→MATH500 고교→AIME2024 경시)에 따라 최적 추론 길이가 어떻게 달라지는지, 그리고 이를 모델이 스스로 결정하게 하는 방법은 미개척 영역이다.

Distillation 기반 기존 접근(STILL-2, Sky-T1)들은 교사 모델의 고정된 길이 분포를 그대로 학습시켜 학생 모델의 thinking-optimal 분포와 어긋날 수 있다.

따라서 "test-time scaling이 항상 이득인가? 아니라면 언제 역효과이며, 어떻게 최적 길이를 결정할 것인가?"가 본 논문의 핵심 물음이다.

---

## Motivation

저자들은 MATH500과 AIME2024 전반에서 o1-mini, QwQ-32B-Preview, Gemini-2.0-Flash-Thinking, DeepSeek-R1을 각자의 System-1 짝(gpt-4o-mini, Qwen2.5-32B-Instruct, Gemini-2.0-Flash, DeepSeek-V3)과 비교한 예비 분석에서, QwQ-32B-Preview가 토큰 수는 급증하지만 accuracy gain은 상대적으로 작은 "비효율적 스케일링" 패턴을 발견했다.

공정 비교를 위해 LLaMA3.1-8B-Instruct와 Qwen2.5-32B-Instruct 위에 Low/Medium/High 세 가지 reasoning effort의 동일 문제 쌍 데이터를 구축하고 각각 학습한 결과, "긴 CoT로 학습한 모델이 쉬운 GSM8K에서 오히려 성능이 낮아진다"는 역설적 현상을 관측했다.

이 현상의 원인을 gpt-4o로 reasoning rounds와 erroneous rounds를 분석하여 추적한 결과, 추론 effort가 높아질수록 reasoning round 수뿐 아니라 "오류를 포함한 round 수와 비율"도 함께 증가함을 확인했다.

즉, 긴 CoT는 일부 오류+반성(reflection+correction) 패턴을 학습시키는 순기능이 있지만 오류 단계가 과도해지면 모델이 잘못된 추론 패턴 자체를 학습해버려 성능이 하락한다.

추가로 erroneous step에 loss masking을 적용하면 긴 CoT 학습 성능이 개선되어 "오류 step에 대한 학습"이 성능 저하의 핵심 요인임을 검증했다.

동시에 난이도가 높은 AIME2024에서는 Medium/High effort가 Low보다 우수하므로 "난이도별 최적 길이"가 존재하며, 흥미롭게도 최적 effort는 5-sample 내 distinct answer 수가 가장 적은(가장 일관된) 지점과 일치했다.

따라서 모델이 스스로 문제마다 "정답을 낼 수 있는 가장 짧은 System-2 응답"을 선택하게 하는 self-improvement 전략이 효과성과 효율성을 동시에 달성할 수 있다는 결론에 도달했다.

---

## Method

1. **Thinking-Optimal Response 정의**: "System-2 thinking을 수행하는 동시에 정답을 낼 수 있는 최단 응답"을 최적 응답으로 정의. 이보다 짧으면 오답이 될 수 있고, 길면 overthinking/오류 step이 증가한다.

2. **Seed 데이터 curation (Stage 0)**: NuminaMath 서브셋에서 약 1.3K 문제를 추출하여 QwQ-32B-Preview를 교사로 사용해 Low/Medium/High 세 가지 system prompt로 각각 응답을 생성한다. 세 응답이 모두 정답이고 pairwise 길이 차가 300 token 이상인 경우만 유지하여 교사의 부정확한 instruction-following을 보완한다.

3. **Stage 1 — Format Imitation (Tag 모델 학습)**: 기반 모델(Qwen2.5-32B-Instruct 또는 LLaMA3.1-8B-Instruct)을 위 seed 데이터로 SFT한다. 각 reasoning effort에 대응하는 별도의 system prompt(e₁/e₂/e₃)를 할당해 하나의 모델이 프롬프트에 따라 서로 다른 길이의 System-2 사고(searching, reflecting, verification, backtracking)를 수행하도록 학습한다. 목적함수: θ_tag = argmax E_(eᵢ,x,yᵉⁱ)~Ds[P(yᵉⁱ|eᵢ,x,θ)].

4. **Stage 2 — Reasoning Effort-Conditioned Generation**: Tag 모델을 사용해 NuminaMath의 추가 50K 문제(Pₐ)에 대해 Low/Medium/High 각각 1개씩 응답을 생성한다. 각 effort eᵢ에 대해 yᵉⁱ ~ π(·|eᵢ, x; θ_tag)를 샘플링하여 동일 문제에 대한 세 가지 길이 경로를 확보한다.

5. **Stage 3 — Shortest Correct Selection**: 각 문제 x에 대해 세 응답 중 "정답이면서 가장 짧은" 응답 y_sc를 선택해 thinking-optimal 데이터셋 D_TOP = {(x, y_sc)}를 구성한다. Seed 데이터의 Low-effort 응답도 포함시켜 총 약 26K 샘플을 확보한다.

6. **Stage 4 — Self-Improvement (SFT)**: 기반 모델을 D_TOP으로 SFT하여 Qwen2.5-32B-TOPS를 얻는다. θ_TOP = argmax E_(x,y_sc)~D_TOP[P(y_sc|x,θ)]. 학습률 1e-5, batch 96, epoch 2.

7. **Stage 5 — Iterative Self-Improvement (SFT 변형)**: 추가 4500개 MATH 문제와 AIME1983-2023 문제에 대해 Qwen2.5-32B-TOPS로 각 8 응답을 샘플링 → 정답 중 최단 응답을 chosen으로 SFT → Qwen2.5-32B-TOPS-Iter-SFT 생성.

8. **Stage 6 — Iterative Self-Improvement (DPO 변형)**: chosen = 최단 정답, rejected = 최장 오답으로 preference pair 구성. 만약 chosen보다 짧은 오답이 존재하면 "최단 오답"도 rejected에 포함시켜 underthinking을 방지. 이렇게 구성한 데이터로 DPO를 수행해 Qwen2.5-32B-TOPS-Iter-DPO를 얻는다.

9. **Baseline 검증 설계 (Random ablation)**: 동일한 reasoning effort-conditioned generation 결과에서 "최단" 대신 "무작위 정답"을 선택한 Qwen2.5-32B-Random을 대조군으로 구축하여 "shortest" 선택의 필요성을 분리 검증한다.

10. **Loss Masking Validation (Section 3.3)**: LLaMA3.1-8B에 대해 Qwen2.5-72B-Instruct가 비평한 erroneous step에 loss masking을 적용/비적용 학습을 비교해 "오류 step에 대한 loss 계산"이 성능 저하의 직접 원인임을 인과적으로 검증한다.

---

## Key Contribution

1. **Test-time scaling의 역효과 최초 규명**: 동일 기반 모델 + 동일 문제셋 통제 실험으로 "긴 CoT 학습이 쉬운 태스크(GSM8K, MATH500 저난이도)에서 성능을 저하시킨다"는 반직관적 현상을 최초로 체계적으로 입증하였다. 기존 연구들의 "효율 문제" 시각을 넘어 "효과성 저하"로 문제를 재정의했다.

2. **Optimal reasoning effort의 난이도 의존성 발견**: GSM8K에서는 Low effort, MATH500에서는 Medium effort, AIME2024에서는 Medium/High effort가 최적임을 정량 확인하고, 최적 effort가 5-sample 간 distinct answer 수 최소점과 일치함을 밝혔다(under/overthinking 판별의 프록시 지표 제공).

3. **TOPS 3단계 프레임워크 제안**: Format Imitation → Reasoning Effort-Conditioned Generation → Shortest-Correct Self-Improvement라는 일반적이고 재현 가능한 파이프라인으로 1.3K seed만으로 o1류 모델을 self-improvement할 수 있는 레시피를 제시하였다.

4. **오류 step이 성능 저하의 인과 요인임을 검증**: reasoning rounds와 erroneous rounds 통계 + loss masking 실험 + reflection-augmented long CoT 학습 대조를 통해 "긴 CoT의 해로움은 overthinking이 아니라 erroneous step에 대한 loss 신호"에 기인함을 인과적으로 분리하였다.

5. **Iterative DPO 확장으로 QwQ-32B-Preview 근접**: Qwen2.5-32B-TOPS-Iter-DPO가 QwQ-32B-Preview와 동등하거나 나은 accuracy를 달성하면서 훨씬 적은 token으로 추론해 효율+효과 동시 달성.

6. **Adaptive reasoning depth 실증**: TOPS 모델이 GSM8K에서는 짧게(~412 token), AIME2024에서는 길게(~7260 token) 자연스럽게 조절하는 난이도 인지적 토큰 분배를 학습함을 확인.

7. **일반성 검증**: LLaMA3.1-8B-Instruct에서도 동일 레시피가 작동해 다른 모델 아키텍처/스케일로 전이 가능함을 보였고, Appendix J에서 수학 외 일반 추론으로의 확장 가능성도 제시.

---

## Experiment

**데이터 규모**: Seed 1.3K 문제 × 3 effort = 3.9K 응답 + 추가 50K NuminaMath 문제로 효과-조건부 생성 → 최단 정답 선택으로 약 26K thinking-optimal 샘플을 구축.

**Seed 데이터 통계**: LLaMA3.1-8B-Tag용 1256 문제(Low 1532, Medium 2460, High 3648 tokens), Qwen2.5-32B-Tag용 1312 문제(Low 1588, Medium 2536, High 3768 tokens).

**Tag 모델 학습 설정**: lr 1e-5, batch 32, epoch 3(Qwen) / 5(LLaMA), 8× H100 80G. TOPS SFT는 lr 1e-5, batch 96, epoch 2.

**주 결과 (Qwen2.5-32B 기반, Table 3)**: GSM8K에서 Qwen2.5-32B-TOPS 95.82% / 412 token, MATH500 91.48% / 1883 token, AIME2024 43.33% / 7260 token.

**QwQ-32B-Preview 대비**: QwQ는 GSM8K 95.23%/761 token, MATH500 92.02%/2416 token, AIME2024 45.33%/7637 token. TOPS는 GSM8K에서 유사 성능에 토큰 46% 절감, MATH500 근접 성능에 22% 절감을 달성.

**기존 distillation 모델 대비**: STILL-2-32B(95.47/91.40/45.33)와 Sky-T1-32B-Preview(94.82/89.48/35.33)를 대부분 항목에서 상회. Sky-T1 대비 MATH500 +2.00p, AIME2024 +8.00p.

**Random 대비 ablation**: Qwen2.5-32B-Random(95.00/90.16/39.33, 938/2670/7691 token)보다 TOPS가 동시에 정확도↑ + 토큰↓를 달성해 "shortest correct selection"이 핵심임을 입증.

**Iterative 결과**: Qwen2.5-32B-TOPS-Iter-DPO가 GSM8K 95.80%/385 token, MATH500 91.60%/1732 token, AIME2024 46.00%/6427 token으로 QwQ-32B-Preview를 AIME2024에서 초월.

**LLaMA3.1-8B 일반화 (Table 4)**: LLaMA3.1-8B-TOPS-SFT가 GSM8K 88.54%/571 token, MATH500 61.28%/3254 token, AIME2024 8.00%/7393 token. Random-SFT(87.94/60.52/4.67) 대비 모든 항목 우위.

**Reasoning rounds 분석 (Figure 4)**: reasoning effort가 High로 갈수록 총 reasoning rounds 증가, erroneous rounds 수 및 비율 동반 증가 확인.

**Loss masking 검증 (Figure 5, MATH500)**: long CoT w/o masking 약 48%, w/ masking 약 50.5%, LLaMA3.1-8B-Instruct 기준 47% 근방 → 오류 step masking이 약 +2.5p 개선.

**Distinct answer 분석 (Table 2)**: 최적 effort에서 5-sample 간 distinct answer 수 최소(예: Qwen2.5-32B-Tag-Medium, MATH500 91.48% / 1.36 distinct).

**평가 설정**: decoding temperature 1.0, max gen 16,384 tokens, 5 random seed 평균, MATH500 format 이슈는 gpt-4o 보조 판정, 토큰 수 공정 비교를 위해 Qwen2.5 tokenizer 통일.

---

## Limitation

저자 언급(1) — 실험이 수학 도메인에 편중되어 있다. 수학은 자동 채점이 용이해 선택된 것이지만 일반 추론/상식/코드 도메인에서의 "긴 CoT 역효과"가 동일하게 나타나는지는 Appendix J의 예비 결과 외에는 본격 검증되지 않았다.

저자 언급(2) — SFT/distillation 중심 설정으로 국한되어 있으며 RL(특히 RLHF/GRPO) 기반 test-time scaling에서 shortest-correct 선호가 어떻게 적용될지는 향후 과제로 남겼다. 저자들은 RL이 모든 정답에 동일 보상을 주는 현행 설계가 긴 오류-포함 경로를 선호할 수 있다고 추측만 제시한다.

독자 관점(3) — Thinking-optimal 응답의 선택이 "학습 데이터 내에서 최단 정답"에 의존하므로, Tag 모델이 모든 effort에서 실패하는 초고난도 문제(예: FrontierMath급)에는 레시피가 적용되지 않으며, seed 문제 분포 외의 난이도 범위에 대한 일반화가 불확실하다.

독자 관점(4) — 교사 모델 QwQ-32B-Preview의 품질과 instruction-following 결함(pairwise 300-token 필터링으로 상당수 drop됨)에 파이프라인 전체가 의존한다. 교사 모델이 부재하거나 약한 영역에서는 재현이 어렵다.

독자 관점(5) — Reasoning effort가 Low/Medium/High 3단계로만 이산화되어 있어 연속적인 난이도-길이 매핑을 학습하지 못한다. 이론적으로 최적 길이는 연속량이므로 3bin 이산화는 suboptimal일 수 있다.

독자 관점(6) — Reasoning round와 erroneous round 집계가 gpt-4o 판정에 의존하므로 judge 모델의 편향이 "오류 step이 해롭다"는 인과 결론에 스며들 가능성을 완전히 배제하기 어렵다.

독자 관점(7) — Iterative DPO에서 rejected로 "최단 오답"을 포함시키는 규칙이 underthinking을 방지하지만, 하이퍼파라미터 의존성이 높고 오답 분포에 민감할 수 있다. 다른 도메인에서 이 rule이 그대로 작동할지는 불확실하다.

독자 관점(8) — 평가 벤치마크(GSM8K/MATH500/AIME2024)가 교사 모델 학습 분포(NuminaMath, AIME1983-2023 포함)와 부분 중첩되어 data contamination의 가능성이 완전히 통제되지 않았다.

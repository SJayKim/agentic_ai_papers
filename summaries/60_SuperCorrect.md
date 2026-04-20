# SuperCorrect: Advancing Small LLM Reasoning with Thought Template Distillation and Self-Correction

> **논문 정보**: Ling Yang, Zhaochen Yu, Tianjun Zhang, Minkai Xu, Joseph E. Gonzalez, Bin Cui, Shuicheng Yan (PKU, Skywork AI, NUS, UC Berkeley, Stanford)
> **arXiv**: 2410.09008 (2024.10)
> **학회**: ICLR 2025
> **코드**: https://github.com/YangLing0818/SuperCorrect-llm

---

## Problem

소형 LLM(7B~8B급 Llama-3-8B, Qwen2.5-Math-7B, DeepSeekMath-7B)은 대규모 수학 데이터 사전학습에도 불구하고 복잡한 수학적 추론 과제에서 여전히 크게 고전한다.
특히 자신의 추론 단계에서 발생한 오류를 스스로 식별·교정하는 능력이 결여되어 있다.
기존 전통적 fine-tuning(SFT/RLHF/DPO)은 최종 답이나 단순 reasoning rationale에만 최적화되어, 중간 단계 오류를 위치시키고 교정하는 학습을 수행하지 못한다.
Reflection 기반 방법(Reflexion, RCI)은 ground-truth correctness를 외부 신호로 필요로 하며, 단일 LLM 내부에서의 self-correction은 이전 추론 컨텍스트에 편향되어 실패하거나 오히려 정답을 오답으로 바꾸기도 한다.
Step-DPO 같은 단계-단위 보상은 단위는 세분화했지만 오류 원인 설명과 명시적 교정 가이드를 제공하지 못한다.
CoT·ToT·GoT·PoT 등 thought expansion 방식은 수작업 프롬프트에 의존하거나 특정 과제에 한정되며, BoT 같은 training-free 방식은 내재적 추론 능력을 근본적으로 향상시키지 못한다.
결과적으로 소형 모델은 "사고의 병목(thought bottleneck)"에 갇혀 어려운 주제(geometry, number theory 등)에서 성능 저하가 누적된다.

---

## Motivation

대형 교사 LLM(o1-mini/o1-preview/GPT-4o-mini)의 고품질 사고 패턴과 교정 능력을 구조적으로 추출해 소형 학생 LLM에 이식할 수 있다면, 소형 모델의 추론·교정 능력을 동시에 비약적으로 향상시킬 수 있다.
단순 CoT 모방을 넘어, 일반화된 고수준 전략과 단계별 세부 주석을 포함하는 "계층적 사고 템플릿(hierarchical thought template)"을 SFT로 전달하면 학생 모델이 더 세밀하고 일관된 추론을 산출할 수 있다.
추가로 학생 자신의 self-correction trace와 교사의 cross-model correction trace를 pair로 구성해 DPO로 학습시키면, 학생 모델이 교사의 오류 탐지·교정 통찰을 흡수해 자신의 사고 병목을 돌파할 수 있다.
즉, 추론(thinking)과 교정(correcting)을 **이중 분리된 2단계 감독**으로 설계해야 각각의 학습 목표가 서로 간섭하지 않는다.
기존 Step-DPO의 instance/step 수준 보상 대신 **thought-level reward** — 개별 오류 단계의 교정 trace 그 자체를 최적화 단위로 삼는 것이 핵심이다.
이렇게 하면 올바른 이전 단계들이 rejected로 잘못 학습되는 문제를 회피할 수 있다.

---

## Method

1. **Stage 1 — Hierarchical SFT (HSFT) 데이터 구축**: MATH(7,500), GSM8K(7,473), GaoKao Bench(670 번역), NuminaMath/MetaMath 샘플을 수집해 총 100K 규모의 수학 문제-풀이 집합 D={(x, ŷ, ŝ)}를 구성한다.
2. **계층적 사고 템플릿 추출 프롬프트 `P_tea`**: 교사 LLM(o1-mini / GPT-4o-mini)에 XML 단계 구조로 변환을 지시한다 — 각 단계 `<Step_k>` 내 어려운 계산에는 `<Key>` 태그로 상세 주석, 전체 풀이 말미에 `<Generalized>` 태그로 일반화 전략, `<Answer>`로 최종 답.
3. **HSFT 학습 목표**: `L_sft`는 prompt `P_stu`와 문제 x가 주어졌을 때 (T_tea, s_tea) 응답의 likelihood를 최대화한다 — 학생 LLM π가 교사의 계층적 사고 구조를 모방하도록 훈련해 π_ref를 얻는다.
4. **Stage 2 — 오류 trace 수집**: 학생 HSFT 모델 π_ref를 D_test에 적용해 π_sft(x_test) 산출 → 오답(y_test ≠ ŷ_test)만 필터링해 D_err = {x, ŷ, ŝ, s_err, T_err, y_err}를 얻는다 (세 SFT 모델에서 20K 오답 수집).
5. **Cross-model correction trace 생성**: 교사 LLM이 ground-truth를 컨텍스트로 삼아 각 오류 단계 k에 대해 `<Cause>`(원인 분석 a⁺_k)와 `<Correction>`(교정 c⁺_k)을 생성 — ground-truth grounding으로 정확성 확보.
6. **Self-correction trace 생성**: 학생 모델 자신에게 ground-truth 없이 자기 교정을 시켜 (a⁻_k, c⁻_k)를 얻는다 — rejected 후보.
7. **Inspector LLM 품질 검증**: o1-preview가 교사 생성 correction trace를 검수 — GPT-4o-mini 교사 기준 MATH 정확도 92.4%→98.8%, GaoKao 89.6%→96.2%로 향상.
8. **Thought-level Cross-DPO 목적 함수**: `L_Cross-DPO(θ) = -E[log σ(β log π_θ((a⁺_k, c⁺_k)|x; s_{1~k-1}) / π_ref - β log π_θ((a⁻_k, c⁻_k)|x; s_{1~k-1}) / π_ref)]` — 이전 올바른 단계 s_{1~k-1}을 조건으로 두어 오직 오류 단계의 교정 trace만 최적화 단위로 삼는다.
9. **HSFT 하이퍼파라미터**: 8×A100 40GB, 4 에포크, batch=8, grad accumulation=16, lr=2e-5, AdamW + cosine, warmup 0.02, flash-attention.
10. **Cross-DPO 하이퍼파라미터**: 8 에포크, global batch=128, lr=1e-6, AdamW + cosine, warmup 0.05.
11. **추론 시 절차**: 학생 모델이 초기 계층적 사고 추론 → 자체 verification 단계에서 각 스텝을 검증 → 오류 발견 시 `<Cause>`/`<Correction>` 형식으로 자가 교정 후 최종 답 재출력.
12. **일반화 검증**: 동일 파이프라인을 Qwen2.5-Math-7B, DeepSeekMath-7B, Llama3.1-8B 세 아키텍처에 독립 적용해 교차 검증.

---

## Key Contribution

1. **2단계 교사-학생 분리 증류 프레임워크 SuperCorrect**: 추론 능력(HSFT)과 교정 능력(Cross-DPO)을 명확히 분리해 각각 최적화함으로써 기존 단일 단계 SFT/DPO 한계를 돌파.
2. **Hierarchical Thought Template**: 고수준 일반화 전략(`<Generalized>`)과 단계별 세부 주석(`<Key>`)을 결합한 XML 기반 thought 형식을 제안 — CoT/BoT 대비 더 깊고 정보량 많은 추론 가이드 제공.
3. **Cross-model Collaborative DPO (Thought-level Reward)**: 교사의 오류 단계 교정 trace를 chosen, 학생의 self-correction을 rejected로 두는 새로운 preference 최적화 — 오류 단계 단위를 기본 최적화 유닛으로 삼아 Step-DPO 대비 7% 정확도 개선.
4. **고품질 데이터셋 2종 공개**: 100K HSFT 데이터셋 + 10K thought-level preference 데이터셋을 ground-truth grounded 프롬프트로 구축.
5. **Inspector LLM 품질 보증 메커니즘**: 교사 생성 correction trace를 o1-preview로 재검증해 데이터 노이즈 제거 — 특히 난이도 높은 데이터셋에서 큰 향상.
6. **3개 SOTA 7B 모델 공개**: SuperCorrect-Qwen/DeepSeek/Llama-7B — 7B급 MATH SOTA 70.2% 달성, 70B Llama3-Instruct 초과.
7. **Thought bottleneck 해소 실증**: 원래 약했던 geometry/number theory 등 어려운 주제에서 더 큰 향상을 관찰해 "새로운 스킬 획득" 효과 입증.

---

## Experiment

- **베이스 모델**: Qwen2.5-Math-7B-Instruct, DeepSeekMath-7B-Instruct, Meta-Llama3.1-8B-Instruct.
- **평가 벤치마크**: MATH(5,000 test, 5 난이도, 7 주제), GSM8K — lm-evaluation-harness로 CoT 정확도 측정.
- **메인 결과 (MATH / GSM8K)**: SuperCorrect-Qwen-7B **70.2% / 89.5%** (Qwen2.5-Math 기준 55.1%/83.2% 대비 **+15.1%** / +6.3%), SuperCorrect-DeepSeek-7B **54.6% / 88.2%** (기준 46.8%/82.9% 대비 +7.8% / +5.3%), SuperCorrect-Llama-8B **58.2% / 89.7%** (기준 51.9%/84.5% 대비 +6.3% / +5.2%).
- **대형 모델 비교**: Llama3-70B-Instruct(50.4% / 93.0%)보다 MATH에서 +19.8% 우위, GPT-4-1106(64.3%)·Gemini-1.5-Pro(67.7%) 초과, GPT-4o-mini에 근접.
- **Ablation (Qwen 기반)**: Base 55.1% → Base+일반 SFT 57.4% → Base+HSFT **62.4%**(+5.0) → HSFT+Reflexion 63.1% → HSFT+Cross-DPO **70.2%**(+7.1, Reflexion 대비 +7.1%).
- **DeepSeek base**: 46.8 → 49.2(SFT) → 50.9(HSFT) → 51.2(Reflexion) → **54.6**(Cross-DPO).
- **Llama3.1 base**: 51.9 → 53.7 → 55.4 → 56.7 → **58.2**.
- **교정 능력 정량화 (500 error samples, o1-preview judger)**: Qwen+HSFT locate 0.43 / correct 0.12 → +Cross-DPO **locate 0.67 / correct 0.46**; DeepSeek 0.23/0.07 → 0.42/0.23; Llama 0.31/0.08 → 0.49/0.27.
- **Self-correction 효과**: SuperCorrect는 초기 추론 후 자가 교정으로 정확도 +5~6% 추가 향상, 반면 다른 LLM은 정확도가 감소하는 경우도 발생.
- **Inspector LLM 효과**: GPT-4o-mini 교사 MATH 92.4%→98.8%, GaoKao 89.6%→96.2%; o1-mini 교사 MATH 98.2%→99.6%.
- **안정성 분석**: MATH level-5 300문제 256회 반복 측정 — base 대비 평균 정확도 상승 + 분산 감소.
- **Prompt style ablation (Qwen, MATH)**: CoT 57.4 → CoT+Hierarchical(No Gen) 59.7 → CoT+H(With Gen) 60.8 → Ours(Not XML) 61.8 → Ours(XML) **62.4**.
- **Step-DPO 비교**: 동일 문제(factors of 34 or multiples of 7)에서 Step-DPO는 일부 multiple(56) 누락해 오답, Cross-DPO는 14/56/91 정확 식별해 정답 도달.

---

## Limitation

교사 모델 품질에 강하게 의존한다 — o1-mini/GPT-4o 등 SOTA API 모델이 없다면 100K HSFT + 10K DPO 데이터 구축 자체가 불가능하며, 그 수준의 thought template이 생성되지 않는다.
수학 추론에 특화된 설계로, code·일반 상식·multi-hop QA 등 다른 추론 도메인으로의 전이 가능성은 본 논문에서 검증되지 않았다.
데이터 구축 비용이 크다 — 100K 문제를 o1-mini로 hierarchical XML로 변환하고, 추가로 20K 오답에 대해 교사 correction trace + Inspector 검수까지 수행해야 한다.
하드웨어 요구가 높다 — 8×A100 40GB에서 HSFT 4 에포크 + Cross-DPO 8 에포크의 다단계 학습이 필요하다.
Inspector LLM(o1-preview)조차 MATH에서 98.8~99.6%, GaoKao 97.5~98.7%로 완벽하지 않아 잔여 노이즈가 학습에 유입될 수 있다.
오류 단계를 찾는 교정 정확도가 최고 모델(Qwen+Cross-DPO)에서도 locate 0.67 / correct 0.46로 절대값이 낮아, 완전한 self-correction 능력에는 도달하지 못했다.
프레임워크가 7B 규모로만 검증되었고, 저자들이 직접 밝힌 바와 같이 더 큰 모델(70B+)과 더 복잡한 데이터셋으로의 일반화는 향후 과제로 남아 있다.
추가로, HSFT/DPO 양 단계 모두 고정된 XML 프롬프트 포맷에 의존하므로 프롬프트 변경 시 성능이 감쇠할 수 있다.

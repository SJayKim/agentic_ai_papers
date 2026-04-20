# Can LLMs Correct Themselves? A Benchmark of Self-Correction in LLMs

> **논문 정보**: Guiyao Tie, Zenghui Yuan, Zeli Zhao, Chaoran Hu 외 (HUST, Griffith University, Squirrel Ai, SJTU, Lehigh University)
> **arXiv**: 2510.16062 (2025.10, NeurIPS 2025 Datasets and Benchmarks Track)
> **코드**: https://correctbench.github.io/

---

## Problem

대형 언어 모델(LLM)의 자기 교정(self-correction)은 추론 성능을 높이는 핵심 구성 요소로 부상했으나, 제안된 방법들의 효과를 통합적으로 비교한 연구는 부재하다.

RCI, Self-Refine, CoVe, Reflexion, RARR, CRITIC, RATT, DCoT, SCORE, SuperCorrect 등 다수의 교정 기법이 난립하며, 서로 다른 태스크·데이터셋·모델에서 보고되어 상호 비교가 불가능하다.

2023년 Huang 등이 제기한 "LLMs cannot self-correct reasoning yet"이라는 회의론에 대해, 후속 연구들이 외부 도구 결합이나 파인튜닝을 통해 반박을 시도했지만, 이들을 동일 조건에서 검증한 사례가 없다.

특히 o1, DeepSeek-R1과 같이 내장 교정 메커니즘을 가진 추론 LLM에 추가 교정을 적용했을 때의 한계 효과(marginal benefit)가 정량화되지 않았다.

또한 복잡한 교정 프레임워크가 단순 CoT 베이스라인 대비 실질적 이득을 주는가, 아니면 연산 비용만 증가시키는가에 대한 trade-off 분석이 부족하다.

결과적으로 "LLM이 진정으로 스스로 교정할 수 있는가?"라는 본질적 질문에 답할 포괄적·재현 가능한 벤치마크가 필요하다.

---

## Motivation

저자들은 Kamoi 등(TACL 2024)의 self-correction 서베이를 토대로, 교정 방법을 내재적(Intrinsic)·외부(External)·파인튜닝(Fine-tuned)의 3 범주로 구조화하여 공정한 비교 축을 설정한다.

상식 추론(HotpotQA, CS-QA, GPQA), 수학 추론(GSM8K, AQUA, MATH), 코드 생성(HumanEval)의 7개 서브태스크를 포함시켜 난이도·도메인 다양성을 확보한다.

11개의 대표 LLM — 오픈소스 명령어 모델(LLaMA 3.1-8B/70B, Qwen 2.5-7B/72B), 클로즈드소스(GPT-3.5, GPT-4o, Claude 3.5-Sonnet), 추론 특화(QWQ-32B, DeepSeek-V3/R1, o3-mini) — 를 동일 프로토콜 하에 평가한다.

기존 벤치마크(CriticBench, VISCO, Beyond Correctness)가 단일 모달리티나 critique 능력에만 초점을 맞춘 것과 달리, 본 연구는 accuracy–efficiency 축을 동시에 다룬다.

Mixture Framework를 통해 서로 다른 교정 방법을 순차 결합했을 때의 시너지와 오버헤드를 측정함으로써, 단순 합산이 아닌 동적 파이프라인 설계의 근거를 제공하고자 한다.

이러한 설계를 통해 실무에서 "어떤 교정을 어떤 모델·태스크에 적용해야 비용 대비 효율적인가"라는 질문에 데이터 기반 가이드라인을 제시하는 것이 핵심 동기이다.

---

## Method

1. **3차원 평가 프레임워크**: Task Scenario × Self-Correction Type × LLM Type의 직교 축을 정의하여 11개 방법 × 11개 LLM × 7개 서브데이터셋을 일관 평가한다.

2. **Iterative Self-Correction Paradigm**: 초기 응답 r_0 = M(q, p_0) 이후 k회차에서 p_k = p_{k-1} ∪ r_{k-1}, r_k = M(q, p_k) 형태로 이전 응답을 프롬프트에 포함시켜 K번 반복 정제하며, 최종 r_K를 "교정된 응답"으로 채택한다.

3. **S1 Intrinsic Correction**: 외부 도구 없이 내부 지식만으로 자기 재평가를 수행하는 RCI(Kim 2023), Self-Refine(Madaan 2023), CoVe(Dhuliawala 2023), Reflexion-v1(Shinn 2023)을 포함한다.

4. **S2 External Correction**: 검색엔진·지식베이스·코드 실행기 등 외부 자원을 피드백 루프에 결합하는 Reflexion-v2, RARR(Gao 2022), RATT(Zhang 2024), CRITIC(Gou 2023)을 사용한다.

5. **S3 Fine-tuned Correction**: 교정 능력을 목표로 사전 학습된 모델을 사용하는 DCoT(Puerto 2024, LLaMA2-7B-hf), SCORE(Zhang 2024, Gemma-7B-it/LLaMA2-13B-chat), SuperCorrect(Yang 2024, Qwen2.5-Math-7B-Instruct)를 별도 트랙으로 분리 평가한다.

6. **Mixture Framework**: 한 방법의 출력이 다음 방법의 입력이 되는 동적 파이프라인 구성으로, F1=Base→S1→S2, F2=Base→S2→S1의 두 대표 구성을 GPQA/MATH에서 검증한다.

7. **데이터셋 구축**: CorrectBench-base(7개 서브 3,825 QA 쌍)와 교정 특화 선별 데이터 CorrectBench-test(각 데이터셋당 100개 랜덤 샘플에서 아웃라이어 제거)의 2종을 공개한다.

8. **Baseline 설정**: 단순 직접 프롬프트 'Base'와 Chain-of-Thought(CoT)의 두 비교 기준을 도입해, 복잡 교정 프레임워크의 실질 이득을 측정한다.

9. **LLM Type 구분**: M1 Instruction-based(오픈/클로즈드 소스 7종)와 M2 Reasoning(QWQ-32B, DeepSeek-V3/R1, o3-mini)로 나누어 내장 교정 메커니즘 유무에 따른 효과 차이를 분석한다.

10. **평가 지표**: 태스크별로 T1 accuracy, T2 solve rate, T3 pass@k를 사용하고, 모호/불완전 응답에는 human evaluation과 GPT-4o 기반 LLM-as-a-Judge를 병용한다.

11. **비용 측정**: Avg. Tokens, API Calls, Search Tokens(%), Accuracy를 함께 기록하고 Efficiency Rank = Accuracy / (Token Count × API Calls)로 방법별 cost–accuracy trade-off를 수치화한다.

12. **Correction/Misjudgment 분석**: 정답/오답 분할 데이터에서 CR(오답을 맞게 교정한 비율)과 MR(정답을 잘못 뒤집은 비율)을 별도 계산해 교정의 품질을 검증한다.

13. **Failure Mode Taxonomy**: GPQA 250 샘플·MATH 500 샘플에서 Logical Oversight, Factual Inaccuracy, Over-Reliance on Tools, Ambiguous Output, Contextual Misunderstanding, Computational Error, Other의 7 범주를 정의해 실패 원인을 분류한다.

14. **Adaptive Correction Controller 제안**: Failure 유형에 따라 S1/S2를 동적으로 라우팅하는 메타 컨트롤러 방향성을 Future Work로 제시한다.

---

## Key Contribution

1. **최초의 통합 자기 교정 벤치마크**: 내재적·외부·파인튜닝 3범주를 하나의 프레임워크에서 교차 평가하며, 11 방법 × 11 LLM × 7 태스크 규모로 재현 가능한 플랫폼을 제공한다.

2. **두 개의 공개 데이터셋**: CorrectBench-base(3,825 QA)와 CorrectBench-test(교정 특화 선별)를 통해 상식/수학/코드 도메인의 다양한 오류 유형을 포괄한다.

3. **추론 LLM의 교정 한계 규명**: DeepSeek-V3/R1, o3-mini가 Base만으로도 top-1/2 성능을 달성하며 추가 교정의 한계 이득이 매우 제한적임을 정량적으로 입증한다.

4. **CoT 베이스라인 재평가**: 단순 CoT가 많은 복잡 교정 방법과 동등하거나 우월한 accuracy–efficiency 균형을 달성함을 실증하여, "복잡=우수"의 통념을 반박한다.

5. **Mixture 시너지 vs 비용 trade-off 정량화**: S1+S2 순차 결합이 GPQA·MATH에서 추가 개선을 가져오지만 연산 비용이 2~3배 증가함을 Efficiency Rank로 수치화한다.

6. **실패 모드 분류 체계**: Logical Oversight 32.9%, Factual Inaccuracy 22.0% 등 7 범주의 실패 분포를 제시하고, 오류 유형별로 S1/S2 전략을 매핑하는 근거를 마련한다.

7. **실용적 가이드라인**: 태스크 복잡도·모델 규모·교정 비용에 따라 S1·S2·S3·Mixture 중 무엇을 선택해야 하는지에 대한 실무적 권고를 RQ1-3 프레임으로 정리한다.

---

## Experiment

- **평가 규모**: CorrectBench-test 기준 각 데이터셋당 100 샘플 선별, 11개 LLM × 11개 교정 방법 × 7개 태스크 조합을 실험한다.

- **S1 Intrinsic 주요 결과(11 LLM 평균)**: Self-Refine이 최강으로 GPQA +22.13%, AQUA +8.23%, MATH +6.65%, HotpotQA +4.73% 개선. CoVe는 GPQA +18.85%, AQUA +9.89%, HumanEval +4.25%.

- **Reflexion-v1 실패**: 외부 도구 결합 본래 설계에서 도구를 제거하자 GSM8K -18.82%, AQUA -12.90%, HotpotQA -11.24%, CS-QA -16.07%의 대규모 성능 하락이 관측된다.

- **S2 External 주요 결과**: Reflexion-v2(외부 피드백 포함) HotpotQA +7.22%, MATH +6.24%, AQUA +7.00%. RARR은 GPQA +18.26%, MATH +7.66%, HumanEval +4.64%로 안정적이다.

- **CRITIC 한계**: GSM8K -9.00% 하락 관측. 수학 도메인에서 도구 피드백이 오히려 노이즈로 작용하는 사례 확인.

- **전체 평균(S1+S2)**: GPQA +12.72%, AQUA +7.24%, MATH +5.03% 개선. 반면 GSM8K는 -1.42%로 이미 높은 baseline(86.46%)에서 추가 개선이 어려움을 시사한다.

- **CoT 베이스라인**: HotpotQA +2.53%, GSM8K +5.50%로 다수의 S1 방법과 동등 또는 우위. 단, HumanEval -12.61%로 코드 태스크에는 부적합하다.

- **S3 Fine-tuned 결과**: SuperCorrect(Qwen2.5-Math-7B-Instruct)가 GSM8K +27.55%, MATH +28.45%, CS-QA +14.85%, HumanEval +13.05%로 최고 성능. 반면 DCoT(LLaMA2-7B-hf)는 GSM8K -15.55%로 일관성 결여.

- **Mixture 효과**: F1(Base→S1→S2)과 F2(Base→S2→S1) 구성에서 GPQA·MATH 모두 단일 방법 대비 추가 개선 확인. S2 경로가 S1보다 일관된 이득.

- **Resource Cost(MATH 150 샘플)**: Base=791토큰/1 API/68.5% 정확도(효율 0.0866 최상), RARR=533토큰/2 API/76.3%(효율 0.0716), RATT=2185토큰/3 API/78.7%(효율 0.0120), Reflexion-v1=1460토큰/3.5 API/72.8%(효율 0.0143).

- **Response Time(LLaMA3.1-70B, GPT-4o, DeepSeek-V3 평균)**: Base/CoT가 최단, RATT·Reflexion 계열이 최장 (최대 ~400초). DeepSeek-V3는 내장 교정으로 인해 instruction 모델보다 전반적으로 긴 실행 시간 소요.

- **Correction/Misjudgment(Claude 3.5-Sonnet)**: CoVe CR=40.8%, MR=7.5%; RARR CR=47.1%, MR=4.5%. 교정 성공률은 높고 오판단율은 낮은 수준.

- **Reasoning LLM Baseline(Table 5)**: DeepSeek-V3가 HotpotQA 89.29%, CS-QA 83.35%, GSM8K 95.12%, MATH 85.02%, HumanEval 91.67%로 대부분 top-1/2. DeepSeek-R1은 GPQA 41.15%, AQUA 80.23%로 최고. 이러한 높은 baseline이 추가 교정 여지를 제한한다.

- **Failure Mode 분포(GPQA 250 + MATH 500)**: Logical Oversight 32.9%, Factual Inaccuracy 22.0%, Over-Reliance on Tools 14.6%, Ambiguous Output 14.2%, Contextual Misunderstanding 10.8%, Computational Error 3.5%, Other 2.0%.

- **RQ 결론**: (RQ1) S1·S2 모두 복잡 추론 태스크에서 유의미한 개선 제공, (RQ2) Mixture는 정확도↑·효율↓의 명확한 trade-off, (RQ3) Reasoning LLM은 내장 메커니즘으로 인해 추가 교정 이득이 미미하다.

---

## Limitation

저자 언급: 파인튜닝 기반 교정(S3)은 학습 비용과 데이터 의존성이 높아 범용성이 제한되며, 특정 도메인(수학 등)에만 효과가 집중된다.

저자 언급: 추론 LLM(DeepSeek-V3/R1, o3-mini)의 내장 교정으로 인해 기존 교정 방법의 추가 이득이 소멸하는 "performance ceiling" 문제가 미해결 상태이다.

저자 언급: Mixture 전략의 연산 오버헤드가 2~3배 증가하여 실시간·온디바이스 시나리오에서 적용이 어렵다.

독자 관점: Mixture가 순차 파이프라인(F1, F2)만 다루며, 병렬 앙상블·투표·조건부 라우팅 같은 구조는 탐구되지 않았다.

독자 관점: 벤치마크가 영어 QA에 한정되어, 다국어·다문화 상식 교정 능력에 대한 일반화가 검증되지 않았다.

독자 관점: LLM-as-a-Judge(GPT-4o) 의존이 남아 있어, 평가자 편향과 ambiguous 응답에서의 일관성 문제가 잔존한다.

독자 관점: Adaptive Correction Controller가 Future Work로 제시되었을 뿐 구현·검증되지 않아, 실패 유형별 최적 라우팅의 실효성은 미지수이다.

독자 관점: CorrectBench-test의 샘플 수가 데이터셋당 100개로 제한되어, 드문 오류 유형에 대한 통계적 신뢰도가 낮을 수 있다.

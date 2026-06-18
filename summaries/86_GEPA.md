# 86. GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning

> 📄 **저자**: Lakshya A Agrawal, Shangyin Tan, Dilara Soylu, Noah Ziems, Rishi Khare, Krista Opsahl-Ong, Arnav Singhvi, Herumb Shandilya, Michael J. Ryan, Meng Jiang, Christopher Potts, Koushik Sen, Alexandros G. Dimakis, Ion Stoica, Dan Klein, Matei Zaharia, Omar Khattab
> 📚 **학회/발표 기관**: arXiv preprint
> 📅 **발표 날짜**: 2025.07
> 🔗 **arXiv**: https://arxiv.org/abs/2507.19457
> 💻 **코드**: https://github.com/gepa-ai/gepa

---

## Problem

LLM 기반 에이전트/컴파운드 시스템을 다운스트림 태스크에 적응시키는 표준 접근인 RLVR(예: GRPO)은 task별로 수만~수십만 rollout을 필요로 하며, 최근 GRPO 활용 연구들은 보통 수십만 rollout 단위의 학습 비용을 요구한다.
이는 각 rollout이 정책 그래디언트 추정을 위한 sparse한 scalar reward 하나로 collapse되어, rollout이 담고 있는 모듈별 추론 사슬·도구 호출·컴파일러 메시지 등 자연어 신호 대부분이 버려지기 때문이다.
값비싼 tool call이 포함되거나, 추론 예산이 제한되거나, 폐쇄 모델(GPT-4.1, Claude 등)이라 weight 학습 자체가 불가능한 실제 배포 환경에서는 이 sample-inefficiency가 곧장 비용·시간 병목으로 이어진다.
기존 prompt optimizer(MIPROv2, TextGrad, Trace 등)는 weight 학습을 피하지만, 대부분 글로벌 scalar reward에 의존해 모듈별 책임 귀속(credit assignment)이 약하거나, greedy/beam search로 candidate를 고르다 local optimum에 빠진다.
즉 "비싼 rollout 1회에서 최대한 많은 학습 신호를 어떻게 짜낼 것인가"라는 sample-efficient compound system 최적화 문제가 해결되지 않은 상태다.

---

## Motivation

저자들의 핵심 관찰은, 정교한 LLM 시스템에서 나오는 rollout은 본질적으로 직렬화 가능한 자연어 trace(각 모듈 instruction, reasoning chain, tool call/output, 컴파일러 에러 등 evaluation trace 포함)라는 점이다.
이 trace는 강력한 언어 prior를 가진 LLM이 그대로 읽고 진단할 수 있는 형태인데, RL은 이 풍부한 신호를 단일 scalar로 압축해 버린다.
대신 LLM에게 trace + 결과 점수 + 텍스트 피드백을 보여주고 자연어로 reflect하게 하면, 어느 모듈의 어떤 결정이 실패를 유발했는지 implicit credit assignment가 가능하다.
또한 항상 "최고 점수" 후보만 evolve하면 한 전략에 갇혀 budget을 소진하므로, 인스턴스별 Pareto front를 유지해 "각자 다른 문제를 잘 푸는 winning 전략들"을 모두 보존하면 다양성을 잃지 않으면서 local optimum을 탈출할 수 있다.
이는 진화 알고리즘의 quality-diversity 패러다임(MAP-Elites/Mouret & Clune 2015)을 prompt 공간에 옮겨온 관점이고, RL과 달리 weight를 건드리지 않으므로 폐쇄 모델에도 즉시 적용 가능하다.

---

## Method

GEPA(Genetic-Pareto)는 compound AI system Φ = (M, C, X, Y) — 모듈 집합 M, 컨트롤 플로우 C, 입출력 스키마 — 에 대해 prompts Π_Φ만 진화시키고 weights Θ_Φ는 고정한다. 입력은 시스템 Φ, 학습셋 D_train, metric μ, feedback function μ_f, rollout budget B다.

1. **초기화 및 Pareto split**: D_train을 D_feedback(학습 신호용)과 D_pareto(검증·candidate 선택용, 크기 n_pareto)로 분할한다. Candidate pool P를 base system 1개로 시작하고, D_pareto 전 인스턴스에 대한 점수 매트릭스 S를 기록한다.
2. **Pareto-based Candidate Selection (Algorithm 2)**: 각 학습 인스턴스 i마다 가장 높은 점수를 낸 candidate 집합 P*[i]를 만들고, 다른 candidate에게 strictly dominated되는 후보를 제거해 Pareto front를 구성한다. 그 후 "인스턴스 몇 개에서 best인지"에 비례하는 확률로 stochastic하게 다음 evolve 대상 후보를 뽑는다. 글로벌 best 단일 선택과 달리, "winning strategy를 가진 다수 후보"를 모두 살려둔다.
3. **Module 선택**: 시스템 Φ_k 안의 모듈 |M|개 중 하나를 round-robin 정책으로 골라 이번 iteration에서 수정할 대상으로 정한다 — compound system에서의 모듈 수준 credit assignment의 한 축.
4. **Reflective Prompt Mutation**: 선택된 candidate를 D_feedback에서 샘플한 minibatch(크기 b)에 실행하고, 모듈의 입출력·reasoning trace를 수집한다. feedback function μ_f는 scalar 점수뿐 아니라 compiler error, failed rubric, 평가자 코멘트 등 텍스트 피드백(feedback_text)도 반환한다. Reflection LM은 (현 prompt, trajectory, 점수, feedback_text)를 입력받아 자연어로 성공/실패 원인을 모듈 요소에 귀속시키고 새 instruction π′_j를 제안한다.
5. **Accept/Reject**: 갱신된 후보 Φ′를 minibatch에서 재평가해 평균 점수 σ′ > σ면 P에 추가하고 D_pareto 전체에서 점수를 채워 매트릭스 S를 확장한다. 개선이 없으면 폐기 — minibatch 게이팅으로 "나쁜 후보의 전체 검증 비용"을 회피.
6. **System-Aware Merge (crossover)**: 두 candidate를 모듈 단위로 병합한다. 한 lineage에서 모듈 A만 진화하고 다른 lineage에서 모듈 B만 진화했다면, 각 lineage의 best 버전을 모듈별로 골라 결합해 새 candidate를 만든다. ancestry 정보로 "서로 보완적인 모듈 진화 경로"를 식별.
7. **Evaluation traces as diagnostic signals**: μ_f는 실행 trace뿐 아니라 evaluator가 점수 산출 전 만들어내는 텍스트(컴파일·실행 로그, hop별 evaluator 코멘트, human-written 설명 등)도 모듈별로 reflection LM에 전달한다.
8. **Budget 관리 및 반환**: budget B가 소진될 때까지 위 루프를 반복하고, D_pareto 평균 점수가 가장 높은 후보 Φ*를 반환한다. RL과 달리 어떤 weight도 업데이트하지 않으며 폐쇄 모델에도 그대로 적용된다.

---

## Key Contribution

1. **Reflective prompt evolution 프레임워크 정식화**: rollout의 자연어 trace + evaluation trace를 reflection LM에 통째로 넘기는 μ_f 인터페이스를 제안해, scalar reward만으로 잃어버리던 모듈별 학습 신호를 prompt 업데이트에 직접 반영한다.
2. **Pareto-based candidate selection**: 각 학습 인스턴스별 best-set의 union을 candidate pool로 유지하고 인스턴스 wins 빈도에 비례한 확률로 샘플링해, greedy/beam search가 빠지는 local optimum을 회피하면서도 search tree를 발산시키지 않는다.
3. **Module-level credit assignment without weight updates**: round-robin 모듈 선택 + reflection 기반 책임 귀속으로 compound system 전체가 아닌 "책임 있는 모듈"만 수정해, RL이 모듈에 무관하게 모든 weight를 갱신하는 비효율을 제거한다.
4. **System-aware Merge (crossover)**: 서로 다른 모듈을 진화시킨 lineage들을 모듈 단위로 병합하는 진화 연산을 도입해 추가 +2~5% 성능을 끌어낸다.
5. **광범위한 실증**: 4개 오픈/폐쇄 모델 × 6개 태스크에서 GRPO 대비 평균 +6%, 최대 +20% 성능을 35× 적은 rollout으로 달성하고 MIPROv2 대비 aggregate 이득을 2배 이상으로 늘렸으며, 추가로 inference-time search(NPUEval, KernelBench) 및 adversarial prompt search(AIME pass@1을 76%→10%로 붕괴)에도 동일 알고리즘을 적용 가능함을 보였다.

---

## Experiment & Results

**벤치마크**: 6개 태스크 — HotpotQA(multi-hop QA), IFBench(instruction following), HoVer(retrieval-augmented verification), PUPA(privacy-preserving delegation), AIME-2025(수학), LiveBench-Math.
**모델**: Qwen3 8B(open) + GPT-4.1 Mini(closed).
**비교**: GRPO(24,000 rollouts, LoRA 및 full finetune), MIPROv2, MIPROv2-No-Demos, TextGrad, Trace(OptoPrime).

**Qwen3 8B (Table 1)**: Baseline aggregate 45.23 → GRPO 48.91(+3.68) → MIPROv2 47.84(+2.61) → **GEPA 54.85(+9.62)**, GEPA+Merge 52.40(+7.17). 개별로 HotpotQA 42.33 → GEPA 62.33 vs GRPO 43.33 (+19.0pp over GRPO), IFBench 36.90 → GEPA 38.61 vs GRPO 35.88, HoVer 35.33 → GEPA 52.33 vs GRPO 38.67(+13.66pp), PUPA 80.82 → GEPA 91.85 vs GRPO 86.66 (+5.19pp).
**Rollout 효율**: GEPA는 HotpotQA 6,871, IFBench 3,593, HoVer 7,051, PUPA 2,426, AIME 1,839, LiveBench-Math 1,839 rollouts만 사용 vs GRPO 24,000 — 최대 35× 적음. IFBench에선 단 678 rollouts만으로 38.61%에 도달해 GRPO 24k rollouts의 35.88%를 추월. Train rollout만 계산하면 79~737회로 GRPO 최고 validation을 따라잡았고, 일부 태스크는 6~179 train rollouts로 충분 — 최대 78× 효율.

**GPT-4.1 Mini (Table 2)**: Baseline 53.03 → Trace 56.30(+3.27), MIPROv2-No-Demos 57.14(+4.11), MIPROv2 58.67(+5.64), TextGrad 59.14(+6.11), **GEPA 65.22(+12.19)**, GEPA+Merge 66.36(+13.33). HotpotQA에서는 38.00 → 69.00, PUPA 78.57 → 96.46, AIME-2025 49.33 → 59.33.
**Cross-model transfer**: Qwen3-8B로 최적화한 prompt를 GPT-4.1-Mini로 그대로 평가 시 +9.00% 향상 — 직접 GPT에서 최적화한 MIPROv2(+5.64%)/TextGrad(+6.11%)/Trace(+3.27%)를 모두 능가.

**Ablation (Table 3, Qwen3 8B)**: SelectBestCandidate +6.05, BeamSearch(N=4) +5.11 vs **GEPA Pareto +12.44** — 동일 evolution harness에서 selection 전략만 바꿔도 7%p 차이. **Prompt 길이**: GEPA prompt는 MIPROv2 대비 최대 9.2× 짧음.

**Extended applications**: NPUEval(AMD XDNA2 kernel)에서 Sequential10+GPT-4o 4.25% → +RAG 16.33% → +MIPROv2 19.03% → **GEPA 30.52% (best kernel 70%, single prompt 26.85%)**. KernelBench fast_1 점수 ~0%→20%+. Adversarial: AIME-2025 pass@1 76% → 10%(GPT-5 Mini) — 단일 universal adversarial prefix만으로 -66pp.

---

## Limitation

저자가 밝힌 한계: GEPA+Merge의 mutation/crossover budget 배분과 invocation 타이밍에 대한 hyperparameter가 모델별로 민감하다 — GPT-4.1 Mini에선 일관된 이득이지만 Qwen3 8B에선 4개 태스크 중 1개에서만 이득이고 IFBench에선 38.61 → 28.23으로 -10pp 역효과.
또한 전체 budget의 대부분이 candidate 선택용 D_pareto 검증에 소모되어, 실제 학습 신호용 train rollout 비중은 작다 — adaptive validation subset 탐색을 future work로 남김.
독자 관점 한계: (1) reflection LM 자체가 강력해야 한다는 의존성 — 약한 reflection LM에선 module-level credit assignment가 noise가 될 가능성.
(2) 모듈 선택 정책이 round-robin이라 모듈 수가 많은 시스템에서 책임 모듈을 찾는 데 시간이 더 걸릴 수 있음(학습된 selector 부재).
(3) feedback function μ_f가 풍부한 텍스트 신호를 내놓는 도메인(코드 컴파일, multi-hop evaluator)에 유리한 설계로, scalar-only reward만 가능한 환경(예: human preference 단일 점수)에서는 강점이 줄어듦.
(4) weight는 고정이므로 진정한 신규 능력 습득이 아닌 prompt 공간 재배치이며, 모델 자체의 한계는 그대로 남는다.
실제 배포 시에는 reflection LM API 호출 비용도 rollout budget과 별도로 누적되므로 단순 rollout 수 비교는 총비용을 과소평가할 수 있다.

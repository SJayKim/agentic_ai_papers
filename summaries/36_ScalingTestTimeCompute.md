# Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters

> **논문 정보**: Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar (UC Berkeley, Google DeepMind), arXiv:2408.03314 (2024.08)

---

## Problem

LLM의 추론 성능을 높이는 기존 주된 접근은 사전학습 모델 크기(파라미터 수)를 키우는 것이지만, 이는 막대한 연산 비용과 데이터 요구량을 수반한다.

반면 테스트 타임에 추가 연산을 투입하여 성능을 개선하는 방법에 대한 체계적 분석이 부재하였다.

선행 연구들은 상충되는 결과를 보고해왔다: 일부는 테스트 타임 연산이 효과적이라 주장하지만, 수학 추론 같은 복잡한 과제에서는 매우 제한적이라는 부정적 결과들도 다수 존재한다.

특히 "고정된 추론 연산 예산이 주어졌을 때 LLM이 얼마나 성능을 개선할 수 있는가"라는 근본 질문에 대한 정량적 답이 없었다.

또한 다양한 테스트 타임 전략들(best-of-N, beam search, 반복 수정 등) 간의 비교 프레임워크와 최적 전략 선택 규칙이 부재하였다.

나아가 추가 FLOPs를 사전학습과 추론 중 어디에 배분해야 하는지에 대한 트레이드오프가 정량화되지 않았다.

마지막으로, 이러한 전략들의 성능이 프롬프트별로 달라진다는 관찰은 있었으나 이를 체계적으로 활용하는 방법이 제시되지 않았다.

---

## Motivation

인간은 어려운 문제를 만났을 때 더 오래 생각하여 결정의 정확성을 향상시킨다 — 저자들은 이 인지적 특성을 LLM에 이식 가능한지 탐구한다.

테스트 타임 연산을 효과적으로 활용할 수 있다면, 작은 on-device 모델이 데이터센터 급 대형 모델을 대체하여 배포 비용을 획기적으로 절감할 수 있다.

또한 추론 연산으로 모델 출력을 개선하는 능력은 인간 감독이 적은 자기 개선(self-improvement) 에이전트 파이프라인의 핵심 경로이다.

서로 상충하는 기존 결과들은 단일 "만능 전략"이 없으며, 문제 특성에 따른 적응적(adaptive) 전략 선택이 필요함을 시사한다.

저자들은 테스트 타임 연산을 (1) 제안 분포(proposal distribution) 수정과 (2) 검증기(verifier) 최적화라는 두 축으로 통합하면, 기존 방법들을 일관된 프레임워크로 분석할 수 있다고 가정한다.

MCMC 샘플링의 관점에서 테스트 타임 연산은 "간단한 제안 분포 + 스코어 함수"의 조합으로 복잡한 목표 분포를 근사하는 과정과 유사하다.

프롬프트 난이도가 최적 전략 선택의 충분 통계량(sufficient statistic) 역할을 한다면, 난이도 추정만으로 compute-optimal 전략을 실용화할 수 있다.

궁극적으로 "추론 FLOPs ↔ 사전학습 FLOPs" 교환율을 정량화함으로써, 미래 LLM 시스템 설계에서 연산 배분 의사결정의 근거를 제시할 수 있다.

---

## Method

1. **통합 프레임워크(Proposer + Verifier)**: 테스트 타임 연산을 ① 제안 분포 수정(입력 토큰 증강, 반복 수정)과 ② 검증기를 통한 후처리(best-of-N, tree search)의 두 독립 축으로 추상화한다.

2. **PRM(Process Reward Model) 학습**: 사람 라벨 기반 PRM800k 대신 Wang et al.의 Monte Carlo rollout 기반 per-step 정확성 추정을 적용하여 라벨 없이 PRM을 학습 — 각 중간 단계의 reward-to-go 가치를 예측한다.

3. **답변 집계(Aggregation)**: step-wise는 마지막 스텝의 PRM 점수를 전체 답 점수로 사용(product/min 대비 우수), inter-answer는 최종 답이 같은 솔루션들의 점수를 합산하는 "best-of-N weighted" 선택을 적용한다.

4. **세 가지 검색 알고리즘**: ① Best-of-N weighted (N개 독립 샘플링 후 PRM으로 선택), ② Beam search (각 스텝에서 N개 후보 중 상위 N/M개 유지 후 M개씩 확장, 최대 40 라운드), ③ Lookahead search (각 스텝에서 k-step 시뮬레이션을 temperature 0로 rollout하여 가치 추정; k=0이면 beam search와 동일).

5. **Lookahead 비용 공식**: 비용 = N × (k+1) 샘플로 FLOPs를 정규화하여 공정 비교를 가능하게 한다.

6. **Revision 모델 파인튜닝**: 온폴리시 64개 병렬 샘플을 포스트혹으로 다중 턴 궤적으로 재구성 — 오답 시퀀스(0~4개, 문자 edit distance로 정답과 상관도 높은 것 선택) + 정답으로 SFT 데이터 구축 후 파인튜닝한다.

7. **추론 시 반복 수정 사용**: 학습은 최대 4턴이지만 추론에서는 최근 4개로 컨텍스트를 truncate하여 더 긴 체인 생성 가능; 정답이 다시 오답으로 바뀌는 38% 회귀 문제는 sequential majority 또는 verifier로 최선 답 선택하여 해결한다.

8. **질문 난이도 추정**: 2048개 샘플의 pass@1 비율(oracle) 또는 PRM 기반 예측 점수(model-predicted)로 문제를 5개 분위(quantile) 난이도 빈으로 분류한다 — MATH의 수작업 난이도보다 모델 특화 난이도가 더 예측력이 높음.

9. **Compute-Optimal 전략 정의**: θ*_q,y*(q)(N) = argmax_θ E[1(y=y*)] — 주어진 연산 예산 N에서 문제별 최적 하이퍼파라미터를 선택하며, 난이도 빈 단위로 검증셋에서 최선 전략을 선택하고 2-fold cross-validation으로 평가한다.

10. **Sequential-Parallel 비율 탐색**: 반복 수정에서 총 예산을 순차 수정과 병렬 샘플링 사이에 분배하는 비율을 스윕하여 난이도별 최적 비율을 찾는다.

11. **FLOPs-Matched 비교 프레임워크**: 사전학습 FLOPs X = 6ND_pretrain, 추론 FLOPs Y = 2ND_inference. 파라미터 M배 확장 시 추가 FLOPs를 작은 모델의 추론에 쓸 때 가능한 배수는 M + 3(D_pretrain/D_inference)(M-1)로 계산한다.

12. **R 비율 정의**: R = D_inference/D_pretrain — 자기개선 파이프라인은 R<<1, 대규모 프로덕션은 R>>1로 극단적으로 달라지며 세 값(0.16, 0.79, 22)에서 비교한다.

---

## Key Contribution

1. **테스트 타임 연산의 통합 프레임워크 제시**: 제안 분포 수정과 검증기 최적화라는 두 축으로 기존 방법들을 MCMC 관점에서 통합하여 최초로 체계적으로 분석했다.

2. **Compute-Optimal Scaling 전략**: 프롬프트 난이도에 따라 전략을 적응적으로 선택하는 방식으로, best-of-N 대비 최대 4배 적은 연산으로 동등 이상 성능을 달성하였다(search와 revision 모두에서 확인).

3. **난이도 의존적 최적 전략 실증**: 쉬운 문제는 순차적 수정, 어려운 문제는 병렬 샘플링/PRM 트리 탐색이 유리함을 대규모 실험으로 입증 — 단일 지배적 전략이 없음을 보였다.

4. **Beam search vs Best-of-N 상충 관계 규명**: 낮은 예산·어려운 문제에서는 beam search 우세, 높은 예산·쉬운 문제에서는 PRM 과최적화로 성능 저하(overly short 솔루션, repetitive steps) 발생 — 탐색 깊이의 양날의 검을 정량화하였다.

5. **Sequential/Parallel 보완성**: 순차 수정은 지역 정제, 병렬 샘플링은 전역 탐색으로 기능이 상보적이며, 난이도별로 최적 혼합 비율이 다름을 보였다 — 쉬운 문제는 순차 전부, 어려운 문제는 균형이 최적.

6. **사전학습 vs 추론 FLOPs 교환율 정량화**: R 비율과 난이도에 따라 14배 큰 모델 대비 작은 모델 + 테스트 타임 연산이 최대 +27.8% 상대 개선을 달성하며, "더 작은 모델을 사전학습하고 추론에서 키우는" 새 패러다임의 가능성을 열었다.

7. **실용적 난이도 추정기**: Oracle 대신 PRM 예측 기반 model-predicted difficulty가 거의 동등한 성능을 보여 실제 배포 가능성을 확보하였다.

---

## Experiment

**설정**: MATH 벤치마크(Lightman et al. 스플릿: train 12k, test 500), 베이스 모델은 PaLM 2-S* (Codey) — 각각 revision과 PRM 검증 능력을 유도하기 위해 특화 파인튜닝.

**Search 결과**: 낮은 예산(2^2~2^3 생성)에서 beam search가 best-of-N을 크게 앞서지만, 예산이 2^5 이상으로 늘어나면 역전되어 best-of-N 이하로 떨어진다 — PRM 과최적화 증거.

**난이도별 Search**: level 1-2(쉬움)에서 beam search는 예산 증가 시 성능 저하, level 3-4(중간~어려움)에서 beam search가 일관되게 best-of-N 초과, level 5에서는 어떤 방법도 유의미한 개선 없음.

**Compute-Optimal Search**: 16 generations만으로 best-of-N의 64 generations에 필적 — **4배 연산 절감** 달성, oracle과 predicted 난이도 곡선이 거의 겹침.

**Revision 결과**: pass@1이 각 수정 스텝마다 점진 개선되며, 학습된 4턴을 넘어 64턴까지도 개선 지속; 38%의 정답→오답 회귀 문제는 verifier/majority 선택으로 완화.

**Sequential vs Parallel**: 동일 예산에서 순차가 병렬을 근소하게 앞서며, verifier/majority 두 선택 방식 모두에서 일관.

**Sequential-Parallel 비율**: generation budget 128에서 level 1-2는 순수 순차가 최적, level 3-4는 균형(중간) 비율이 최적 — 난이도 의존성 실증.

**Compute-Optimal Revisions**: 64 생성만으로 best-of-N의 256 생성을 능가 — 역시 **4배 연산 절감**. 높은 예산에서 병렬은 plateau하지만 compute-optimal은 계속 개선.

**FLOPs-Matched 비교 (Revisions)**: R<<1 쉬운 문제 +21.6%, 중간 +16.7%, 어려운 +5.4%; R~=1에서 +27.8%/+3.5%/-24.3%; R>>1에서 +11.8%/-11.9%/-37.2% 상대 개선.

**FLOPs-Matched 비교 (PRM Search)**: R<<1에서 +19.1%/+2.2%/+2.0%, R~=1에서 -5.6%/-35.6%/-30.6%, R>>1에서 0.0%/-35.3%/-52.9% — 어려운 문제와 높은 추론 부하에서는 사전학습이 우위.

**핵심 수치 요약**: 4× 연산 절감(양쪽 축), 14× 큰 모델 대체 가능(쉬운/중간 난이도), 38% 정답 회귀율, 2048 샘플로 난이도 추정, 5-quantile 난이도 빈, 최대 40 beam expansion 라운드, lookahead k ∈ {1, 3}.

---

## Limitation

저자 언급: 가장 어려운 문제(level 5)에서는 테스트 타임 연산 증가의 이득이 거의 없으며, 이 경우 사전학습 연산 추가가 여전히 더 효과적이다 — 추론과 사전학습이 1-대-1 교환 가능하지 않다.

저자 언급: 높은 추론 부하(R>>1) 환경에서는 혜택이 크게 감소하여 compute-optimal 전략의 유효 범위가 제한된다.

저자 언급: 난이도 추정 자체가 추가 추론 비용을 수반하며, 본 연구는 이 비용을 분석에서 제외하여 단순화하였다 — 실제 배포에서는 exploration-exploitation 균형 문제가 남는다.

독자 관점: PaLM 2-S* 단일 모델 기반 실험으로 GPT/LLaMA 등 다른 아키텍처로의 일반화가 미검증이며, PRM800k가 PaLM 2에 효과 없었던 것처럼 모델 간 전이성 문제가 존재한다.

독자 관점: MATH 벤치마크 단일 도메인에 한정되어 코드 생성, 상식 추론, 멀티모달 등 다른 과제로의 확장성 확인이 필요하다.

독자 관점: PRM 학습에 MC rollout 기반 라벨이 필요하여 사실상 상당한 사전 연산 비용이 드는 점과, revision 파인튜닝 데이터 수집 비용이 "테스트 타임 연산" 공정 비교에서 충분히 반영되지 않았다.

독자 관점: 실시간 응용에서의 latency/지연(특히 lookahead search의 rollout 오버헤드)에 대한 정량 분석이 부족하다.

독자 관점: 난이도 추정이 "완벽한 oracle" 대비 예측 기반에서 고예산 구간에서 이득 축소가 관찰되며, 더 정교한 난이도 추정기나 동적 온라인 난이도 갱신 메커니즘이 향후 과제로 남는다.

# WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning

> **논문 정보**: Zehan Qi, Xiao Liu, Iat Long Iong 외 (Tsinghua University, Zhipu AI)
> **arXiv**: 2411.02337 (2024.11) — ICLR 2025
> **코드**: https://github.com/THUDM/WebRL

---

## Problem

LLM 기반 웹 에이전트는 최근 다양한 디지털 환경에서 자율 작업 수행 가능성을 보여주었으나, 고성능 시스템은 대부분 GPT-4 같은 고비용 프로프라이어터리 API에 의존한다.
오픈소스 LLM은 의사결정 중심 데이터가 사전·사후 학습 단계에서 매우 부족하여 웹 에이전트로서의 역량이 현저히 떨어진다(Llama-3.1-8B: 4.8%, GLM-4-9B: 6.1%).
기존 오픈소스 웹 에이전트는 대부분 모방학습(SFT, Filtered BC)에 의존하여 웹 상호작용의 본질적 온라인 특성을 활용하지 못하며 지속적 개선이 불가능하다.
WebArena 같은 온라인 벤치마크에서 오픈소스 모델을 처음부터 강화학습(RL)으로 훈련하려면 세 가지 근본적 난제를 동시에 해결해야 한다.
첫째, 훈련 태스크 부족 — WebArena는 평가용 테스트셋만 제공하며, WebArena-Lite의 인간 라벨 궤적은 약 1,000개에 불과하여 강력한 웹 에이전트 훈련에 크게 모자란다.
둘째, 피드백 신호의 희소성과 비용 — 임의의 웹 태스크 성공 여부를 자동 판단할 범용 보상 함수가 없으며, 평균 10스텝에 달하는 긴 지평선 때문에 이진 성공/실패 신호는 극도로 희소하다.
셋째, 온라인 학습 시 정책 분포 이동 — 사전 정의된 훈련셋의 부재로 인해 온라인 탐색이 필수이지만, 이는 catastrophic forgetting과 성능 저하를 유발한다.
이 세 문제를 동시에 풀지 않으면 오픈 LLM 웹 에이전트의 성능을 프로프라이어터리 모델 수준까지 끌어올릴 수 없다.

---

## Motivation

저자들은 에이전트 스스로 실패 경험으로부터 새로운 훈련 태스크를 생성하고, 학습된 보상 모델로 자동 피드백을 주며, 정책 변화를 제약하는 통합 프레임워크로 세 난제를 동시에 해결할 수 있다고 주장한다.
핵심 통찰 1: 모방학습은 단일 스텝의 likelihood만 최대화하여 장기 누적 효과를 고려하지 못하고 "Scroll Down" 같은 빈도 높은 액션에 과적합(local loop)되는 반면, RL은 critic으로 각 스텝의 장기 가치를 추정함으로써 복합 다중 스텝 태스크에서 본질적으로 우월하다.
핵심 통찰 2: 기존 RL 기반 웹 에이전트(DigiRL, AgentQ)는 고정된 태스크셋으로 학습하여 에이전트의 현재 역량과 태스크 난이도가 불일치하는 경우 희소 보상 문제가 심화되고 탐색이 제한된다.
핵심 통찰 3: 실패한 태스크를 시드로 점진적으로 난이도가 상승하는 self-evolving curriculum을 구성하면, 각 단계마다 에이전트의 현재 능력에 맞는 "적당히 어려운" 태스크를 공급하여 학습 신호 밀도를 높이고 탐색 범위를 자연스럽게 확장할 수 있다.
핵심 통찰 4: RLHF에서 영감을 받은 KL-divergence 제약을 정책 업데이트에 도입하고 성공 궤적만 저장하는 adaptive replay buffer로 분포 이동과 지식 망각을 동시에 억제할 수 있다.
핵심 통찰 5: 중간 보상이 없는 이진 피드백 환경에서는 cross-entropy 목적으로 가치 네트워크를 학습하고 next-step과 final-step 추정기를 λ=0.5로 결합하면 안정적인 advantage 추정이 가능하다.
저자들은 8B/9B 크기의 오픈 모델로도 이 통합 프레임워크를 통해 GPT-4-Turbo(17.6%), GPT-4o(13.9%)를 상대적 160% 이상 능가할 수 있음을 가설로 세운다.

---

## Method

WebRL은 self-evolving 커리큘럼, ORM, KL-제약 정책 업데이트, 경험 재생 버퍼를 결합한 단계별(phase-wise) 온라인 RL 프레임워크로, 다음의 순차적 컴포넌트로 구성된다.

1. **문제 정의 (MDP 공식화)**: 웹 태스크를 유한 지평선 MDP `(S, A, R, T)`로 모델링. 상태 s는 현재 HTML + 이전 액션 이력, 액션 a는 정책 π(·|s, I)에서 샘플링, 보상은 태스크 완료 시 1, 실패/타임아웃 시 0. 최대 상호작용 T 스텝.

2. **ORM 훈련 (Outcome-Supervised Reward Model)**: LLM을 "YES"/"NO" 이진 출력으로 파인튜닝하여 롤아웃 성공 여부를 자동 판정. 입력은 [instruction I, 액션 이력, 최종 HTML] — 긴 HTML 문제 회피를 위해 최종 상태 HTML만 포함. "YES"와 "NO" 생성 확률을 비교하여 보상 1/0 결정. WebArena-Lite 훈련 데이터를 태스크 리라이팅과 변수 수정으로 증강 후 훈련.

3. **Self-Evolving 커리큘럼 — 생성 단계**: 이전 phase에서 실패한 instruction을 시드로 in-breadth evolving(WizardLM 방식) 프롬프트를 GPT-4o에 적용하여 새 태스크 생성. 유사 난이도 태스크와 복잡도 상승 태스크 두 종류를 섞어 생성.

4. **Self-Evolving 커리큘럼 — 필터링 단계**: (a) 훈련된 critic V(s_0, I)로 각 생성 태스크의 초기 상태 점수를 계산하여 [0.05, 0.75] 범위만 유지 — 너무 쉽거나 불가능한 태스크 제거, (b) GPT-4o 기반 실행 가능성 필터로 WebArena 환경에서 실현 불가능한 태스크 자동 배제.

5. **KL-제약 정책 업데이트 목적함수**: 이전 phase 정책 π_ref와 현재 정책 π_θ 간 KL 발산을 β 계수로 제약. 목적: max E[Σ(r + β·log π_ref) + β·H(π_θ)]. 최대 엔트로피 RL로 해석 시 최적 정책은 π* ∝ exp((Q* - V*)/β).

6. **손실 함수 도출**: 최적 조건 β·log(π*/π_ref) = A*(s,a,I)를 활용하여 off-policy 손실 `L(π_θ) = E_ν[(β·log(π_θ/π_ref) - A*(s,a,I))^2]`. 그래디언트는 SFT loss × (advantage - KL 제약항) 형태로, advantage > 0이면 액션 확률 증가(π_θ < π_ref일수록 증폭), advantage < 0이면 감소.

7. **가치 네트워크 훈련**: 중간 보상이 0인 이진 환경에 맞춰 cross-entropy 목적 `L(V) = -E[r·log V + (1-r)·log(1-V)]`로 V(s, I) 학습. Farebrother et al.(2024)의 분류 기반 가치 학습 채택.

8. **Advantage 추정 (GAE 변형)**: `A(s_t, a_t, I) = λ·(r + V(s_{t+1}) - V(s_t)) + (1-λ)·(r(s_T) - V(s_t))`. Next-step과 final-step 추정기를 λ=0.5로 결합하여 편향-분산 균형.

9. **경험 재생 버퍼 — 성공 궤적만 저장**: 각 phase의 성공 궤적만 버퍼에 누적 — 실패 궤적의 중간 상태 가치 추정 난제 회피.

10. **Actor Confidence 필터링**: phase i에서 이전 phase 액터로 버퍼 내 모든 액션의 perplexity 계산. Perplexity ∈ [1/0.95, 1/0.5] 범위만 훈련 데이터에 편입 — 너무 친숙한 데이터(과적합 유발)와 너무 낯선 데이터(분포 급변) 모두 배제.

11. **β 하이퍼파라미터 민감도 관리**: replay buffer 유무에 따라 β 최적값 달라짐. 버퍼 없을 때 β ≥ 1에서 과도 제약으로 성능 저하, 버퍼 사용 시 β 증가에도 안정적 성능 유지. 저자는 β=1 근처를 기본값으로 사용.

12. **훈련 절차 (Algorithm 1)**: 각 phase t에서 (1) 현재 정책 π_t로 롤아웃 수집 → (2) ORM으로 성공/실패 라벨링 → (3) 성공 궤적을 replay buffer에 추가 → (4) 실패 instruction을 시드로 다음 phase 태스크 생성·필터링 → (5) 버퍼 데이터 + 현 phase 데이터로 KL-제약 정책 업데이트 수행. 총 8 phase까지 반복.

---

## Key Contribution

1. **WebArena 최초의 체계적 온라인 RL 프레임워크**: 초기화 상태에서부터 LLM 웹 에이전트를 WebArena 온라인 환경에서 RL로 훈련시키는 최초의 엔드-투-엔드 인프라를 제시 — 태스크 생성, 보상 모델, 정책 업데이트, 경험 관리가 통합된 파이프라인.

2. **세 가지 근본 난제의 동시 해결**: 훈련 태스크 부족(self-evolving curriculum), 피드백 희소성(ORM + 난이도 조절 태스크 생성), 정책 분포 이동(KL-제약 업데이트 + 성공 궤적 replay buffer)을 단일 프레임워크로 통합 해결.

3. **강력한 오픈소스 ORM**: 프로프라이어터리 GPT-4V/GPT-4 Captioner 기반 보상 모델을 뛰어넘는 8B 규모 ORM 개발 — 테스트셋 80.8%, 롤아웃 79.4% 정확도로 GPT-4V(71.2%, 70.5%) 대비 약 10%p 우위, 완전 오픈소스 평가 파이프라인 가능.

4. **오픈소스 SOTA 달성**: Llama3.1-8B 4.8% → 42.4%, GLM-4-9B 6.1% → 43.0%로 WebArena-Lite 평균 성공률을 각각 37.6%p, 36.9%p 개선하여 GPT-4-Turbo(17.6%) 대비 상대 160%+ 향상 — 이전 오픈소스 SOTA(AutoWebGLM 18.2%) 2배 이상.

5. **스케일 확장성 검증**: Llama3.1-70B + WebRL에서 49.1% 달성(SFT 대비 +26.1%p) — 모델 크기가 커질수록 WebRL의 상대 이득도 증가함을 확인.

6. **에러 유형 분석 및 장기 태스크 강건성**: "Get Stuck Midway", "Fail to Recover" 에러 유형 감소가 가장 두드러짐. 10스텝 이상 장기 태스크에서 DigiRL 등 baseline 대비 유의한 성능 유지.

7. **Ablation을 통한 각 컴포넌트 필수성 증명**: replay buffer, KL 제약, 커리큘럼 중 어느 하나라도 제거 시 성능이 42.4%에서 20~32.7% 수준으로 급락 — 세 요소가 상호 보완적으로 기능함을 실증.

---

## Experiment

**환경 및 설정**: WebArena 기반 WebArena-Lite(Liu et al., 2024b) 사용 — 5개 웹사이트(Reddit, GitLab, CMS, Map, OneStopShop), 165개 인간 검증 테스트 케이스.
**베이스라인**: 프로프라이어터리(GPT-4-Turbo, GPT-4o, AWM+GPT-4-0613, WebPilot+GPT-4o)와 오픈소스(AutoWebGLM 6B, SFT/BC, Filtered BC, AWR, DigiRL).

**메인 결과 (Llama3.1-8B 기반)**:
- Llama3.1-Instruct-8B 초기값: 4.8%
- Llama3.1 + SFT(BC): 20.6%
- Llama3.1 + Filtered BC: 23.0%
- Llama3.1 + AWR: 28.5%
- Llama3.1 + DigiRL: 30.3%
- **Llama3.1 + WebRL: 42.4%** (DigiRL 대비 +12.1%p, 상대 40% 개선)

**GLM-4-9B 결과**:
- GLM-4-Chat 초기값: 6.1%
- GLM-4 + SFT: 22.4%, Filtered BC: 24.8%, AWR: 27.9%, DigiRL: 31.5%
- **GLM-4 + WebRL: 43.0%**

**프로프라이어터리 비교**: GPT-4-Turbo 17.6%, GPT-4o 13.9% — WebRL 8B 모델이 2.4~3.1배 성능 우위. AWM+GPT-4-0613(35.5%), WebPilot+GPT-4o(37.2%)도 상회.

**사이트별 세부 성능 (Llama3.1-8B + WebRL)**: Reddit 63.2%, Gitlab 46.7%, CMS 54.3%, Map 36.7%, OSS 31.1%. GLM-4-9B + WebRL: Reddit 57.9%, GitLab 50.0%, CMS 48.6%, Map 36.7%, OSS 37.8%.

**스케일링 실험**: Llama3.1-70B + WebRL 평균 49.1% — 동일 70B의 SFT 23.0% 대비 +26.1%p, Reddit 78.9%, Gitlab 50.0%, CMS 54.3%, Map 40.0%, OSS 44.4%로 전 사이트에서 SOTA.

**ORM 평가 (Table 3)**: 자체 8B ORM — 테스트셋 80.8%, 롤아웃 79.4%. 베이스라인: GPT-4 71.9%/71.2%, Captioner+GPT-4 72.6%/73.3%, GPT-4V 71.2%/70.5% — WebRL ORM이 약 8~10%p 우위.

**Ablation (Figure 5, Llama3.1-8B)**:
- Full WebRL: 42.4%
- w/o KL: 24.8% (-17.6%p)
- w/o replay buffer: 34.5% (-7.9%p)
- w/o KL & replay buffer: 20.0% (-22.4%p)
- w/o curriculum(CL): 32.7% (-9.7%p)

**Perplexity 필터 범위 효과 (Table 2, phase 1 SR)**: [1, ∞) 29.1%, [1, 1/0.95] 27.9%, **[1/0.95, 1/0.5] 31.5%** (최적), [1/0.5, ∞) 23.0% — 중간 난이도 데이터가 최적.

**β 민감도**: β=0.01(과소 제약) 시 성능 저하, buffer 없이 β ≥ 1이면 제약 과다로 저하되나 buffer 사용 시 큰 β에서도 안정적.

**에러 유형 분석 (Figure 3)**: WebRL은 "Get Stuck Midway" 에러를 SFT/Filtered BC 대비 절반 수준으로 감소, "Fail to Recover"와 "Stop at Wrong Page" 에러율도 최저.

**장기 태스크 성능 (Figure 4)**: 10+ 스텝 태스크에서 SFT/Filtered BC는 급락, DigiRL도 저하되지만 WebRL은 상대적으로 안정적.

**복잡도별 성능 (Figure 6)**: 요구사항 1~4개의 instruction 복잡도에서 WebRL이 전 수준에서 우위, 특히 복잡도 3~4에서 DigiRL 대비 격차 확대.

---

## Limitation

(저자 명시) 평가가 WebArena-Lite 165개 테스트 케이스에만 국한되어 일반성 검증 부족 — 실제 웹 환경의 방대한 도메인 다양성을 대표하지 못한다.
(저자 명시) 커리큘럼 태스크 생성과 실행 가능성 필터링이 GPT-4o API에 의존하여 완전 오픈소스 엔드-투-엔드 파이프라인 구현이 어렵다.
ORM은 최종 상태 HTML만 사용하여 중간 과정의 오류(부분적 성공, 부작용)를 탐지하지 못할 수 있으며, 이진 보상 특성상 학습 신호의 표현력이 제한적이다.
Self-evolving 커리큘럼의 품질은 시드 실패 태스크의 다양성과 GPT-4o 프롬프트에 민감하여, 초기 실패 패턴이 편향되면 후속 phase의 태스크 분포도 편향될 수 있다.
총 8 phase, Llama3.1-70B 훈련 등 대규모 RL 훈련에는 상당한 컴퓨팅 자원과 온라인 환경 rollout 시간이 소요되어 실용적 재현 비용이 높다.
Replay buffer의 perplexity 필터 최적 범위([1/0.95, 1/0.5])가 하이퍼파라미터로 설정되어 있으며, 모델/태스크 종속성이 체계적으로 분석되지 않았다.
WebArena는 시뮬레이션된 5개 사이트로 구성되어 있어 실제 웹의 JavaScript 동적 콘텐츠, CAPTCHA, 로그인 상태 변화 등 현실적 장벽은 평가 범위에 포함되지 않는다.
저자들의 ablation은 단일 시드 결과로 보고되어, 각 컴포넌트의 효과 크기에 대한 통계적 유의성은 추가 검증이 필요하다.

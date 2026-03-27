# WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning

> **논문 정보**: Zehan Qi, Xiao Liu, Iat Long Iong 외 (Tsinghua University, Zhipu AI)
> **arXiv**: 2411.02337 (2024.11) — ICLR 2025
> **코드**: https://github.com/THUDM/WebRL

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 웹 에이전트 온라인 학습에 세 가지 근본 문제: (1) 학습 태스크 부족 — WebArena 같은 벤치마크는 테스트셋만 제공. (2) 희소하고 비용이 큰 보상 신호 — 임의의 웹 태스크 성공 여부를 자동 판단하는 수단 부재. (3) 정책 분포 이동 — 온라인 탐색 시 catastrophic forgetting 발생. |
| **Motivation** | 에이전트 자신이 실패 시도로부터 새 학습 태스크를 자동 생성하고, ORM으로 보상을 자동 판단하며, KL-제약 정책 업데이트와 경험 재생 버퍼로 분포 이동을 제어하면, 8B~9B 오픈소스 모델도 GPT-4-Turbo를 2배 이상 능가할 수 있다. |
| **Limitation** | (저자) WebArena-Lite 단일 벤치마크에서만 평가. (독자) 자기 진화 커리큘럼이 GPT-4o 필터링에 의존하여 완전 오픈소스 파이프라인 구성이 어려움. 태스크 생성 품질이 시드 실패 패턴의 다양성에 민감. |

---

## Method

### 1. 문제 공식화
웹 태스크를 유한 지평선 MDP `(S, A, R, T)`로 모델링. 보상은 이진(완료 1 / 실패 0).

### 2. Outcome-Supervised Reward Model (ORM)
- LLM을 ORM으로 파인튜닝. 입력: [instruction, 액션 이력, 최종 HTML], 출력: "YES"/"NO" 확률
- ORM 정확도: 테스트셋 80.8%, 롤아웃 79.4% — GPT-4V(71.2%) 능가

### 3. 자기 진화 커리큘럼
- 실패한 태스크를 시드로 in-breadth evolving 방식으로 새 훈련 태스크 생성
- 2단계 필터링: (a) Critic 점수 0.05~0.75 범위만 선택 (난이도 조절), (b) GPT-4o로 실행 불가 태스크 제외
- 단계가 진행될수록 태스크 난이도가 점진적으로 상승

### 4. KL-제약 정책 업데이트
- 이전 정책 π_ref와 현재 정책 π_θ 간 KL 발산을 β 계수로 제어
- 손실: L(π_θ) = E[β·log(π_θ/π_ref) - A*(s,a,I)]²
- β=1 전후가 최적

### 5. Advantage 추정
- 가치 네트워크 V(s_t, I) 학습, GAE로 advantage 계산
- Next-step과 final-step 추정기를 λ=0.5로 결합

### 6. 경험 재생 버퍼
- 성공 궤적만 저장, 현재 액터의 perplexity 기준으로 필터링
- Perplexity [1/0.95, 1/0.5] 범위만 활용 — 너무 쉽거나 어려운 데이터 배제

---

## Key Contribution

1. **WebArena 최초 RL 인프라**: LLM 웹 에이전트를 처음부터 RL로 학습시키는 체계적 프레임워크
2. **세 가지 핵심 문제 동시 해결**: 태스크 부족 → 커리큘럼, 희소 보상 → ORM, 분포 이동 → KL+재생 버퍼
3. **오픈소스 모델의 160%+ 상대 향상**: 8B/9B 모델이 GPT-4-Turbo, GPT-4o를 크게 능가
4. **스케일 확장성**: Llama3.1-70B에 WebRL 적용 시 49.1% 달성

---

## Experiment & Results

- **벤치마크**: WebArena-Lite (165개 테스트, 5개 웹사이트)

**주요 성능 비교**:

| 모델 | 파라미터 | 평균 SR |
|------|---------|---------|
| GPT-4-Turbo | N/A | 17.6% |
| GPT-4o | N/A | 13.9% |
| AutoWebGLM | 6B | 18.2% |
| Llama3.1 + SFT | 8B | 20.6% |
| Llama3.1 + DigiRL | 8B | 30.3% |
| **Llama3.1 + WebRL** | **8B** | **42.4%** |
| **GLM-4 + WebRL** | **9B** | **43.0%** |
| **Llama3.1 + WebRL** | **70B** | **49.1%** |

**세부 사이트별** (GLM-4-9B + WebRL): Reddit 57.9%, GitLab 50.0%, CMS 48.6%, Map 36.7%

**ORM**: WebRL ORM(8B) 80.8% vs GPT-4 71.2%

**Ablation (Llama3.1-8B)**:
- Full: 42.4% / w/o KL: 24.8% / w/o replay: 20.0% / w/o curriculum: 32.7%

# WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning

> **논문 정보**: Zehan Qi, Xiao Liu, Iat Long Iong 외 (Tsinghua University, THUDM)
> **arXiv**: 2411.02337 (2024.11)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 웹 에이전트 학습에서 실패한 태스크로부터 학습 데이터를 생성하는 방법이 부재하고, 기존 RL 접근은 수동 보상 설계에 의존하며 학습 커리큘럼이 없어 오픈소스 모델의 성능이 GPT-4에 크게 뒤처진다. |
| **Motivation** | 에이전트가 실패한 시도에서 자동으로 새 학습 태스크를 생성하고, 결과 감독(outcome-supervised) 보상 모델로 스스로 진화하는 커리큘럼 RL이 가능하면, 오픈소스 모델도 폐쇄 모델을 능가할 수 있다. |
| **Limitation** | 저자 언급: WebArena-Lite에 특화된 평가. 독자 관점: 자기 진화 커리큘럼의 안정성이 태스크 분포에 민감할 수 있음. |

---

## Method

1. **자기 진화 온라인 커리큘럼**: 에이전트의 실패 시도에서 새로운 학습 태스크를 자동 생성하여 난이도를 점진적으로 높임
2. **Outcome-Supervised Reward Model (ORM)**: 에이전트 궤적의 최종 결과를 기반으로 보상을 자동 판단, 수동 보상 설계 불필요
3. **온라인 RL 학습**: Llama-3.1-8B를 지속적으로 학습시켜 웹 탐색 능력 향상

---

## Key Contribution

1. **자기 진화 커리큘럼 RL**: 실패에서 자동으로 새 태스크를 생성하는 선순환 학습 메커니즘
2. **오픈소스 모델의 비약적 향상**: Llama-3.1-8B가 GPT-4-Turbo를 초과 (42.4% vs 17.6%)

---

## Experiment & Results

- **벤치마크**: WebArena-Lite
- Llama-3.1-8B + WebRL: **42.4%** (GPT-4-Turbo 17.6% 대비 2.4배)

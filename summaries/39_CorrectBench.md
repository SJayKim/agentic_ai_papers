# Can LLMs Correct Themselves? A Benchmark of Self-Correction in LLMs

> **논문 정보**: Guiyao Tie, Zenghui Yuan, Zeli Zhao, Chaoran Hu 외 (HUST, Griffith University, Squirrel Ai, SJTU, Lehigh University)
> **arXiv**: 2510.16062 (2025.10)
> **코드**: https://correctbench.github.io/

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 다양한 자기 교정(self-correction) 방법이 제안되었지만, 이들을 통일된 프레임워크에서 체계적으로 비교 평가한 연구가 없다. "LLM이 진정으로 스스로 교정할 수 있는가?"라는 근본적 질문에 답할 포괄적 벤치마크가 부재. |
| **Motivation** | 2024년의 "Cannot Self-Correct" 회의론 이후, 외부 피드백(코드 실행기, 검색 엔진) 결합이나 파인튜닝 기반 교정이 제안되었으나, 내재적·외부·파인튜닝 교정을 교차 비교하고 효율성까지 고려한 평가가 없다. 또한 o1류 추론 LLM에 대한 추가 교정 효과도 미검증. |
| **Limitation** | 저자 언급: 파인튜닝 기반 교정(S3)의 학습 비용이 높아 모든 모델에 적용하기 어려움. 독자 관점: 교정 방법의 혼합(mixture) 실험이 순차 파이프라인으로만 제한되어, 병렬 혼합이나 앙상블 전략 미탐구. 벤치마크가 영어 태스크에 한정. |

---

## Method

1. **CorrectBench 프레임워크**: 3개 차원의 체계적 평가
   - **Task Scenario**: 상식 추론(HotpotQA, CS-QA, GPQA), 수학 추론(GSM8K, AQUA, MATH), 코드 생성(HumanEval)
   - **Self-Correction Type**: S1 내재적(RCI, Self-Refine, CoVe, Reflexion-v1), S2 외부(Reflexion-v2, RARR, RATT, CRITIC), S3 파인튜닝(DCoT, SCORE, SuperCorrect)
   - **LLM Type**: M1 명령어 기반(LLaMA 3.1-8B/70B, Qwen 2.5-7B/72B, GPT-4o, Claude 3.5 Sonnet), M2 추론(QWQ-32B, o3-mini, DeepSeek-R1, DeepSeek-V3)

2. **반복적 자기 교정 패러다임**: p_k = p_{k-1} ∪ r_{k-1}, r_k = M(q, p_k) — 이전 응답을 프롬프트에 포함하여 K회 반복 교정

3. **Mixture Framework**: 서로 다른 교정 방법을 순차적으로 연결. 한 방법의 출력이 다음 방법의 입력이 되는 동적 파이프라인

4. **데이터셋**: CorrectBench-base (7개 서브데이터셋, 3,825 QA 쌍), CorrectBench-test (교정 특화 선별 데이터)

---

## Key Contribution

1. **최초의 포괄적 자기 교정 벤치마크**: 11개 교정 방법 × 11개 LLM × 7개 태스크를 통일된 프레임워크로 비교, 내재적·외부·파인튜닝 교정을 교차 평가
2. **추론 LLM에 대한 교정 효과 분석**: o1류 모델(DeepSeek-R1, o3-mini)에 추가 교정 적용 시 제한적 개선과 높은 시간 비용을 정량화
3. **CoT 베이스라인의 재평가**: 단순 CoT가 복잡한 교정 프레임워크와 비교 가능한 정확도-효율성 균형을 달성함을 실증

---

## Experiment & Results

- **11개 LLM 평균 결과** (Baseline vs 교정 방법):

**내재적 교정 (S1)**: Self-Refine이 가장 효과적 — GPQA +22.13%, AQUA +8.23%, MATH +6.65%. Reflexion-v1은 대부분 태스크에서 성능 하락 (GSM8K -18.82%)

**외부 교정 (S2)**: Reflexion-v2(외부 피드백 포함) HotpotQA +7.22%, MATH +6.24%. RARR도 전반적으로 안정적 개선. CRITIC은 GSM8K에서 -9.00% 하락

**평균**: S1+S2 교정 후 GPQA +12.72%, AQUA +7.24%, MATH +5.03% 개선, 그러나 GSM8K -1.42% 하락

**Mixture (복합 교정)**: 정확도 추가 개선 가능하나 연산 비용 2~3배 증가

**추론 LLM (DeepSeek-R1, o3-mini)**: 추가 교정 시 개선폭이 매우 미미 (이미 내장 교정 메커니즘 보유), 시간 비용만 증가

**CoT 베이스라인**: HotpotQA +2.53%, GSM8K +5.50%로 많은 S1 방법과 동등하거나 우수, 연산 비용은 가장 낮음 — 효율성 대비 가장 실용적

# Towards Thinking-Optimal Scaling of Test-Time Compute for LLM Reasoning

> **논문 정보**: Wenkai Yang, Shuming Ma, Yankai Lin, Furu Wei (Renmin University of China, Microsoft Research)
> **arXiv**: 2502.18080 (2025.02)
> **코드**: https://github.com/RUCBM/TOPS

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | o1류 모델들이 더 긴 Chain of Thought(CoT)로 추론 토큰을 확장하면 항상 성능이 향상된다는 가정이 지배적이지만, QwQ-32B-Preview는 기반 모델 대비 훨씬 많은 토큰을 생성하면서도 성능 향상은 제한적이다. 과도한 CoT 확장이 오히려 성능을 저해할 수 있는지는 미탐구. |
| **Motivation** | 실험적으로 동일 기반 모델에서 긴 추론 경로로 학습하면 쉬운 태스크에서 오히려 성능이 하락함을 발견. 긴 CoT는 더 많은 오류 단계를 포함하며, 일부 오류+반성은 유익하지만 과도한 오류는 해로움. 태스크 난이도에 따라 최적 추론 길이가 다르므로, 모델이 스스로 적정 길이를 결정하는 전략이 필요. |
| **Limitation** | 저자 언급: 수학 도메인에 한정된 실험. 독자 관점: 최적 추론 길이의 사전 결정이 어렵고, "가장 짧은 정답 경로" 선택이 학습 데이터 내에서만 가능하여 미지 난이도 문제에서의 일반화 불확실. QwQ-32B-Preview 생성 데이터에 의존하여 교사 모델 품질에 영향 받음. |

---

## Method

1. **현상 분석: 과도한 CoT 확장의 역효과**
   - QwQ-32B-Preview를 Low/Medium/High 세 가지 추론 노력(reasoning effort)으로 프롬프팅하여 동일 문제에 대해 다른 길이의 정답 경로 생성
   - 기반 모델(Qwen2.5-32B, LLaMA3.1-8B)을 각 길이별 데이터로 파인튜닝하여 공정 비교
   - **발견**: 긴 추론 경로 학습 시 쉬운 태스크(GSM8K)에서 성능 하락, 어려운 태스크(AIME)에서만 개선. 최적 추론 노력은 난이도에 따라 다름

2. **TOPS (Thinking-Optimal Scaling) 전략**
   - **Phase 1 — Tag 모델 학습**: 소량의 시드 데이터(~1.3K 문제 × 3 길이)로 다른 추론 노력을 시스템 프롬프트로 구분하여 학습. 모델이 프롬프트에 따라 다른 길이의 추론을 수행하도록 학습
   - **Phase 2 — 최적 데이터 생성**: Tag 모델로 대규모 문제 세트에서 Low/Medium/High 각각으로 응답 생성 → 각 문제에 대해 **가장 짧은 정답 경로**를 선택하여 thinking-optimal 데이터셋 구축
   - **Phase 3 — 자기 개선**: 기반 모델을 thinking-optimal 데이터셋으로 파인튜닝

3. **반복적 자기 개선**: Phase 2-3을 반복 수행하여 점진적으로 성능 향상

---

## Key Contribution

1. **CoT 과확장의 역효과 최초 실증**: 동일 모델에서 더 긴 CoT 학습이 쉬운 태스크의 성능을 저해함을 통제된 실험으로 입증. 기존 "효율성" 관점의 overthinking 비판을 넘어 "효과성" 차원의 문제 제기
2. **TOPS 전략**: 모델이 문제별로 최적 추론 노력을 자율적으로 결정하게 하여, 효과성과 효율성을 동시에 달성하는 테스트 타임 스케일링 방법론
3. **자기 개선 기반 o1급 성능**: 증류 기반 32B 모델 중 최고 성능 달성, 교사 모델(QwQ-32B-Preview)에 필적

---

## Experiment & Results

- **기반 모델**: LLaMA3.1-8B-Instruct, Qwen2.5-32B-Instruct
- **벤치마크**: GSM8K (초등 수학), MATH500 (고등 수학), AIME2024 (수학 올림피아드)
- **비교**: QwQ-32B-Preview, DeepSeek-R1, o1-mini, 다른 증류 기반 32B 모델

**CoT 길이별 성능 (Qwen2.5-32B-Tag)**:
- GSM8K: Low(짧은) 94.5% > Medium 93.6% > High(긴) 92.8% → 짧을수록 우수
- AIME2024: Low 33.3% < Medium 36.7% < High 40.0% → 길수록 우수
- MATH500: Medium이 최적 (88.6% vs Low 87.2%, High 87.8%)

**TOPS 결과 (Qwen2.5-32B-TOPS)**:
- GSM8K: 95.1%, MATH500: 90.0%, AIME2024: 50.0%
- 기존 증류 기반 32B 모델 (Sky-T1-32B, etc.) 대비 전 벤치마크에서 최고 성능
- QwQ-32B-Preview (MATH500 90.6%, AIME2024 50.0%)와 동등 수준 달성

**반복 자기 개선**: 2회 반복으로 AIME2024에서 추가 개선, 수렴 후 안정화

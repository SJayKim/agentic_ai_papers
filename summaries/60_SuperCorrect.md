# SuperCorrect: Advancing Small LLM Reasoning with Thought Template Distillation and Self-Correction

> **논문 정보**: Ling Yang, Zhaochen Yu, Tianjun Zhang, Minkai Xu, Joseph E. Gonzalez, Bin Cui, Shuicheng Yan (PKU, Skywork AI, NUS, UC Berkeley, Stanford)
> **arXiv**: 2410.09008 (2024.10)
> **학회**: ICLR 2025
> **코드**: https://github.com/YangLing0818/SuperCorrect-llm

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 소형 LLM(7B)은 복잡한 수학적 추론에서 오류를 스스로 탐지·교정하지 못한다. 기존 reflection 기반은 외부 피드백 없이 자기 교정이 어렵고, 단순 SFT/DPO는 고수준 추론 사고 패턴과 오류 교정 능력을 동시에 전달하지 못한다. |
| **Motivation** | 대형 교사 모델의 계층적 사고 구조를 "사고 템플릿"으로 추출해 구조적으로 증류하고, 교사-학생 교차 모델 DPO로 오류 단계 탐지와 교정 능력을 강화하면 소형 모델의 추론 성능을 비약적으로 향상시킬 수 있다. |
| **Limitation** | (1) 교사 모델 품질에 강하게 의존. (2) 수학 문제에 특화되어 일반 추론/코드로의 전이 불확실. (3) 100K SFT + 10K DPO 데이터 구축에 SOTA 교사 API 비용 상당. (4) 8×A100에서 다단계 학습 필요. |

---

## Method

### Stage 1 — Hierarchical SFT (HSFT): 사고 템플릿 증류
- 교사 LLM(o1-mini, GPT-4o-mini)에게 수학 풀이를 XML 구조의 **계층적 사고 템플릿**으로 변환
  - **High-level thought** (`<Generalized>` 태그): 일반화된 풀이 전략
  - **Detailed solution** (`<Step_k>` + `<Key>` 태그): 각 단계의 핵심 계산/변환 상세 주석
- 100K 샘플 HSFT 데이터셋 구축 후 학생 LLM SFT
- 훈련: 4 에포크, 배치 8, lr=2e-5, AdamW + cosine, flash-attention

### Stage 2 — Cross-model Collaborative DPO: 교차 모델 교정
- HSFT 학생 모델의 오류 풀이 수집 → 오류 데이터셋 구성
- **Chosen**: 교사 LLM이 오류 단계의 원인(`<Cause>`)과 교정(`<Correction>`) 제공
- **Rejected**: 학생 모델 자신의 self-correction 트레이스
- **Thought-level DPO**: 인스턴스 전체가 아닌 오류 단계 단위로 최적화 — 올바른 이전 단계가 rejected로 잘못 학습되는 문제 방지
- DPO 훈련: 8 에포크, 배치 128, lr=1e-6

### Inspector LLM
- o1-preview가 교사 생성 교정 트레이스의 정확도를 검증하여 품질 보증
- GPT-4o-mini + Inspector: 정확도 92.4% → 98.8%

---

## Key Contribution

1. **2단계 교사-학생 증류**: HSFT(추론) + Cross-model DPO(교정)를 분리하여 체계적 전달
2. **Thought-level DPO**: 오류 단계 단위 최적화로 Step-DPO보다 정밀한 교정 학습
3. **Inspector LLM 품질 보증**: 교사 모델 생성 데이터의 오류를 자동 검증
4. **7B 모델 SOTA**: SuperCorrect-Qwen-7B가 MATH 70.2% 달성

---

## Experiment & Results

- **모델**: Qwen2.5-Math-7B, DeepSeekMath-7B, Llama3.1-8B
- **벤치마크**: MATH, GSM8K

**메인 결과**:

| 모델 | MATH | GSM8K |
|------|------|-------|
| Qwen2.5-Math-7B (기준) | 55.1% | 83.2% |
| **SuperCorrect-Qwen-7B** | **70.2%** | **89.5%** |
| SuperCorrect-DeepSeek-7B | 54.6% | 88.2% |
| SuperCorrect-Llama-8B | 58.2% | 89.7% |
| Llama3-70B (10배 크기) | 50.4% | 93.0% |

- SuperCorrect-Qwen: Qwen 대비 MATH **+15.1%**, 70B Llama3보다 **+19.8%**

**Ablation (Qwen 기반)**:
- Base + 일반 SFT: 57.4% → Base + HSFT: 62.4% (+5.0%)
- HSFT + Reflexion: 63.1% → HSFT + Cross-DPO: **70.2%** (+7.1%)

**교정 능력**: Cross-DPO 적용 후 오류 위치 정확도 0.43→**0.67**, 교정 정확도 0.12→**0.46**

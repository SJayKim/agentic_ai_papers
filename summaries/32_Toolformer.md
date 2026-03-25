# Toolformer: Language Models Can Teach Themselves to Use Tools

> **논문 정보**: Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom (Meta AI Research)
> **arXiv**: 2302.04761 (2023.02)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 대화·추론에서 뛰어나지만, 단순 산술, 최신 정보 조회, 시간 인식 등 기본 기능에서 구조적으로 취약하다. 기존 도구 사용 연구는 대량의 인간 주석에 의존하거나 특정 태스크에만 한정되어, 범용적이고 자율적인 도구 사용이 불가능했다. |
| **Motivation** | 검색 엔진, 계산기, 번역기 등 외부 도구는 LLM의 고유한 한계를 보완할 수 있지만, 모델이 언제·어떤 도구를·어떻게 호출할지를 스스로 결정하는 자가 학습 방법이 없었다. 인간이 유용하다고 판단하는 것과 모델이 실제로 필요로 하는 것이 다를 수 있어, 모델 자체의 신호에 기반한 학습이 필요하다. |
| **Limitation** | 저자 언급: API 호출은 입력당 최대 1회로 제한, 도구 간 연쇄 호출(chaining) 미지원. 독자 관점: GPT-J 6.7B 기반으로 대형 모델에서의 스케일링 효과 미검증. 5개 도구만 실험하여 다양한 API 생태계로의 확장성 불확실. Self-supervised 필터링이 비용이 높고, 새 도구 추가 시 데이터셋 재생성 필요. |

---

## Method

1. **Self-Supervised API 호출 데이터 생성 (3단계)**
   - **Sampling**: 각 API에 대해 소수(~5개)의 데모를 프롬프트로 제공하고, LM이 텍스트 데이터셋 C의 각 위치 i에서 API 호출 후보를 샘플링. `<API>` 토큰의 확률이 임계값 s를 초과하는 위치를 선별
   - **Execution**: 샘플링된 API 호출을 실제 실행하여 결과 r을 획득
   - **Filtering**: API 호출+결과를 포함했을 때의 손실(L⁺)과 호출 없을 때의 손실(L⁻)을 비교. L⁻ - L⁺ ≥ τ (필터링 임계값)인 호출만 유지 — 즉 모델이 미래 토큰 예측에 실제로 도움이 된다고 판단한 호출만 선별
   - 가중 함수 w_t = max(0, 1-0.2t)로 API 호출 직후 위치에 더 큰 가중치 부여

2. **파인튜닝**
   - 필터링된 API 호출을 원본 텍스트에 삽입하여 증강 데이터셋 C* 생성
   - C*로 GPT-J (6.7B)를 표준 언어 모델링 목적 함수로 파인튜닝
   - C*가 원본 C와 동일한 텍스트를 포함하므로 범용 언어 모델링 능력 보존

3. **추론 시 도구 호출**
   - 디코딩 중 `<API>` 토큰이 top-k(k=10)에 포함되면 API 호출 시작
   - `→` 토큰 생성 시 디코딩 중단 → API 실행 → 결과 삽입 → 디코딩 재개
   - 입력당 최대 1회 API 호출로 무한 루프 방지

4. **통합된 5개 도구**: QA 시스템(Atlas), 계산기(사칙연산), Wikipedia 검색(BM25), 기계번역(NLLB 600M), 캘린더(현재 날짜)

---

## Key Contribution

1. **최초의 자가 지도 도구 사용 학습**: 인간 주석 없이 모델 자체의 손실 신호만으로 "언제, 어떤 도구를, 어떻게" 호출할지를 학습하는 패러다임 제시
2. **범용성 보존**: 도구 사용 학습 후에도 원본 언어 모델링 능력(perplexity)이 유지되어, 태스크 특화 없이 제로샷으로 다양한 다운스트림 태스크에 적용 가능
3. **6.7B 모델이 175B 모델에 필적**: 도구 접근 덕분에 Toolformer(GPT-J 6.7B)가 GPT-3(175B)과 비교 가능한 성능 달성

---

## Experiment & Results

- **기반 모델**: GPT-J (6.7B)
- **비교 대상**: GPT-J (vanilla), GPT-J+CC (API 없이 동일 데이터 파인튜닝), OPT (66B), GPT-3 (175B)
- **평가**: 제로샷, 태스크별 도구 지정 없이 모델이 자율 판단

**수학 (수학적 데이터셋)**:
- Toolformer: ASDiv 40.2%, SVAMP 29.4%, MAWPS 44.0%
- GPT-3 (175B): ASDiv 52.0%, SVAMP 32.5%, MAWPS 49.0% — 25배 작은 모델이 근접

**QA (질문응답)**:
- Toolformer: WebQS 15.4%, NQ 17.5%, TriviaQA 48.8%
- GPT-J: WebQS 6.2%, NQ 7.3%, TriviaQA 38.8% — 도구 없는 동일 모델 대비 2~2.5배 향상

**다국어**:
- Toolformer: MLQA 43.6% (번역 도구 활용)
- GPT-3: MLQA 34.2% — 175B 모델을 초과

**언어 모델링 perplexity**: WikiText: Toolformer 16.03 vs GPT-J 15.88 — 도구 학습 후에도 perplexity 거의 동일하게 유지

**스케일링**: 모델 크기 775M → 6.7B로 증가할수록 도구 사용 효과가 크게 증가 — 작은 모델은 도구를 효과적으로 활용하지 못함

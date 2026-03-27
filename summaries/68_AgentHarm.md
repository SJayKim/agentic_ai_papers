# AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents

> **논문 정보**: Maksym Andriushchenko, Alexandra Souly 외 (Gray Swan AI, UK AI Security Institute)
> **arXiv**: 2410.09024 (2024.10)
> **학회**: ICLR 2025
> **코드**: https://huggingface.co/datasets/ai-safety-institute/AgentHarm

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트 안전성 평가가 단일 턴 챗봇 설정에만 국한되어, 도구를 사용하는 에이전트가 다단계 해로운 행동을 수행할 위험을 체계적으로 측정하지 못한다. |
| **Motivation** | 에이전트가 이메일, 파일 조작, 웹 검색 등 실세계 도구를 사용하면 악의적 지시에 따라 다단계 해로운 행동 체인을 실행할 수 있다. 단일 턴 안전성이 다중 턴 에이전트로 전이되지 않는다. |
| **Limitation** | 영어만 포함. 멀티턴 공격 미지원. 합성 도구 환경이라 실제 피해 미발생. 그레이딩 함수가 대안적 실행 경로를 놓칠 수 있음. |

---

## Method

### 1. 태스크 설계 (110 base + 330 augmented = 440개)
- 11개 해악 카테고리: 사기, 사이버범죄, 괴롭힘, 저작권 침해, 테러리즘 등
- 각 태스크는 2~8개 도구 호출을 순차 요구, 이전 결과를 다음에 통합하는 의존 구조
- 각 악의적 태스크마다 동일 도구의 **무해한 대응 태스크(benign counterpart)** 작성

### 2. 태스크 증강 (4가지)
- Detailed task, Open-ended task, Hint included (detailed), Hint included (open-ended)

### 3. 합성 도구 (104개)
- Inspect 프레임워크 기반, 사이드 이펙트 없는 독립 함수
- 일반(`send_email`) ~ 도메인 특화(`finetune_huggingface_model`)까지 포함
- 자가 수정 지원: 파일명 환각 시 오류 메시지 반환

### 4. 세밀한 채점 루브릭
- 수동 작성 조건 검사 위주, 의미론 검사에만 부분적 LLM 심판 활용
- 부분 점수 부여 가능, 거부 판정(refusal judge) 별도 적용

### 5. 데이터 분할
- Validation 10%, Public test 60%, Private test 30%
- Canary string 삽입으로 학습 데이터 필터링 지원

### 6. 공격 방법
- No attack (직접 요청), Forced tool call, Universal jailbreak template

---

## Key Contribution

1. **최초의 에이전트 직접 공격 전용 벤치마크**: 악의적 사용자가 직접 해로운 지시를 내리는 시나리오를 대규모로 다룸
2. **능력 저하 감지 내장**: 탈옥 후에도 다단계 태스크 수행 가능 여부를 함께 측정
3. **놀라운 순응성 발견**: Mistral Large 2가 탈옥 없이 82.2% 해악 점수 — 에이전트 안전 훈련이 불충분
4. **범용 탈옥의 에이전트 전이성 입증**: 채팅용 탈옥 템플릿이 에이전트에도 효과적

---

## Experiment & Results

**기본 해악 점수 (탈옥 없음)**:
- Mistral Large 2: **82.2%** (거부율 1.1%) — 가장 높은 순응성
- GPT-4o mini: 62.5% (거부율 22%)
- GPT-4o: 48.4% (거부율 48.9%)
- Claude 3.5 Sonnet: 13.5% (거부율 85.2%)
- Llama-3.1 405B: 거부율 88.3% 최고

**범용 탈옥 적용 후**:
- GPT-4o: 48.4% → **72.7%** (거부율 48.9% → 13.6%)
- Claude 3.5 Sonnet: 13.5% → **68.7%** (거부율 85.2% → 16.7%)
- Gemini 1.5 Pro: 15.7% → **56.1%** (거부율 78.4% → 3.5%)

**Best-of-5 (τ=1, 탈옥)**:
- GPT-4o: 72.7% → **83.7%**, Claude: 68.7% → **79.7%**, Mistral: 80.5% → **90.8%**

**탈옥 후 능력 보존**: 비거부 해악 점수와 무해 태스크 점수가 유사 → 탈옥이 에이전트 능력을 저하시키지 않음

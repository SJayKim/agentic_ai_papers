# Gorilla: Large Language Model Connected with Massive APIs

> **논문 정보**: Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez (UC Berkeley, Microsoft Research)
> **arXiv**: 2305.15334 (2023.05)
> **코드**: https://gorilla.cs.berkeley.edu

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM이 API를 호출할 때 잘못된 인자를 생성하거나 존재하지 않는 API를 환각(hallucination)하는 문제가 심각하다. GPT-4도 TorchHub에서 36.55%의 환각 오류율을 보이며, API 문서가 빈번하게 변경되면 모델 재학습 없이는 최신 정보를 반영할 수 없다. |
| **Motivation** | 웹 스케일의 수백만 개 API를 LLM 프롬프트에 모두 넣을 수 없고, 유사 기능의 API가 겹치며 미묘한 제약 조건이 존재한다. 소수의 하드코딩된 도구가 아닌 방대하고 변화하는 API 생태계에서 정확한 호출을 위한 체계적인 파인튜닝과 검색 통합이 필요하다. |
| **Limitation** | 저자 언급: 현재 검색기(BM25, GPT-Index)가 불완전하면 오히려 성능을 저해할 수 있음 (TorchHub에서 -21.5%). 독자 관점: LLaMA-7B 기반으로 모델 규모가 작아 복잡한 제약 조건 추론에 한계. APIBench가 ML 허브에 국한되어 REST API, 웹서비스 등 일반 API로의 확장성 미검증. |

---

## Method

1. **APIBench 데이터셋 구축**
   - TorchHub (94개, 전수), TensorFlow Hub (696개, 전수), HuggingFace (925개, 도메인별 top-20) — 총 1,645개 API
   - 각 API의 모델 카드를 JSON 구조로 변환: {domain, framework, api_call, api_arguments, performance, ...}
   - GPT-4 Self-Instruct로 API당 10개 자연어 지시문 생성 (총 16,450 쌍), 직접 작성은 18개 예시만

2. **Gorilla 모델 학습 (Retriever-Aware Fine-tuning)**
   - LLaMA-7B를 {instruction, API} 쌍으로 대화 형식 파인튜닝
   - **Zero-shot 모드**: 사용자 프롬프트만으로 API 생성
   - **Retrieval 모드**: 검색기(BM25/GPT-Index)가 최신 API 문서를 검색 → 프롬프트에 append → "Use this API documentation for reference:" 형태로 학습
   - 학습 시 검색 결과를 포함하여 모델이 검색된 문서를 파싱하고 활용하는 법을 학습 (retriever-aware training)

3. **AST Sub-Tree Matching 평가**
   - 생성된 코드를 AST로 파싱 후 API 호출 서브트리를 데이터셋과 매칭
   - **환각**: 데이터베이스에 없는 API를 호출한 경우
   - **오류**: 존재하는 API지만 잘못 사용한 경우
   - 기존 단위 테스트의 한계(동일 기능의 여러 정답 API 존재)를 극복하는 평가 체계

4. **제약 조건 추론**: "10M 파라미터 미만, ImageNet 정확도 70% 이상" 등 복합 제약이 포함된 프롬프트에서 API를 선택하는 능력 평가

---

## Key Contribution

1. **대규모 API 호출 전용 파인튜닝 파이프라인**: Self-Instruct + Retriever-Aware Training으로 7B 모델이 GPT-4를 능가하는 API 호출 정확도 달성 (zero-shot +20.43%)
2. **테스트 타임 문서 변경 적응**: 검색기 결합 학습으로 API 버전 업그레이드, 레포지토리 변경 등에 재학습 없이 대응 가능
3. **APIBench 및 AST 평가 체계**: ML API 1,645개를 포괄하는 벤치마크와 환각/오류를 분리 측정하는 AST 기반 평가 도입

---

## Experiment & Results

- **Baseline**: GPT-4, GPT-3.5-Turbo, Claude, LLaMA-7B
- **검색기**: Zero-shot, BM25, GPT-Index, Oracle

**Zero-shot (검색기 없이)**:
- Gorilla: TorchHub 59.13%, HuggingFace 71.68%, TensorHub 83.79%
- GPT-4: TorchHub 38.70%, HuggingFace 19.80%, TensorHub 18.20%
- Gorilla가 GPT-4 대비 평균 +20.43% 정확도, 환각률 5~11% vs GPT-4 36~78%

**GPT-Index 검색기 사용 시**:
- Gorilla: TorchHub 61.82% (환각 0%), HuggingFace 47.46%, TensorHub 64.96%
- GPT-4: TorchHub 59.13%, HuggingFace 44.58%, TensorHub 43.94%

**Oracle 검색기 사용 시**: Gorilla HuggingFace 91.26%, TensorHub 94.16% — 검색기 품질이 핵심 병목

**환각 감소**: Gorilla는 TorchHub에서 환각 0~7%로 GPT-4(36.55%)와 Claude(65.59%)를 압도적으로 개선

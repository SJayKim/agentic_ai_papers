# GAIA: A Benchmark for General AI Assistants

> **논문 정보**: Grégoire Mialon et al. (Meta AI, Hugging Face, AutoGPT)
> **arXiv**: 2311.12983 (2023.11)
> **코드**: https://huggingface.co/gaia-benchmark

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 범용 AI 어시스턴트의 능력을 측정하는 벤치마크가 부재. 기존 벤치마크는 특정 기능(수학, 코드 등)만 평가하여 실세계 복합 태스크 처리 능력을 반영하지 못한다. |
| **Motivation** | 실세계 질문은 멀티모달 추론, 웹 브라우징, 도구 사용, 복잡한 다단계 문제 해결을 동시에 요구. 인간은 이를 92%에서 해결하지만 GPT-4+플러그인은 15%에 불과하여, AGI까지의 거리를 측정하는 엄격한 벤치마크가 필요. |
| **Limitation** | 저자 언급: 450개 질문으로 규모 제한. 독자 관점: 3단계 난이도 분류가 주관적일 수 있음. |

---

## Method

1. **450개 실세계 질문**: 멀티모달(이미지, PDF, 오디오) + 웹 검색 + 도구 사용이 필요한 복합 질문
2. **3단계 난이도**: Level 1 (1~5단계), Level 2 (5~10단계), Level 3 (10+단계, 전문 도구 필요)
3. **자동 평가**: 정답이 짧고 명확하여 자동 채점 가능

---

## Key Contribution

1. **AGI 측정 벤치마크**: 인간 92% vs GPT-4 15%의 극적 격차로 현재 AI의 한계를 정량화
2. **OWL, WORKFORCE 등 후속 에이전트 연구의 표준 벤치마크**로 자리잡음

---

## Experiment & Results

- 인간: 92%, GPT-4+plugins: 15%, AutoGPT: ~5%
- Level 3에서 GPT-4가 0%에 가까움 → 복합 도구 사용의 근본적 한계

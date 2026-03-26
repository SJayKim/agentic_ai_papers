# AgentBench: Evaluating LLMs as Agents

> **논문 정보**: Xiao Liu, Hao Yu, Hanchen Zhang 외 (Tsinghua University, THUDM)
> **arXiv**: 2308.03688 (2023.08)
> **코드**: https://github.com/THUDM/AgentBench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM의 에이전트 능력을 평가하는 포괄적 벤치마크가 부재. 기존 평가는 단일 환경에 국한되어 다양한 에이전트 시나리오에서의 종합적 비교가 불가능하다. |
| **Motivation** | 에이전트로서의 LLM은 웹 브라우징, 코드 실행, 게임, DB 쿼리 등 다양한 환경에서 장기 추론과 의사결정이 필요. 8개 환경에서 29개 모델을 통합 평가하면 LLM 에이전트 능력의 실체를 파악 가능. |
| **Limitation** | 저자 언급: 일부 환경이 특정 능력에 편향. 독자 관점: 멀티모달 태스크 미포함. |

---

## Method

1. **8개 평가 환경**: Operating System, Database, Knowledge Graph, Digital Card Game, Lateral Thinking Puzzle, Household, Web Shopping, Web Browsing
2. **29개 LLM 평가**: GPT-4, ChatGPT, Claude, LLaMA 등 상용+오픈소스 모델 포괄
3. **장기 추론 평가**: 다중 턴 상호작용에서 계획 수립, 도구 사용, 오류 복구 등 종합 평가

---

## Key Contribution

1. **최초의 다중 환경 에이전트 벤치마크**: 8개 환경에서 LLM-as-agent를 통합 평가
2. **상용-오픈소스 격차 발견**: 상위 상용 LLM과 오픈소스 모델 간 에이전트 능력에 큰 격차 존재

---

## Experiment & Results

- GPT-4가 전반적으로 최고 성능, ChatGPT가 그 다음
- 오픈소스 모델은 상용 모델 대비 장기 추론과 도구 사용에서 크게 뒤처짐
- 코드 관련 환경에서는 격차가 상대적으로 작음

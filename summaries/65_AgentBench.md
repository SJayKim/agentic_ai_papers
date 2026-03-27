# AgentBench: Evaluating LLMs as Agents

> **논문 정보**: Xiao Liu, Hao Yu, Hanchen Zhang 외 (Tsinghua University, OSU, UC Berkeley)
> **arXiv**: 2308.03688 (2023.08) | **학회**: ICLR 2024
> **코드**: https://github.com/THUDM/AgentBench

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트 능력을 평가하는 포괄적·표준화된 벤치마크가 부재. 기존 평가는 단일 환경, 좁은 액션 스페이스에 국한되어 종합적 비교가 불가능하다. |
| **Motivation** | 8개 환경(OS, DB, KG, 카드 게임, 퍼즐, 가정, 웹 쇼핑, 웹 브라우징)에서 29개 모델을 통합 평가하면 LLM 에이전트 능력의 실체를 파악할 수 있다. |
| **Limitation** | (1) 텍스트 전용, 멀티모달 미포함. (2) 일부 환경이 특정 능력(코드, 절차 추종)에 편향. (3) OSS 모델 70B 이하 제한. (4) temperature=0 고정. |

---

## Method

### 8개 환경, 3가지 접지 유형 (5개 신규 제안)

**Code-grounded**: OS (Ubuntu bash), DB (MySQL), KG (Freebase 45M 개체)
**Game-grounded**: Digital Card Game (Aquawar), Lateral Thinking Puzzles, House Holding (ALFWorld)
**Web-grounded**: Web Shopping (WebShop), Web Browsing (Mind2Web)

### 평가 프레임워크
- Dev 269개, Test 1,014개 샘플. 환경별 난이도 편향 제거를 위해 역평균 점수 가중 평균
- CoT 기반 "Thought + Action" 형식, temperature=0
- Server-Client HTTP 아키텍처, Docker 캡슐화
- 실패 유형: CLE(컨텍스트 초과), IF(형식 오류), IA(잘못된 액션), TLE(라운드 한도 초과)

### 29개 모델
API: GPT-4, GPT-3.5-turbo, Claude, PaLM2, GLM-4 + OSS: LLaMA-2, CodeLLaMA, Vicuna, WizardLM 등

---

## Key Contribution

1. **최초의 다중 환경 에이전트 벤치마크**: 8개 환경(5개 신규)에서 통합 평가
2. **상용-오픈소스 격차 정량화**: API 모델 평균 2.32 vs OSS 평균 0.51 (4.5배 격차)
3. **실패 원인 체계적 분석**: TLE, IF/IA, CLE 유형별 정량 분석
4. **코드 학습의 양면성**: 절차적 태스크에 유리하지만 일반 추론에는 불리
5. **고품질 정렬 데이터의 중요성**: vicuna-13b가 codellama-34b와 대등 — 데이터 품질 > 모델 크기

---

## Experiment & Results

**전체 순위 (OA Score)**:
- GPT-4: **4.01** — 압도적 1위
- Claude-3 Opus: **3.11**, GLM-4: **2.89**, GPT-3.5: **2.32**
- 최상위 OSS codellama-34b: **0.96** — GPT-3.5에도 크게 미달

**환경별 실패 유형**: TLE가 지배적 (KG 67.9%, LTP 82.5%), IF가 DB(53.3%)·DCG(38.5%)에서 두드러짐

**GPT-4 환경별**: OS 42.4%, DB 32.0%, KG 58.8%, DCG 74.5%, HH 78.0%, WS 61.1%, WB 29.0%

**코드 학습 양면성**: CodeLLaMA-34b WS 52.1%(우수) vs DCG 8.4%(열세, llama-2-70b 21.3%)

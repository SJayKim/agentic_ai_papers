# Plan-on-Graph: Self-Correcting Adaptive Planning of LLM on Knowledge Graphs

> **논문 정보**: Liyi Chen, Panrong Tong, Zhongming Jin, Ying Sun, Jieping Ye, Hui Xiong (USTC, Alibaba Cloud, HKUST-GZ)
> **arXiv**: 2410.23875 (2024.10)
> **학회**: NeurIPS 2024
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | ToG, StructGPT 등 기존 KG-augmented LLM은 탐색 너비를 수동 고정하고 단방향 탐색만 수행한다. 잘못된 경로를 탐지·교정하는 메커니즘이 없어 오류가 누적되며, 복잡한 질문에서 LLM이 조건 일부를 망각한다. |
| **Motivation** | 서브 목표 분해 + 의미론적 안내(Guidance) + 메모리(Memory) + 반성(Reflection)을 결합하면, 효율과 정확도를 동시에 향상시킬 수 있다. |
| **Limitation** | 서브 목표 분해 품질이 LLM 성능에 전적 의존. Reflection이 추가 LLM 호출 유발. 긴 추론 체인에서 메모리가 컨텍스트 한계에 근접 가능. entity linking이 사전 레이블링되어 있다는 가정에 의존. |

---

## Method

### 1. Task Decomposition
LLM이 질문을 서브 목표 리스트 O = {o1, o2, ...}로 분해. 이후 전 과정에서 KG 탐색 방향을 안내하는 Guidance로 기능.

### 2. Path Exploration (적응적 너비)
- **Relation Exploration**: 꼬리 엔티티의 후보 관계 수집 → LLM이 서브 목표 기반으로 유연한 수(adaptive breadth)로 선택
- **Entity Exploration**: 후보 엔티티 다수 시 DistilBERT로 사전 필터링 → LLM이 최종 선택

### 3. Memory Updating
- **Subgraph (G_Sub)**: 검색된 엔티티/관계 집합 — Reflection 시 역추적 대상 결정에 활용
- **Reasoning Paths (P)**: 추론 경로 전체 — 경로 구조 유지로 교정 가능
- **Sub-Objective Status (S)**: 서브 목표별 알려진 정보 요약 — 조건 망각 문제 완화

### 4. Evaluation & Reflection
- 충분 시: 추론 경로 + 서브 목표 상태 + LLM 지식 통합하여 최종 답변
- 불충분 시: 현재 경로 계속 확장 또는 이전 엔티티로 역추적(backtrack) 결정. 역추적 시 전체 candidate에서 되돌아갈 엔티티 선택

---

## Key Contribution

1. **최초의 KG 반성 메커니즘**: self-correction + adaptive exploration을 통합한 최초 연구
2. **Training-free**: 프롬프팅만으로 파인튜닝 기반 SOTA(GAIN 등) 능가
3. **효율성**: ToG 대비 LLM 호출 최소 40.8% 감소, 처리 시간 4배 이상 단축
4. **Zero-shot 강건성**: GrailQA 제로샷에서 GPT-3.5로도 모든 파인튜닝 방법 능가

---

## Experiment & Results

- **데이터셋**: CWQ, WebQSP, GrailQA (Freebase 기반)

**성능 (Hits@1)**:

| 방법 | CWQ | WebQSP | GrailQA |
|------|-----|--------|---------|
| ToG (GPT-3.5) | 57.1 | 76.2 | 68.7 |
| **PoG (GPT-3.5)** | **63.2** | **82.0** | **76.5** |
| **PoG (GPT-4)** | **75.0** | **87.3** | **84.7** |
| GAIN (Fine-tuned) | — | — | 76.3 |

**효율성 (GPT-3.5, CWQ)**: LLM 호출 22.6→13.3 (-41%), 토큰 1486→353 (-76%), 시간 96.5s→23.3s (-76%)

**Ablation (CWQ)**: w/o Memory -4.3%p (최대 저하), w/o Reflection -3.8%p, w/o Guidance -3.1%p

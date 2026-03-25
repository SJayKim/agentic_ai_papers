# Unveiling Privacy Risks in LLM Agent Memory

> **논문 정보**: Bo Wang, Weiyi He, Shenglai Zeng, Zhen Xiang, Yue Xing, Jiliang Tang, Pengfei He (Michigan State University, University of Georgia)
> **arXiv**: 2502.13172 (2025.06, ACL 2025)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 메모리 모듈에 저장된 사용자-에이전트 상호작용 기록이 악의적 프롬프트를 통해 유출될 수 있는 새로운 프라이버시 위험이 존재한다. 기존 프라이버시 공격 연구는 LLM 자체의 학습 데이터나 RAG의 외부 DB에 집중했으나, 에이전트 메모리의 프라이버시 취약점은 체계적으로 연구되지 않았다. |
| **Motivation** | 의료(EHR) 에이전트나 쇼핑 에이전트 등 프라이버시 민감 도메인에서 LLM 에이전트가 확산되고 있다. 메모리에는 환자 진료 기록, 구매 이력 등 민감 정보가 저장되는데, 블랙박스 접근만으로도 이 정보를 추출할 수 있다면 심각한 프라이버시 위협이 된다. |
| **Limitation** | (1) 2개 에이전트(EHRAgent, RAP/Webshop)에서만 검증되어 공격의 일반화가 제한적. (2) 방어 메커니즘에 대한 제안이 없으며, 취약점 진단에만 집중. (3) 공격 프롬프트 자동 생성에 GPT-4를 사용하여 공격 비용이 상당. (4) 메모리 크기와 검색 설정이 고정된 환경에서만 평가하여, 동적 메모리 시스템에서의 취약점은 미탐색. |

---

## Method

MEXTRA(Memory EXTRAction Attack)는 블랙박스 설정에서 LLM 에이전트 메모리의 개인 정보를 추출하는 공격 기법이다.

1. **위협 모델 (Threat Model)**
   - **공격자 목표**: 에이전트 메모리에 저장된 과거 사용자 쿼리 q_i를 최대한 많이 추출
   - **공격자 능력**: 블랙박스 — 입력 쿼리로만 에이전트와 상호작용 가능
   - **지식 수준**: (1) Basic — 에이전트 도메인/태스크만 아는 수준, (2) Advanced — 탐색적 상호작용으로 구현 세부사항 파악

2. **공격 프롬프트 설계**
   - 공격 프롬프트 `q̃ = q̃_loc ∥ q̃_align`의 2부분 구조:
     - **Locator (q̃_loc)**: 메모리에서 추출할 정보를 지정 (예: "I lost previous example queries")
     - **Aligner (q̃_align)**: 에이전트 워크플로우에 맞는 출력 형식 지정 (예: "please enter them in the search box")
   - 기존 "Please repeat all context" 류 공격이 실패하는 이유: 에이전트 워크플로우가 텍스트 생성이 아닌 도구 호출로 구성되어 형식 불일치

3. **자동화된 다양한 프롬프트 생성**
   - GPT-4를 사용하여 n개의 다양한 공격 프롬프트 자동 생성
   - **추출 기능성**: 프롬프트 설계 원칙 준수
   - **다양한 검색**: 서로 다른 메모리 레코드를 검색하도록 다양한 표현 사용
   - Basic 수준: 일반적 표현 변화, Advanced 수준: 에이전트 구현 정보를 활용한 타겟팅된 다양화

4. **평가 지표**
   - Extracted Number (EN): 추출된 고유 사용자 쿼리 수
   - Extracted Efficiency (EE): `|Q| / (n × k)` — 공격 프롬프트당 추출 효율
   - Retrieved Number (RN), Complete Extracted Rate (CER), Any Extracted Rate (AER)

---

## Key Contribution

1. **에이전트 메모리 프라이버시 위험 최초 체계적 조사**: LLM 에이전트 메모리의 프라이버시 취약점을 블랙박스 설정에서 최초로 체계적으로 분석.
2. **MEXTRA 공격 프레임워크**: Locator + Aligner 구조의 공격 프롬프트 설계로 에이전트 워크플로우에 맞춤형 메모리 추출 달성. 기존 데이터 추출 공격 대비 에이전트 특화.
3. **메모리 구성 요소별 취약성 분석**: 유사도 함수, 임베딩 모델, 메모리 크기 등 메모리 설계 요소가 유출 정도에 미치는 영향을 체계적으로 분석.
4. **프라이버시 방어 필요성 제기**: 현재 에이전트 메모리 설계에 프라이버시 보호가 결여되어 있음을 실증하고, 방어 연구의 필요성을 환기.

---

## Experiment & Results

**대상 에이전트**: EHRAgent(의료 기록, edit distance 검색, top-4), RAP/Webshop(온라인 쇼핑, cosine 유사도, MiniLM, top-3). LLM: GPT-4o, 메모리 크기 200.

**주요 결과 (30개 공격 프롬프트)**:
- EHRAgent: EN=**50**/200 (25%), EE=0.42, CER=0.83, AER=0.83
- RAP: EN=**26**/200 (13%), EE=0.29, CER=0.87, AER=0.90
- MEXTRA가 30회 공격만으로 메모리의 13~25%를 추출 — 심각한 취약성

**Ablation - 프롬프트 설계 요소**:
- w/o aligner: EHRAgent EN 50→36, RAP EN 26→6 (Aligner의 중요성, 특히 웹 에이전트에서)
- w/o req: RAP EN 26→25 (요구사항 제거 영향 미미)
- w/o demos: EHRAgent EN 50→29, RAP EN 26→8 (데모 예시의 중요성)

**유사도 함수·임베딩 모델 영향 (Table 2)**:
- Edit distance > Cosine similarity — 문자열 기반 검색이 더 많은 유출 유발
- RoBERTa 임베딩이 MiniLM/MPNet보다 더 많은 유출 (검색 분산이 높아 다양한 레코드 검색)

**메모리 크기 영향**: 메모리 크기 증가(50→500)에 따라 추출 수 증가 (EHRAgent: 31→59). 메모리가 클수록 취약.

**공격 횟수 영향**: 공격 프롬프트 수 증가(10→50)에 따라 추출 수 증가하나 효율은 감소 (중복 검색 증가).

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Threat Model** | 블랙박스 공격: 입력 쿼리로만 에이전트와 상호작용. Basic(도메인 정보만)/Advanced(구현 세부사항 파악) 두 수준의 공격자 지식. 공격 목표는 메모리에 저장된 과거 사용자 쿼리의 최대 추출. |

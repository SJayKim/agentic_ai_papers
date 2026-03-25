# MIRIX: Multi-Agent Memory System for LLM-Based Agents

> **논문 정보**: Yu Wang, Xi Chen (MIRIX AI / UCSD / NYU)
> **arXiv**: 2025.07
> **코드**: https://mirix.io/

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 메모리 시스템은 단일 평면(flat) 저장소에 의존하여, 에피소드·시맨틱·절차적 지식을 구분하지 못한다. 텍스트 중심 설계로 멀티모달(이미지, 스크린샷 등) 입력을 처리하지 못하며, 원시 입력 저장은 스토리지 요구를 폭증시킨다. |
| **Motivation** | 인간 인지는 에피소드 기억, 의미 기억, 절차 기억 등 다양한 메모리 유형을 활용한다. LLM 에이전트도 장기 개인화·패턴 인식·맥락 인식 응답을 위해 구조화된 다중 메모리 유형이 필요하다. 특히 웨어러블 기기 등에서 스크린샷 같은 멀티모달 입력의 메모리 관리가 실질적으로 필요하다. |
| **Limitation** | (1) 6개 메모리 유형에 8개 에이전트를 운영하므로 LLM 호출 횟수가 많아 비용·지연이 증가한다. (2) ScreenshotVQA가 3명의 PhD 학생 데이터(87개 질문)로 매우 소규모이다. (3) LOCOMO에서 Single-Hop 질문의 모호성으로 인한 성능 한계가 있다. (4) Knowledge Vault의 민감 정보 보안에 대한 체계적 검증이 부족하다. |

---

## Method

MIRIX는 인간 인지 시스템에서 영감을 받은 **6종 메모리 + 다중 에이전트** 아키텍처다.

1. **6가지 메모리 컴포넌트**
   - **Core Memory**: 항상 에이전트에 노출되는 고우선순위 영속 정보 (사용자 이름, 선호 등)
   - **Episodic Memory**: 시간 태그된 특정 이벤트·경험 (타임스탬프, 요약, 상세)
   - **Semantic Memory**: 시간 독립적 추상 지식·사실·관계 (계층적 트리 구조로 조직)
   - **Procedural Memory**: 목표 지향 프로세스, 가이드, 워크플로우 (단계별 지침)
   - **Resource Memory**: 문서, 파일, 멀티모달 리소스 (전체/발췌 저장)
   - **Knowledge Vault**: 자격 증명, 주소, API 키 등 민감한 verbatim 정보 (보안 등급별)

2. **Active Retrieval 메커니즘**
   - 사용자 입력에서 자동으로 토픽 추출 → 6개 메모리 컴포넌트 각각에서 상위 10개 관련 항목 검색
   - 검색 결과를 소스 태그(`<episodic_memory>` 등)와 함께 시스템 프롬프트에 주입
   - embedding_match, bm25_match, string_match 등 다양한 검색 전략 지원

3. **Multi-Agent Workflow (8개 에이전트)**
   - **Meta Memory Manager**: 중앙 제어 — 입력 분석 후 관련 Memory Manager들에 라우팅
   - **6개 Memory Manager**: 각 메모리 유형별 전담 에이전트, 병렬 업데이트 수행
   - **Chat Agent**: 사용자와 대화, 자동 검색 후 응답 생성, 필요 시 Memory Manager에 업데이트 요청
   - **업데이트 흐름**: 입력 → 자동 검색 → Meta Memory Manager 분석 → 관련 Memory Manager들에 병렬 분배 → 중복 방지 업데이트 → 확인

4. **멀티모달 지원**: 스크린샷 등 이미지 입력을 Vision LLM으로 분석 → 구조화된 메모리로 변환 → 원시 이미지 대비 99.9% 스토리지 절감

---

## Key Contribution

1. **6종 구조화 메모리**: 인간 인지에 기반한 Core/Episodic/Semantic/Procedural/Resource/Knowledge Vault 6종 메모리로, 기존 flat/단일 메모리 시스템의 한계를 근본적으로 해결.
2. **멀티모달 메모리**: 텍스트 넘어 스크린샷 등 시각 정보를 메모리로 변환·관리하는 최초의 메모리 시스템. 기존 시스템이 처리 불가능한 20,000장 스크린샷 규모까지 지원.
3. **ScreenshotVQA 벤치마크**: 실제 컴퓨터 사용 기록 기반 새로운 멀티모달 메모리 벤치마크 도입.
4. **LOCOMO SOTA**: 텍스트 기반 장기 대화에서도 85.38%로 기존 최고 대비 +8.0p 달성.

---

## Experiment & Results

**ScreenshotVQA** (Gemini-2.5-flash 백본):
- MIRIX 전체 정확도: **59.50%** vs SigLIP@50 44.10%, Gemini(long-context) 11.66%
- 스토리지: MIRIX **15.89MB** vs SigLIP 15.07GB (99.9% 절감), Gemini 236.70MB
- Student 3 (5,349장, 1개월): MIRIX 67.27% vs SigLIP 54.55%, Gemini 25.45%
- RAG 대비 +35% 정확도, long-context 대비 +410% 정확도

**LOCOMO** (gpt-4.1-mini 백본):
- MIRIX Overall: **85.38%** vs Zep 79.09%, LangMem 78.05%, Mem0 62.47%
- Multi-Hop: MIRIX **83.70%** vs Zep 69.16%, Mem0 57.32% (+24p 이상)
- Temporal: MIRIX **88.39%** vs LangMem 86.92%, Zep 83.33%
- Single-Hop: MIRIX 85.11% vs Full-Context 88.53% (근소 차이, 질문 모호성 영향)
- Full-Context(상한) 87.52% 대비 MIRIX 85.38%로 거의 근접

**gpt-4o-mini 백본 비교**: Zep 75.14%, Memobase 70.91%, Mem0g 68.44% — MIRIX의 gpt-4.1-mini 결과(85.38%)가 모든 gpt-4o-mini 결과를 크게 초과.

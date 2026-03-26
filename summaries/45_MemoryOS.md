# Memory OS of AI Agent

> **논문 정보**: Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai (BUPT, Tencent AI Lab)
> **arXiv**: 2506.06326 (2025.05)
> **코드**: https://github.com/BAI-LAB/MemoryOS

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 고정 길이 컨텍스트 윈도우에 의존하여, 시간적 간격이 큰 대화에서 사실 불일치와 개인화 부족이 발생한다. 기존 메모리 메커니즘은 지식 조직화, 검색 메커니즘, 아키텍처 중 단일 차원에만 집중하여 통합적 메모리 관리 체계가 부재하다. |
| **Motivation** | A-Mem(지식 조직화), MemoryBank(검색), MemGPT(아키텍처)가 각각 개별 차원에서 작동하지만, 운영체제의 메모리 관리 원칙처럼 저장·업데이트·검색·생성을 통합 관리하는 시스템이 없다. 장기 대화의 맥락 일관성과 사용자 개인화를 위해 체계적 메모리 OS가 필요. |
| **Limitation** | 저자 언급: LoCoMo 벤치마크에 한정된 평가. 독자 관점: 3계층 구조의 최적 파라미터(FIFO 크기, 페이징 주기 등)가 태스크별로 크게 다를 수 있으나 일반화 검증 부족. Tencent AI Lab 참여에도 대규모 실서비스 적용 결과 미보고. |

---

## Method

1. **3계층 저장 아키텍처**
   - **Short-Term Memory (STM)**: 현재 대화 세션의 최근 내용 유지. 대화 체인 기반 FIFO 원칙으로 관리
   - **Mid-Term Memory (MTM)**: STM에서 넘어온 최근 대화 기록을 보관. 시간적으로 가까운 대화의 맥락 유지
   - **Long-Term Personal Memory (LTM)**: 사용자 선호, 습관, 페르소나 등 장기적 개인화 정보. 세그먼트 페이지 조직 전략으로 구조화

2. **4개 핵심 모듈**
   - **Memory Storage**: 3계층 구조에 정보를 조직화하여 저장
   - **Memory Updating**: STM→MTM은 대화 체인 기반 FIFO, MTM→LTM은 세그먼트 페이징 + 열도(heat) 기반 메커니즘으로 동적 갱신
   - **Memory Retrieval**: 시맨틱 세그멘테이션으로 3계층에서 관련 정보를 적응적으로 검색
   - **Response Generation**: 검색된 메모리를 통합하여 맥락적으로 일관되고 개인화된 응답 생성

3. **열도(Heat) 기반 업데이트**: 자주 참조되거나 중요한 메모리의 "열도"를 추적하여 MTM→LTM 승격 결정

---

## Key Contribution

1. **최초의 체계적 메모리 OS**: 저장·업데이트·검색·생성을 통합 관리하는 운영체제 영감의 메모리 프레임워크
2. **3계층+4모듈 아키텍처**: STM/MTM/LTM의 계층적 저장과 FIFO/세그먼트 페이징/열도 기반의 동적 업데이트 메커니즘 결합
3. **LoCoMo 벤치마크에서 대폭 향상**: GPT-4o-mini 기반 F1 +49.11%, BLEU-1 +46.18%

---

## Experiment & Results

- **벤치마크**: LoCoMo (장기 대화 메모리 평가)
- **기반 모델**: GPT-4o-mini
- **Baseline**: MemGPT, A-Mem, MemoryBank 등

**주요 결과**:
- F1: baseline 대비 평균 +49.11% 향상
- BLEU-1: baseline 대비 평균 +46.18% 향상
- 장기 대화에서 맥락 일관성과 개인화 메모리 유지에서 기존 방법 대비 압도적 성능

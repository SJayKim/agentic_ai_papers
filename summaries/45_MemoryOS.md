# Memory OS of AI Agent

> **논문 정보**: Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai (BUPT, Tencent AI Lab)
> **arXiv**: 2506.06326 (2025.05)
> **코드**: https://github.com/BAI-LAB/MemoryOS

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM은 고정 길이 컨텍스트 윈도우에 의존하여, 시간적 간격이 큰 대화에서 사실 불일치와 개인화 부족이 발생한다. 기존 메모리 메커니즘은 지식 조직화(A-Mem), 검색 메커니즘(MemoryBank), 아키텍처(MemGPT) 중 단일 차원에만 집중하여, 저장·업데이트·검색·생성을 통합 관리하는 체계적 메모리 OS가 부재하다. |
| **Motivation** | 운영체제의 세그먼트-페이지 메모리 관리 원칙에서 영감을 얻어, AI 에이전트를 위한 포괄적 메모리 운영체제를 설계한다. 장기 대화에서의 맥락 일관성, 사용자 개인화, 페르소나 지속성을 동시에 달성하기 위해 계층적 저장 구조와 동적 업데이트 메커니즘의 통합이 필요하다. |
| **Limitation** | 저자 언급: 평가가 LoCoMo와 GVD 두 벤치마크에 한정되어 있으며 도메인 다양성 검증이 부족하다. 독자 관점: 3계층 구조의 핵심 하이퍼파라미터(STM 큐 길이=7, 히트 임계값 τ=5, MTM 세그먼트 최대 200 등)가 태스크·도메인별로 크게 달라질 수 있으나 일반화 검증이 미흡하다. 대규모 실서비스 적용 결과가 보고되지 않았으며, 계층 간 전환 오버헤드가 실시간 응답에 미치는 영향이 불명확하다. |

---

## Method

1. **3계층 저장 아키텍처 (Memory Storage Module)**
   - **Short-Term Memory (STM)**: 실시간 대화 데이터를 대화 페이지(dialogue page) 단위로 저장. 각 페이지는 `{Q_i, R_i, T_i}` 구조. 최대 7개 페이지의 고정 길이 큐로 유지
   - 각 페이지에 대화 체인(dialogue chain) 메타정보를 LLM이 생성: 신규 페이지의 문맥 연관성 평가 후 체인 연결 여부 결정
   - **Mid-Term Memory (MTM)**: 동일 주제의 대화 페이지를 세그먼트로 묶는 세그먼트-페이지 저장 구조 채택. 세그먼트 소속 판별은 코사인 유사도(임베딩)와 자카드 유사도(키워드)를 합산한 `F_score`로 결정 (임계값 θ=0.6)
   - **Long-term Personal Memory (LPM)**: User Persona(Profile + KB + 90차원 Traits)와 Agent Persona(Profile + Traits)로 구성. User KB와 Agent Traits 각각 최대 100개 항목의 FIFO 큐로 관리

2. **동적 업데이트 메커니즘 (Memory Update Module)**
   - **STM→MTM**: STM 큐가 최대 용량(7) 초과 시 가장 오래된 대화 페이지를 FIFO 원칙으로 MTM에 이전. `F_score`로 기존 세그먼트와 유사도를 측정하여 병합하거나 신규 세그먼트 생성
   - **MTM→LPM**: 세그먼트의 열도(Heat) 점수로 승격·삭제 결정. `Heat = α·N_visit + β·L_interaction + γ·R_recency`, `R_recency = exp(-Δt/μ)`
   - Heat 임계값 τ=5 초과 세그먼트는 LPM으로 전환되어 User Traits(90차원), User KB, Agent Traits를 LLM이 자율 갱신

3. **적응적 검색 (Memory Retrieval Module)**
   - **STM 검색**: 모든 STM 페이지를 반환하여 최근 맥락 확보
   - **MTM 2단계 검색**: `F_score`로 상위 m=5개 세그먼트 선택 → 각 세그먼트 내에서 의미 유사도 기반 상위 k개 대화 페이지 선택
   - **LPM 검색**: User KB와 Agent Traits에서 쿼리 벡터와 의미 유사도 기준 상위 10개 항목 검색

4. **응답 생성 (Response Generation Module)**
   - STM(최근 문맥) + MTM(주제별 대화 페이지) + LPM(페르소나 정보)의 검색 결과를 통합하여 최종 프롬프트 구성

---

## Key Contribution

1. **최초의 체계적 메모리 OS**: 저장·업데이트·검색·생성을 통합 관리하는 운영체제 영감의 메모리 프레임워크
2. **3계층+4모듈 아키텍처**: STM/MTM/LPM의 계층적 저장과 FIFO/세그먼트 페이징/열도 기반의 동적 업데이트 메커니즘 결합
3. **LoCoMo 벤치마크에서 대폭 향상**: GPT-4o-mini 기반 F1 평균 +49.11%, BLEU-1 평균 +46.18%
4. **효율성 우수**: A-Mem 대비 LLM 호출 수 1/2.6 수준(4.9 vs. 13), MemGPT 대비 토큰 소비 1/4.4 수준(3,874 vs. 16,977)

---

## Experiment & Results

- **벤치마크**: LoCoMo (평균 300턴, ~9K 토큰, 4유형), GVD (15명 가상 사용자, 10일간 멀티턴 대화)
- **기반 모델**: GPT-4o-mini, Qwen2.5-7B, Qwen2.5-3B
- **Baseline**: TiM, MemoryBank, MemGPT, A-Mem

**GVD (GPT-4o-mini)**:
- Accuracy: MemoryOS 93.3% vs. A-Mem 90.4% (+3.2%↑)
- Correctness: MemoryOS 91.2% vs. A-Mem 86.5% (+5.4%↑)
- Coherence: MemoryOS 92.3% vs. A-Mem 91.4% (+1.0%↑)

**LoCoMo (GPT-4o-mini)**:
- F1 평균: MemoryOS 36.23 vs. MemGPT 29.13 (전체 대비 +49.11%)
- Temporal 유형: F1 +118.80%, BLEU-1 +111.52%
- Single-hop F1 +32.35%, Multi-hop F1 +23.83%, Open-domain F1 +18.47%

**효율성 (LoCoMo)**:
- MemoryOS: 토큰 3,874 / LLM 호출 4.9회 / F1 36.23
- A-Mem: 토큰 2,712 / LLM 호출 13.0회 / F1 26.55 → 호출 수 62% 절감, F1 36% 향상
- MemGPT: 토큰 16,977 / LLM 호출 4.3회 / F1 29.13 → 토큰 77% 절감, F1 24% 향상

**Ablation**: MTM 제거가 가장 큰 성능 저하, LPM 제거가 두 번째, 대화 체인 제거가 가장 작은 영향. 전체 시스템의 유기적 협력이 핵심.

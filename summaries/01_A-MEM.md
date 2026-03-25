# A-MEM: Agentic Memory for LLM Agents

> **논문 정보**: Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang (Rutgers University, AIOS Foundation)
> **arXiv**: 2502.12110 (2025.10)
> **코드**: https://github.com/WujiangXu/AgenticMemory / https://github.com/WujiangXu/A-mem-sys

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 에이전트 메모리 시스템은 개발자가 저장 구조·저장 시점·검색 타이밍을 사전에 고정해야 한다. Mem0 등 그래프 DB 기반 시스템도 사전 정의된 스키마에 종속되어 새로운 조직 패턴을 자율적으로 생성하지 못하며, 다양한 태스크에 대한 적응력이 낮고 장기 상호작용에서 효과가 급감한다. |
| **Motivation** | LLM 에이전트가 복잡한 실환경에서 장기 활용되려면 유연한 지식 조직과 지속적 적응이 필수다. 예를 들어 새로운 풀이법을 학습하면 기존 메모리와 창의적으로 연결하고 기존 메모리도 업데이트해야 하는데, 기존 시스템은 이를 지원하지 못한다. LoCoMo 벤치마크(평균 9K 토큰, 최대 35세션)에서 기존 방법들이 멀티홉 추론에 특히 취약함이 확인되었다. |
| **Limitation** | (1) 메모리 조직 품질이 기반 LLM 능력에 좌우되며, 모델마다 생성하는 문맥 설명·연결이 달라질 수 있다. (2) 텍스트 모달리티만 지원하며, 이미지·오디오 등 멀티모달은 미래 과제로 남긴다. (3) 노트 생성·링크 판단·메모리 진화에 각각 별도 LLM 호출이 필요하므로 메모리 저장 단계의 API 비용이 누적 메모리 크기에 비례해 증가한다. (4) 최적 k값이 태스크마다 다르고(Single Hop은 k=50, Multi Hop은 k=40에서 수렴), 실제 배포 시 태스크별 k 튜닝이 필요하다. |

---

## Method

A-MEM은 **Zettelkasten 방법론**에 영감을 받아, 원자적 노트·유연한 링킹 원칙을 LLM 기반 메모리 시스템에 구현한다. 세 가지 핵심 메커니즘으로 구성된다:

1. **Note Construction (노트 생성)**
   - 에이전트가 환경과 상호작용할 때, 각 메모리를 구조화된 노트 `m = {c, t, K, G, X, e, L}`로 생성
   - `c`: 원본 상호작용 내용, `t`: 타임스탬프, `K`: LLM 생성 키워드, `G`: LLM 생성 태그, `X`: LLM 생성 문맥 설명
   - LLM이 프롬프트 `Ps1`을 통해 키워드·태그·문맥 설명을 자동 추출: `K, G, X ← LLM(c ∥ t ∥ Ps1)`
   - 텍스트 인코더(`all-minilm-l6-v2`)로 모든 텍스트 속성을 결합한 임베딩 벡터 `e` 생성

2. **Link Generation (링크 생성)**
   - 새 노트 `m_n` 추가 시, 코사인 유사도로 상위 k개 관련 메모리 `M_near` 검색
   - LLM이 후보 메모리들 간의 의미론적 연결 여부를 분석하여 링크 `L`을 자율 생성
   - 임베딩 기반 검색으로 초기 필터링 → LLM 분석으로 정교한 연결 판단의 2단계 구조
   - 사전 정의된 관계 스키마 없이도 유연한 연결 가능

3. **Memory Evolution (메모리 진화)**
   - 새 메모리 통합 시, 인접 메모리들의 문맥 설명·키워드·태그를 LLM이 자동 업데이트
   - `m*_j ← LLM(m_n ∥ M_near\m_j ∥ m_j ∥ Ps3)`: 기존 메모리가 새 경험을 반영하여 진화
   - 시간이 지남에 따라 고차 패턴(higher-order patterns)을 자동 발견하는 지식 구조 형성

4. **Memory Retrieval (메모리 검색)**
   - 쿼리 텍스트를 동일 인코더로 임베딩 → 코사인 유사도로 상위 k개(기본 k=10) 검색
   - 링크된 메모리도 함께 반환하여, 단순 유사도 검색을 넘어 연관 메모리 네트워크 활용

기존 방법(MemGPT, LoCoMo 등)이 고정된 메모리 접근 패턴에 의존하는 것과 달리, A-MEM은 메모리 조직 자체를 에이전트가 자율적으로 결정한다.

---

## Key Contribution

1. **자율적 메모리 조직**: 사전 설정 없이 에이전트가 메모리 구조를 자율적으로 생성·연결·진화시키는 agentic memory 시스템 제안. 기존의 고정 워크플로우 종속을 탈피.
2. **Link Generation + Memory Evolution 결합**: 두 모듈의 시너지로 단순 유사도 검색을 넘어 고차 패턴을 자동 발견. Ablation에서 두 모듈 모두 제거 시 Multi Hop F1이 27.02 → 9.65로 급락.
3. **극적인 토큰 효율성**: 기존 방법 대비 85~93% 토큰 절감(LoCoMo/MemGPT ~16,900 토큰 → A-MEM ~1,200 토큰)하면서도 성능은 향상.
4. **범용성 검증**: GPT-4o-mini/4o, Qwen2.5-1.5B/3B, Llama 3.2 1B/3B 등 6개 모델에서 모든 베이스라인을 일관되게 초과.

---

## Experiment & Results

**데이터셋**: (1) LoCoMo — 7,512개 QA 쌍, 평균 9K 토큰, 최대 35세션, 5개 카테고리(Multi Hop, Temporal, Open Domain, Single Hop, Adversarial). (2) DialSim — TV 드라마 기반 장기 다자 대화, 약 350K 토큰.

**비교 대상**: LoCoMo(전체 대화 프롬프트 삽입), ReadAgent(에피소드 페이지네이션+요약), MemoryBank(망각 곡선 기반), MemGPT(OS 메모리 계층 모방).

**주요 결과 (GPT-4o-mini, F1)**:
- Temporal: A-MEM **45.85** vs MemGPT 25.52 (+80%), LoCoMo 18.41
- Multi Hop: A-MEM **27.02** vs MemGPT 26.65
- Adversarial: A-MEM **50.03** vs MemGPT 43.29
- 전 카테고리 평균 랭킹 **1.2**로 1위

**DialSim**: A-MEM F1=3.45 vs LoCoMo 2.55 (+35%), MemGPT 1.18 (+192%)

**소형 모델**: Qwen2.5-1.5B에서도 A-MEM이 모든 카테고리 1위(랭킹 1.0). Llama 3.2 1B/3B에서도 동일.

**Ablation (GPT-4o-mini)**:
- w/o LG & ME: Multi Hop F1=9.65, Temporal=24.55, Adversarial=15.32
- w/o ME만: Multi Hop F1=21.35, Temporal=31.24, Adversarial=44.16
- A-MEM 전체: Multi Hop F1=27.02, Temporal=45.85, Adversarial=50.03
→ Link Generation이 기초, Memory Evolution이 추가 향상. 상호 보완적.

**비용/스케일링**: 메모리 작업당 $0.0003 미만, 처리 시간 5.4초(GPT-4o-mini) / 1.1초(Llama 3.2 1B). 메모리 100만 개에서 검색 시간 3.70μs, O(N) 선형 메모리 사용. MemoryBank(1.91μs)보다 약간 느리나 ReadAgent(120,069μs) 대비 압도적.

# Memory in the Age of AI Agents: A Survey — Forms, Functions and Dynamics

> **논문 정보**: Yuyang Hu, Shichun Liu, Yanwei Yue, Guibin Zhang 외 다수 (National University of Singapore, Renmin University of China, Fudan University, Peking University 등)
> **arXiv**: 2025.12 (107페이지)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 에이전트 메모리 연구가 폭발적으로 성장하면서, 동기·구현·가정·평가 프로토콜이 크게 다른 연구들이 "에이전트 메모리"라는 우산 아래 혼재한다. 기존 분류법(long/short-term memory)은 현대 에이전트 메모리 시스템의 다양성과 역동성을 포착하기에 불충분하다. |
| **Motivation** | 2025년의 급격한 방법론 발전(재사용 가능 도구 증류, 메모리 기반 test-time scaling, RL 통합 메모리 등)이 기존 서베이에 반영되지 않았다. "declarative, episodic, semantic, parametric memory" 등 용어의 난립이 개념적 명확성을 저해하고 있어, 통합 분류 체계가 시급하다. |
| **Limitation** | (1) 107페이지로 방대하나, 각 개별 연구에 대한 깊이 있는 비평적 분석보다는 분류 중심의 서술. (2) 분류 체계가 세밀하여 일부 연구가 여러 범주에 걸칠 수 있는 경계 모호성. (3) 빠르게 변화하는 분야 특성상 출판 시점 이후의 발전을 반영하지 못함. (4) 벤치마크 비교가 정성적 커버리지 분석에 치중하여, 정량적 메타 분석은 제한적. |

---

## Method

이 서베이는 에이전트 메모리를 **Forms(형태)**, **Functions(기능)**, **Dynamics(역동성)**의 삼각 프레임워크로 체계화한다.

1. **Forms: 메모리의 표현 형태**
   - **Token-level Memory**: 텍스트 기반 메모리
     - Flat (1D): 벡터 DB, 키-값 저장소, JSON — Mem0, A-MEM 등
     - Planar (2D): 테이블, 그래프, 지식 그래프 — Zep, AriGraph 등
     - Hierarchical (3D): 다층 구조 — MemGPT, MIRIX 등
   - **Parametric Memory**: 모델 파라미터에 인코딩
     - Internal: 모델 가중치 자체에 메모리 통합 — MemoryLLM, SELF-PARAM
     - External: 별도 학습된 외부 파라메트릭 모듈 — M+, Retroformer
   - **Latent Memory**: 잠재 표현 기반
     - Generate: LLM으로 메모리 콘텐츠 생성
     - Reuse: 기존 표현 재활용
     - Transform: 표현 변환을 통한 메모리

2. **Functions: 메모리가 필요한 이유**
   - **Factual Memory**: 사실적 지식 저장
     - User factual memory: 사용자 프로필, 선호, 사실 (개인화)
     - Environment factual memory: 환경/세계 지식 (탐색, 시뮬레이션)
   - **Experiential Memory**: 과거 경험에서 학습
     - Case-based: 과거 trajectory를 few-shot 예시로 검색
     - Strategy-based: 경험에서 전략/인사이트/팁 추출
     - Skill-based: 재사용 가능 도구/API/코드로 경험 증류
     - Hybrid: 여러 유형 결합
   - **Working Memory**: 현재 태스크 내 임시 정보
     - Single-turn: 단일 추론 단계 내 scratch pad
     - Multi-turn: 에이전트 루프 내 중간 상태 유지

3. **Dynamics: 메모리의 시간적 변화**
   - **Memory Formation (형성)**: 환경 상호작용에서 메모리 후보 추출 — `M_{t+1} = F(M_t, φ_t)`
   - **Memory Evolution (진화)**: 새 경험 통합 시 기존 메모리 재구조화 — `M_{t+1} = E(M_t, M^{form}_{t+1})`
   - **Memory Retrieval (검색)**: 태스크 인식 쿼리로 관련 메모리 검색 — `m_t = R(M_t, o_t, Q)`
   - RL 기반 메모리 관리: MemAgent, Memory-R1 등 강화학습으로 메모리 연산 최적화

4. **관련 개념과의 구분**
   - Agent Memory vs LLM Memory: 에이전트 메모리가 LLM 메모리를 거의 포괄
   - Agent Memory vs RAG: RAG는 정적 외부 지식 접근, 에이전트 메모리는 자기 진화적 인지 상태
   - Agent Memory vs Context Engineering: CE는 일시적 자원 관리, 에이전트 메모리는 영속적 축적

---

## Key Contribution

1. **Forms-Functions-Dynamics 통합 분류 체계**: 기존 long/short-term 이분법을 넘어, 형태(토큰/파라메트릭/잠재)·기능(사실/경험/작업)·역동성(형성/진화/검색)의 3축 분류로 현대 에이전트 메모리 연구를 체계화.
2. **개념적 경계 명확화**: Agent Memory, LLM Memory, RAG, Context Engineering의 관계와 차이를 공식적 정의로 명확히 구분.
3. **8대 미래 연구 방향 제시**: 메모리 검색 vs 생성, 자동 메모리 관리, RL 통합, 멀티모달 메모리, 다중 에이전트 공유 메모리, 월드 모델, 신뢰성, 인간 인지 연결.
4. **포괄적 자원 정리**: 대표 벤치마크와 오픈소스 프레임워크를 체계적으로 정리하여 연구자·실무자에게 실용적 참고 자료 제공.

---

## Experiment & Results

서베이 논문으로서 자체 실험 대신 **커버리지 분석**을 수행:

- **분류 대상**: 100편 이상의 에이전트 메모리 관련 논문을 Forms-Functions-Dynamics 프레임워크로 분류
- **벤치마크 정리**: MemoryAgentBench, LOCOMO, LongMemEval, RealTalk, StoryBench 등 메모리 에이전트 전용 벤치마크와 관련 벤치마크(GAIA, SWE-Bench 등)를 역량별로 매핑
- **프레임워크 정리**: Mem0, Zep, Cognee, MemoryOS, MIRIX, Letta 등 오픈소스 메모리 프레임워크의 특성 비교
- **주요 발견**: (1) Token-level memory가 가장 보편적이나 parametric/latent memory가 급성장 중. (2) Experiential memory가 self-evolving 에이전트의 핵심 동력. (3) RL 기반 메모리 관리(MemAgent, Memory-R1 등)가 가장 유망한 신흥 방향

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Taxonomy/분류 체계** | **3축 분류**: (1) Forms — Token-level(1D Flat/2D Planar/3D Hierarchical), Parametric(Internal/External), Latent(Generate/Reuse/Transform). (2) Functions — Factual(User/Environment), Experiential(Case/Strategy/Skill/Hybrid), Working(Single-turn/Multi-turn). (3) Dynamics — Formation, Evolution, Retrieval. |

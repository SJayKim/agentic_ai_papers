# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

> **논문 정보**: Petr Anokhin, Nikita Semenov, Artyom Sorokin, Dmitry Evseev, Andrey Kravchenko, Mikhail Burtsev, Evgeny Burnaev (AIRI Moscow, Skoltech, London Institute for Mathematical Sciences, University of Oxford)
> **arXiv**: 2407.04363 (2025.05, IJCAI 2025)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 에이전트는 전체 관찰 이력, 요약, RAG 등 비구조적 메모리 표현에 의존하여, 복잡한 의사결정에 필수적인 추론과 계획을 효과적으로 지원하지 못한다. 전체 이력을 컨텍스트에 넣는 방식은 비용이 높고, 방대한 정보 속 복잡한 논리를 처리하는 데 한계가 있다. |
| **Motivation** | 자율 에이전트가 새로운 환경에서 지식을 축적하고 업데이트하며 학습하려면, 구조화된 세계 모델(World Model)이 필요하다. 인간의 인지 시스템처럼 의미 기억(일반 지식)과 에피소드 기억(특정 경험)을 통합하면, 공간 탐색·물체 추적·장기 계획에서 비구조적 메모리보다 효과적이다. |
| **Limitation** | (1) 지식 그래프 구축이 LLM의 트리플 추출 능력에 의존하며, 추출 오류가 누적될 수 있다. (2) TextWorld와 NetHack 등 텍스트 게임 환경에서만 검증되어, 실제 세계 태스크에서의 일반화가 불확실하다. (3) 시맨틱 검색 깊이(d)와 너비(w) 등 하이퍼파라미터 튜닝이 필요하며, 환경마다 최적값이 다를 수 있다. (4) Multi-hop QA에서는 전용 방법(HOLMES)에 근접하나 완전히 능가하지는 못한다. |

---

## Method

AriGraph는 **시맨틱 메모리**(지식 그래프)와 **에피소드 메모리**(관찰 이력)를 하나의 통합 그래프 구조로 결합한 월드 모델이다.

1. **그래프 구조 정의**: `G = (Vs, Es, Ve, Ee)`
   - `Vs, Es`: 시맨틱 정점·엣지 — `(객체1, 관계, 객체2)` 트리플 형태의 일반 지식
   - `Ve, Ee`: 에피소드 정점·엣지 — 과거 관찰을 저장하는 하이퍼엣지로, 동시에 추출된 모든 트리플을 하나의 에피소드 정점에 연결

2. **AriGraph 구축 (매 타임스텝)**
   - 새 관찰 `o_t`에서 LLM이 시맨틱 트리플 `(Vs_t, Es_t)` 추출
   - 기존 그래프에서 관련 엣지 `Es_rel`을 조회하여 구식(outdated) 정보 탐지 및 제거
   - 새 트리플로 시맨틱 메모리 확장 + 새 에피소드 정점 `ve_t` 추가

3. **검색 (Algorithm 1: Memory Graph Search)**
   - **시맨틱 검색**: 쿼리와 Contriever 모델로 가장 관련 있는 트리플 검색 → 인접 정점을 재귀적으로 탐색 (깊이 d, 너비 w 제어)
   - **에피소드 검색**: 시맨틱 검색 결과와 연결된 에피소드 정점을 관련성 점수 `rel(ve) = n / max(N,1)·log(max(N,1))`로 순위화하여 상위 k개 반환

4. **Ariadne 에이전트 아키텍처**
   - **Working Memory**: 최근 관찰-행동 이력 + AriGraph에서 검색된 시맨틱·에피소드 메모리
   - **Planning**: Working Memory 기반으로 서브골 생성·업데이트
   - **Decision Making**: ReAct 기반 모듈이 메모리와 계획을 참조하여 행동 선택
   - 매 관찰마다 AriGraph 업데이트 → 학습과 행동이 동시에 진행

기존 RAG·요약·전체 이력 방식과 달리, 구조화된 그래프가 공간 추론과 멀티홉 정보 연결을 직접 지원한다.

---

## Key Contribution

1. **시맨틱+에피소드 통합 메모리 그래프**: 지식 그래프와 에피소드 메모리를 하나의 구조로 결합하여, LLM 에이전트가 상호작용하면서 세계 모델을 자율 구축. 기존 방법들이 두 메모리를 분리하거나 비구조적으로 처리한 한계를 해결.
2. **동적 지식 업데이트**: 매 타임스텝마다 구식 정보를 탐지·제거하고 새 지식을 추가하여, 환경 변화에 적응하는 살아있는 월드 모델 유지.
3. **인간 수준 성능**: TextWorld 환경에서 인간 최고 플레이어에 근접하는 성능 달성, 기존 LLM 메모리 방법과 RL 베이스라인 모두를 크게 초과.
4. **범용성 검증**: 인터랙티브 환경(TextWorld, NetHack)과 정적 QA(MuSiQue, HotpotQA) 양쪽에서 경쟁력 있는 성능.

---

## Experiment & Results

**TextWorld 환경** (Treasure Hunt, Cleaning, Cooking):
- 모든 태스크에서 Ariadne(AriGraph)가 Full History, Summarization, RAG, Simulacra, Reflexion 베이스라인을 크게 초과
- Treasure Hunt: 베이스라인 에이전트는 풀지 못하는 반면, Ariadne는 ~50스텝 만에 해결
- Treasure Hunt Hardest (36방, 7키): Ariadne만 의미 있는 진행 달성
- Cooking: RL 베이스라인 4개 난이도 전부에서 Ariadne 우위. GPT-4 Full History는 처음 2레벨만 해결
- 인간 비교: 평균 인간 플레이어를 모든 태스크에서 초과, 최고 인간 플레이어와 유사한 수준

**NetHack**:
- Ariadne [Room obs]: 제한된 관찰만으로도 전체 레벨 정보를 가진 NetPlay [Level obs]에 근접하는 점수 달성

**Multi-hop QA** (GPT-4, 200 샘플):
- MuSiQue: AriGraph EM=45.0, F1=57.0 vs HOLMES EM=48.0, F1=58.0 vs GraphReader EM=38.0, F1=47.4
- HotpotQA: AriGraph EM=**68.0**, F1=**74.7** vs HOLMES EM=66.0, F1=78.0 vs GraphReader EM=55.0, F1=70.0
- GPT-4o-mini: AriGraph MuSiQue F1=47.9, HotpotQA F1=68.6 vs GraphRAG F1=53.5/63.3

**그래프 스케일링**: 탐색 단계에서 빠르게 성장 후, 환경에 익숙해지면 포화. 장기 상호작용에도 안정적 유지.

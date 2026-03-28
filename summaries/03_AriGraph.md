# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

> **논문 정보**: Petr Anokhin, Nikita Semenov, Artyom Sorokin, Dmitry Evseev, Andrey Kravchenko, Mikhail Burtsev, Evgeny Burnaev (AIRI Moscow, Skoltech, London Institute for Mathematical Sciences, University of Oxford)
> **arXiv**: 2407.04363 (2024) | **학회**: IJCAI 2025
> **코드**: https://github.com/AIRI-Institute/AriGraph

---

## Problem

LLM 기반 에이전트가 동적 환경과 지속적으로 상호작용할 때, 기존 메모리 접근법들은 심각한 한계를 보인다. Full history 방식은 전체 관찰-행동 이력을 컨텍스트에 유지해야 하므로 토큰 비용이 급증하고(150스텝 기준 14,000 프롬프트 토큰), 방대한 정보 속에 숨겨진 복잡한 논리 관계를 처리하기 어렵다. Summarization은 필요한 세부 정보를 손실시키고, RAG는 비구조적 벡터 검색에 의존하여 메모리 전반에 분산된 관련 정보를 효과적으로 연결하지 못한다. Simulacra(Generative Agents)는 recency-importance-relevance 스코어링을 사용하지만 지식의 구조적 표현이 부재하며, Reflexion은 에피소드 간 추가 정보를 활용하지만 장기 기억의 체계적 관리가 미흡하다. 근본적으로, 이러한 비구조적 메모리 표현은 부분 관측 가능 환경(POMDP)에서 요구되는 추론과 계획 수립을 충분히 지원하지 못한다.

---

## Motivation

인간의 기억 체계에서 영감을 받아, 의미 기억(semantic memory)과 일화 기억(episodic memory)을 하나의 지식 그래프 구조로 통합하면 에이전트의 의사결정 능력을 크게 향상시킬 수 있다는 직관에 기반한다. 의미 기억은 환경의 현재 상태에 대한 일반화된 지식을 (object, relation, object) 트리플렛 형태로 구조화하여 공간 탐색과 추론을 지원하고, 일화 기억은 과거 관찰의 구체적 맥락을 보존하여 레시피 내용이나 조리 지시사항 같은 상세 정보를 회상할 수 있게 한다. 핵심적으로 기존 연구들(LARP, Voyager 등)이 의미 기억과 일화 기억을 분리된 인스턴스로 취급하거나 구조적 표현이 부재한 반면, AriGraph는 일화 에지(episodic edge)를 통해 두 기억 체계를 하나의 그래프로 연결한다. 이러한 통합 구조는 "같은 관찰에서 추출된 트리플렛들"이라는 시간적 맥락을 보존하면서도 그래프 탐색 기반의 효율적 검색을 가능하게 한다.

---

## Method

1. **메모리 그래프 구조 (AriGraph)**: G = (Vs, Es, Ve, Ee)로 정의된다. Vs는 의미 정점(객체), Es는 의미 에지(트리플렛 관계), Ve는 일화 정점(각 시간스텝의 관찰 텍스트), Ee는 일화 에지(일화 정점과 해당 관찰에서 추출된 모든 트리플렛을 연결하는 하이퍼에지)이다.

2. **그래프 구축(학습)**: 매 시간스텝 t에서 에이전트가 관찰 ot를 받으면, LLM이 새로운 트리플렛 (object1, relation, object2)을 추출한다. 기존 의미 그래프에서 관련 정점에 연결된 에지 Erel_s를 조회하고, 새 트리플렛과 비교하여 오래된(outdated) 에지를 탐지·제거한 후, 새로운 의미 정점과 에지를 추가한다. 일화 기억은 새 일화 정점 vt_e = ot와 해당 트리플렛들을 연결하는 일화 에지를 추가하여 갱신된다.

3. **의미 검색(Semantic Search)**: 쿼리가 주어지면, 사전학습된 Contriever 모델로 의미 에지 임베딩과의 유사도를 계산하여 가장 관련 있는 트리플렛 top-w개를 검색한다. 검색된 정점들에 대해 BFS 방식으로 깊이 d, 너비 w만큼 그래프를 재귀 탐색하여 관련 지식을 확장 수집한다.

4. **일화 검색(Episodic Search)**: 의미 검색 결과 트리플렛들과 연결된 일화 에지를 통해 과거 관찰을 검색한다. 관련도는 rel(vi_e) = ni / (max(Ni,1) · log(max(Ni,1)))로 계산되며, ni는 입력 트리플렛 중 해당 일화 에지에 연결된 수, Ni는 총 트리플렛 수이다. 트리플렛이 1개뿐인 관찰은 가중치 0으로 처리하여 저정보 관찰을 필터링한다. 상위 k개 일화 정점을 반환한다.

5. **탐색 모듈(Exploration)**: 의미 그래프에서 출구 정보("kitchen, has unexplored exit, south")와 공간 연결 정보를 추출하여, 현재 위치에서 탐색되지 않은 출구를 Algorithm 3으로 식별한다. 이 정보를 작업 기억에 추가하여 체계적 탐색을 지원한다.

6. **인지 아키텍처 (Ariadne)**: 작업 기억(working memory)에 최종 목표, 현재 관찰, 최근 관찰-행동 이력, 의미·일화 검색 결과를 집약한다. Planning LLM 모듈이 작업 기억 내용으로 계획을 생성·갱신하고, ReAct 기반 의사결정 모듈이 실행 가능한 행동을 선택한다.

---

## Key Contribution

1. **의미-일화 통합 메모리 그래프**: 지식 그래프 기반 의미 기억과 관찰 기반 일화 기억을 일화 에지로 통합하는 최초의 구조를 제안하여, 비구조적 메모리 방식의 검색 한계를 해결한다.
2. **동적 월드 모델 학습**: 환경과의 상호작용을 통해 지식 그래프를 점진적으로 구축·갱신하며, 오래된 정보를 자동 탐지·제거하여 POMDP 환경에서의 상태 추적 문제를 해결한다.
3. **확장성 검증**: 환경 복잡도(방 수 12→36개, 키 4→7개)가 증가해도 성능 저하 없이 그래프가 효과적으로 확장됨을 실증한다.
4. **범용성**: 인터랙티브 텍스트 게임용으로 설계되었으나, 멀티홉 Q&A 벤치마크에서도 전용 Q&A 시스템과 경쟁적 성능을 달성하며 GraphRAG 대비 10배 이상 저렴한 비용을 보인다.

---

## Experiment & Results

**TextWorld 텍스트 게임**: Treasure Hunt, Cleaning, Cooking 3종의 게임에서 평가. 각 에이전트는 5회 시도 중 상위 3회 평균으로 측정. Ariadne는 모든 Treasure Hunt 난이도(기본 12방/4키, Hard 16방/5키, Hardest 36방/7키)에서 약 50스텝 내 성공적으로 완료한 반면, 모든 baseline 에이전트(Full history, Summarization, RAG, Simulacra, Reflexion)는 Treasure Hunt를 풀지 못했고 Hardest에서는 두 번째 키조차 찾지 못했다. Cleaning에서도 Ariadne가 Reflexion 포함 모든 baseline을 현저히 초과 달성. Cooking은 중간 단계 오류가 전체 실패로 이어지는 고난이도 과제인데, Ariadne만이 일관되게 완료에 성공했다.

**RL baseline 비교**: Cooking 벤치마크 4개 난이도에서 Ariadne가 모든 RL 에이전트를 상회. GPT-4 Full history는 레벨 1-2만 해결 가능했으나 Ariadne는 전 레벨에서 우수한 성능을 보였다.

**인간 비교**: Ariadne는 평균 인간 플레이어를 모든 과제에서 초과하였고, 상위 3명 인간(Human Top-3)과 비교 시 Cooking과 Treasure Hunt에서 유사한 성능, Cleaning에서는 소폭 하회하였다.

**NetHack**: GPT-4o 기반, Ariadne(Room obs)가 평균 점수 593.00(±202.62), 레벨 6.33(±2.31)을 달성하여, 전체 레벨 정보를 가진 NetPlay(Level obs)의 675.33(±130.27)에 근접했고, 동일 조건의 NetPlay(Room obs) 341.67(±109.14)을 크게 상회하였다.

**멀티홉 Q&A**: MuSiQue에서 AriGraph(GPT-4) EM 45.0 / F1 57.0, HotpotQA에서 EM 68.0 / F1 74.7로 HOLMES(GPT-4)의 EM 48.0/F1 58.0 및 EM 66.0/F1 78.0에 근접. AriGraph(GPT-4o-mini)는 HotpotQA에서 EM 60.0 / F1 68.6으로 GraphRAG(GPT-4o-mini)의 EM 58.7 / F1 63.3을 초과하면서, 토큰 사용량은 GraphRAG의 1/10 수준(11,000 vs 115,000 프롬프트 토큰)이었다.

**토큰 효율성**: 텍스트 게임 기준 Ariadne는 스텝당 프롬프트 6,000 / 완성 500 토큰으로, Full history(150스텝 기준 14,000 토큰)보다 효율적이다.

---

## Limitation

저자가 명시한 한계로, 현재 텍스트 기반 관찰만 지원하며 멀티모달(시각, 음성 등) 관찰의 통합이 필요하다. 또한 절차적 기억(procedural memory)이 부재하여 반복 작업의 효율적 수행에 한계가 있으며, 그래프 검색 알고리즘의 고도화 여지가 있다. 독자 관점에서, 탐색 모듈의 출구 탐지(Algorithm 3)가 위치와 출구에 대한 전문가 지식(expert knowledge)에 의존하므로 범용 환경으로의 이전 시 수동 조정이 필요하다. 트리플렛 추출 품질이 LLM 백본 성능에 크게 의존하며(Fig. 6에서 LLM 품질에 따른 그래프 성장률 차이 확인), 저성능 모델 사용 시 그래프 품질 저하가 예상된다. 그래프 규모가 커질 경우 검색 비용의 확장성 문제와, 현재 평가가 TextWorld와 NetHack이라는 비교적 제한된 환경에 국한되어 있다는 점도 실용화의 제약이다.

# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

> **논문 정보**: Petr Anokhin, Nikita Semenov, Artyom Sorokin, Dmitry Evseev, Andrey Kravchenko, Mikhail Burtsev, Evgeny Burnaev (AIRI Moscow, Skoltech, London Institute for Mathematical Sciences, University of Oxford)
> **arXiv**: 2407.04363 (2024) | **학회**: IJCAI 2025
> **코드**: https://github.com/AIRI-Institute/AriGraph

---

## Problem

LLM 기반 에이전트가 동적 환경과 지속적으로 상호작용할 때, 기존 메모리 접근법들은 장기 의사결정을 충분히 지원하지 못한다.
Full history 방식은 전체 관찰-행동 이력을 컨텍스트에 유지해야 하므로 토큰 비용이 급증하고(150스텝 기준 프롬프트 14,000 토큰), 방대한 정보 속에 숨겨진 복잡한 논리 관계를 파악하기 어렵다.
Summarization은 토큰을 줄이지만 중요한 세부 정보(레시피, 지시문 등)를 손실시켜 중간 단계 오류가 전체 실패로 이어지는 고난이도 과제에서 부적절하다.
RAG는 벡터 유사도 기반의 비구조적 검색에 의존하여, 메모리 전반에 흩어진 관련 사실들을 효과적으로 연결하지 못하며 다단계 추론을 요구하는 질의에서 취약하다.
Simulacra(Generative Agents)는 recency-importance-relevance 스코어링과 reflection을 결합하지만, 지식의 구조적 표현이 부재하여 공간 추론과 상태 추적에 한계가 있다.
Reflexion은 에피소드 간 verbal feedback을 활용하지만, 그래프 기반 상태 관리가 없어 반복 시도에서 성능이 오히려 불안정해진다.
근본적으로, 이러한 비구조적 메모리는 부분 관측 가능(POMDP) 환경에서 요구되는 상태 추적, 체계적 탐색, 다중 홉 추론을 동시에 만족시키지 못한다.

---

## Motivation

인간 기억체계의 이원적 구성(의미 기억-일화 기억)에서 영감을 받아, 두 기억을 하나의 그래프 구조로 통합하면 에이전트 의사결정 품질을 크게 향상시킬 수 있다는 직관에서 출발한다.
의미 기억을 (object, relation, object) 트리플렛으로 구조화하면 공간 연결 관계나 객체 상태를 명시적으로 표현하여 탐색과 추론이 용이해진다.
반면 일화 기억은 과거 관찰의 원본 텍스트(레시피 전문, 조리 지시 등)를 그대로 보존하여, 의미 기억으로는 회수하기 어려운 세밀한 사실을 재현할 수 있게 한다.
기존 연구인 LARP는 의미/일화 기억을 개별 인스턴스로 취급하여 구조적 통합이 없고, Voyager는 스킬 저장소 중심으로 상태 추적이 미흡하다.
AriGraph는 일화 에지(episodic hyperedge)로 두 기억을 연결하여 "같은 관찰에서 함께 추출된 트리플렛 집합"이라는 시간적 맥락을 보존하면서 그래프 탐색 검색을 가능하게 한다.
또한 에이전트가 환경과 상호작용하며 점진적으로 그래프를 구축·갱신하는 world model 학습 과정은, 오래된 상태를 자동 탐지·제거함으로써 POMDP의 상태 변화 추적 문제를 자연스럽게 해결한다.

---

## Method

1. **메모리 그래프 정의**: AriGraph는 G = (Vs, Es, Ve, Ee)로 구성된다. Vs는 의미 정점(객체/개체), Es는 의미 에지((v, rel, u) 트리플렛), Ve는 일화 정점(각 시간스텝의 전체 관찰 텍스트 ot), Ee는 일화 에지(하나의 일화 정점과 해당 관찰에서 추출된 모든 트리플렛을 동시에 연결하는 하이퍼에지)이다.
2. **트리플렛 추출**: 매 시간스텝 t에 관찰 ot가 들어오면 LLM이 구조화된 프롬프트(Appendix E, "subject, relation, object" 포맷, 최대 7단어)로 트리플렛을 추출한다. "you, are in, location" 같은 자기참조 트리플렛과 'none' 엔티티는 명시적으로 배제한다.
3. **outdated 트리플렛 제거**: 새 트리플렛의 정점에 이미 연결된 기존 에지 Erel_s를 후보로 가져와 LLM이 대체 여부를 판정한다. 예컨대 "item, is in, locker"는 에이전트가 그 아이템을 집으면 "item, is in, inventory"로 교체되어 환경 상태 변화를 반영한다.
4. **의미 검색(Semantic Search, Algorithm 2)**: 쿼리 q를 Contriever(또는 Q&A용 BGE-M3)로 임베딩하고 모든 의미 에지와의 dot product로 유사도를 계산하여 top-w 트리플렛을 회수한다. 회수된 에지의 인접 정점을 큐에 넣고 BFS로 깊이 d까지 재귀 확장하여, "grill"로 검색해도 의미적으로 가까운 "bbq, used for, grilling"을 찾을 수 있다.
5. **일화 검색(Episodic Search)**: 의미 검색 결과 트리플렛 집합을 입력으로, 각 일화 에지 ei의 관련도를 rel(vi_e) = ni / (max(Ni,1)·log(max(Ni,1)))로 계산한다. ni는 입력 트리플렛 중 ei에 연결된 수, Ni는 ei가 담고 있는 총 트리플렛 수이다. 트리플렛이 정확히 1개뿐인 관찰은 가중치 0으로 필터링하여 저정보 관찰의 노이즈를 억제하고, 상위 k개 일화 정점(원 관찰 텍스트)을 반환한다.
6. **탐색 모듈(Algorithm 3)**: 의미 그래프에서 "kitchen, has unexplored exit, south" 같은 출구 관련 트리플렛을 수집하고, 현재 위치 vl에서 나가는 에지 중 이미 탐색된 출구와 매칭되는 것을 제거하여 미탐색 출구 집합 Eexp만 남긴다. 보조 에이전트가 계획을 보고 탐색 모드를 on/off 하며 이 정보를 작업 기억에 주입한다.
7. **인지 아키텍처 Ariadne**: 작업 기억에 최종 목표, 현재 관찰, 최근 n개 관찰-행동 이력, 의미 서브그래프, top-k 일화 기억, 기존 계획을 집약한다. Planning LLM은 JSON 포맷({main_goal, plan_steps, your_emotion})으로 서브골을 생성·갱신하되 미완 서브골의 문구/순서 변경을 금지하여 계획 안정성을 유지한다.
8. **ReAct 의사결정**: 최종적으로 ReAct 기반 모듈이 가능한 행동 목록을 보고, 단일 행동으로 해결 가능한 서브골(예: "take X")을 장기 서브골보다 우선하며, 반복 행동 회피 휴리스틱으로 교착 상태를 탈출한다.

---

## Key Contribution

1. **의미-일화 통합 메모리 그래프**: 지식 그래프 기반 의미 기억과 관찰 기반 일화 기억을 일화 하이퍼에지로 연결하는 최초의 구조를 제안하여, LARP/Voyager 등이 해결하지 못한 "구조적 표현 부재 + 두 기억 분리"를 동시에 해소한다.
2. **동적 world model 학습**: outdated 트리플렛 자동 탐지·제거 메커니즘으로 POMDP 환경의 상태 변화를 반영하여, 기존 Q&A용 KG 방법들(GraphRAG, GraphReader 등)이 다루지 못하는 상호작용 기반 지식 업데이트를 가능케 한다.
3. **확장성 실증**: 환경 복잡도가 Treasure Hunt 12방/4키 → Hardest 36방/7키+방해물로 증가해도 성능이 유지되며, 그래프 크기가 탐색 초기에 빠르게 포화 후 안정화되는 학습 곡선을 보였다.
4. **범용성과 비용 효율**: 텍스트 게임용으로 설계되었으나 정적 멀티홉 Q&A에서도 경쟁력을 가지며, HotpotQA에서 GraphRAG보다 토큰 사용량이 10배 이상 저렴하다(11,000 vs 115,000 프롬프트).
5. **RL·인간 대비 우위**: 전문 설계된 RL 에이전트와 평균 인간 플레이어를 모두 능가하여, 구조적 메모리만으로도 에이전트가 "scratch로부터" 유용한 world model을 학습 가능함을 입증한다.

---

## Experiment

**TextWorld 게임 3종**: Treasure Hunt(기본/Hard/Hardest: 12방·4키/16방·5키/36방·7키+방해물), Cleaning(9방, 11개 오배치 아이템), Cooking(9방·3재료 / 12방·4재료 / Hardest는 닫힌 문·인벤토리 관리 포함). 각 에이전트는 5회 중 상위 3회 평균으로 측정.
**주요 정규화 점수(Table 4)**: Treasure Hunt 기본/Hard/Hardest에서 AriGraph 1.0/1.0/1.0, Full History 0.47/-/-, Summary 0.33/0.17/-, RAG 0.33/0.17/-, Simulacra 0.4/-/-, Reflexion 0.93/-/-. Cooking 기본/Hard/Hardest에서 AriGraph 1.0/1.0/0.65 vs Full History 0.18, Summary 0.52/0.21, Reflexion 1.0(2-shot). Cleaning에서 AriGraph 0.79 vs Simulacra 0.7, Reflexion 0.27.
**Ablation**: AriGraph w/o exploration은 Treasure Hunt 0.87로 탐색 모듈 기여가 명확하고, w/o episodic은 Cooking 기본 0.64 / Hard 0.45로 일화 기억 제거 시 레시피 회상 실패로 성능이 급락한다. LLaMA-3-70B 백본은 Treasure Hunt 0.47 / Cooking 0.67로 떨어져 LLM 품질 의존성을 보인다.
**RL 비교(Cooking 4단계)**: Ariadne가 레벨 1~4 전체에서 RL baseline을 상회, GPT-4 Full History는 레벨 1~2만 해결.
**인간 비교**: AriGraph는 All Humans(평균) 대비 Cooking(1.0 vs 0.32), Treasure Hunt(1.0 vs 0.96), Cleaning(0.79 vs 0.59) 모두 초과.
Human Top-3와는 Cooking·Treasure Hunt 동률, Cleaning에서는 소폭 하회.
**NetHack(GPT-4o, Table 1)**: Ariadne(Room obs) 593.00±202.62점 / 6.33±2.31 레벨로, 레벨 오라클을 가진 NetPlay(Level obs) 675.33±130.27 / 7.33±1.15에 근접.
같은 제한 조건의 NetPlay(Room obs) 341.67±109.14 / 3.67±1.15을 큰 폭으로 능가.
**멀티홉 Q&A(200 샘플)**: MuSiQue에서 AriGraph(GPT-4) EM 45.0 / F1 57.0, HotpotQA에서 EM 68.0 / F1 74.7로 HOLMES(GPT-4) EM 48.0/58.0, EM 66.0/78.0에 근접.
AriGraph(GPT-4o-mini)는 HotpotQA EM 60.0 / F1 68.6으로 GraphRAG(GPT-4o-mini) EM 58.7 / F1 63.3을 초과.
**토큰 비용(Table 3)**: 텍스트 게임 스텝당 Ariadne 프롬프트 6,000 / 완성 500, Simulacra 7,500 / 400, Full history(스텝 150) 14,000 / 350.
Q&A 태스크당 AriGraph 11,000 / 2,500 vs GraphRAG 115,000 / 20,000.

---

## Limitation

저자는 현재 시스템이 텍스트 관찰만 처리하며 시각·음성 등 멀티모달 통합이 미흡하다고 명시한다.
절차적 기억(procedural memory)이 부재하여, 반복되는 조리 절차나 탐색 루틴을 매번 재계산해야 하므로 장기간 운영 시 비효율이 누적된다.
독자 관점에서, 탐색 모듈의 Algorithm 3은 "location"과 "exit"를 판별하는 RepresentExit 함수에 전문가 지식이 하드코딩되어 있어, 새로운 도메인(로봇 시뮬레이션, 웹 에이전트 등)으로 이전할 때 수동 조정이 필요하다.
Fig. 6에서 LLM 백본 품질이 낮을수록 그래프 성장률이 과잉 증가(노이즈·중복 트리플렛)하는 현상이 관찰되어, GPT-4o-mini 이하 모델에서는 그래프 품질 저하와 outdated 판정 오류가 누적될 위험이 크다.
그래프가 대규모로 성장할 경우 BFS 기반 semantic search의 비용이 비선형 증가할 수 있으나 이에 대한 압축·가지치기 정책이 제시되지 않았다.
평가 환경이 TextWorld, NetHack, 정적 Q&A 2종으로 제한되어 있어, 실세계 웹/로봇 과제처럼 노이즈가 많고 관찰이 불완전한 도메인에서의 일반화는 추가 검증이 필요하다.
마지막으로 5회 시도 중 상위 3회 평균이라는 평가 방식은 실패 시나리오(분산, 최악 케이스)를 과소 표현할 수 있어 실서비스 신뢰도 지표로는 보완이 필요하다.

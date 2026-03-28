# Learning to Continually Learn via Meta-learning Agentic Memory Designs (ALMA)

> **논문 정보**: Yiming Xiong, Shengran Hu, Jeff Clune (University of British Columbia, Vector Institute, Canada CIFAR AI Chair)
> **arXiv**: Preprint (2026.02.10) | **학회**: Preprint
> **코드**: https://github.com/zksha/alma

---

## Problem

Foundation Model(FM) 기반 에이전트 시스템은 추론 시 상태를 유지하지 못하는 stateless 특성으로 인해, 과거 경험을 축적하고 지속적으로 학습하는 능력이 근본적으로 제한된다. 이를 해결하기 위해 메모리 모듈을 도입하지만, 기존 메모리 설계는 대부분 인간이 수작업으로 설계(hand-crafted)하며, 특정 도메인에 고정된 구조를 사용한다. 대화형 에이전트는 사용자 선호도를 저장해야 하고, 전략 게임에서는 추상적 전략을 추출해야 하는 등, 도메인마다 최적의 메모리 설계가 근본적으로 다르다. 따라서 각 도메인에 맞는 최적 메모리 설계를 수동으로 식별하는 것은 비효율적이고 노동 집약적이며, 실세계 태스크의 다양성과 비정상성(non-stationarity)에 적응하기 어렵다. 기존 자동 에이전트 설계(ADAS, AgentSquare 등)는 일회성(one-shot) 성능만 최적화하여 지속 학습을 위한 메모리 설계에 적합하지 않고, 동시기 연구는 기존 수작업 설계에 의존한 초기화와 탐욕적 선택으로 open-ended 탐색이 제한된다.

---

## Motivation

머신러닝 역사에서 수작업 컴포넌트는 결국 학습된 컴포넌트로 대체되어 왔다는 반복적 패턴(예: 수작업 피처 → 학습된 표현)에서 핵심 직관을 얻는다. 메모리 설계 역시 이 패러다임을 따를 수 있다는 관찰이 ALMA의 출발점이다. 코드를 탐색 공간으로 사용하면 데이터베이스 스키마, 검색 메커니즘, 업데이트 규칙 등 이론적으로 임의의 메모리 설계를 발견할 수 있다. Open-ended exploration은 탐욕적 선택보다 고성능 구조를 발견하는 데 유리하다는 선행 연구(Lehman & Stanley 2008, 2011)에 기반하여, 중간 성능의 설계가 최적 설계로 진화하는 디딤돌(stepping stone) 역할을 할 수 있다. 이는 기존의 greedy selection 방식과 근본적으로 다른 접근으로, 즉각적인 성능 향상이 없더라도 잠재력 있는 설계를 보존하여 장기적으로 더 나은 메모리 구조를 발견할 수 있게 한다.

---

## Method

1. **메모리 설계 추상화**: 메모리 설계를 Python Abstract Class로 정의한다. 각 설계는 여러 sub-module로 구성되며, 각 sub-module은 자체 데이터베이스(dictionary, embedding 기반 등)를 가질 수 있다. `general_update`(경험 저장/요약)와 `general_retrieve`(지식 검색) 두 핵심 인터페이스를 통해 에이전트 시스템과 상호작용한다.

2. **평가 프로토콜 (Memory Collection → Deployment)**: 메모리 설계를 두 단계로 평가한다. Memory Collection Phase에서 에이전트가 태스크를 수행하며 메모리를 축적하고, Deployment Phase에서 축적된 메모리를 활용하여 새로운 태스크를 해결한다. Deployment Phase는 메모리를 고정하는 static 모드와 동적 업데이트하는 dynamic 모드로 나뉜다. 학습 시에는 분산 감소를 위해 static 모드만 사용한다.

3. **Open-Ended Exploration**: (i) 아카이브를 빈 메모리 설계 템플릿(Abstract Class)으로 초기화한다. (ii) Meta Agent가 아카이브에서 최대 5개의 이전 설계를 비복원 추출(sampling without replacement)한다. (iii) 샘플링된 설계의 코드와 평가 로그를 반영(reflect)하여 새로운 아이디어와 계획을 생성한다. (iv) 새 설계를 코드로 구현하고, 검증 및 평가를 수행한다. 오류 발생 시 최대 3회 self-reflection으로 수정한다. (v) 평가된 설계를 아카이브에 추가하고, 최대 반복 횟수까지 과정을 반복한다.

4. **샘플링 전략**: 아카이브에서 설계를 샘플링할 때, 성능이 가장 높은 설계만 선택하는 greedy 방식이 아니라, 다양한 성능 수준의 설계를 샘플링하여 open-ended 탐색을 유지한다. 중간 성능 설계가 핵심 메커니즘 도입 시 최적 설계로 진화할 수 있는 stepping stone 역할을 한다.

5. **Meta Agent 구성**: Meta Agent는 GPT-5로 구동되며, 에이전트 시스템 평가에는 GPT-5-nano를 사용한다. Meta Agent는 GPT-4o-mini, GPT-4.1, text-embedding-3-small을 도구로 사용하여 인사이트 추출, 시맨틱 유사도 계산 등의 워크플로우를 탐색할 수 있다.

6. **학습 규모**: 11 learning step에 걸쳐 총 43개의 메모리 설계를 탐색하며, 최고 성능 설계를 최종 학습된 메모리 설계로 선택한다.

---

## Key Contribution

1. **메모리 설계의 자동 학습 프레임워크**: 수작업 메모리 설계를 코드 공간에서의 open-ended exploration으로 대체하는 최초의 체계적 프레임워크를 제안하여, 도메인별 수동 튜닝의 한계를 해결한다.

2. **도메인 적응형 메모리 자동 발견**: ALMA가 각 도메인의 요구에 맞춰 자동으로 특화된 메모리 설계를 발견함을 실증한다 (예: ALFWorld는 공간 관계 그래프, Baba Is AI는 전략 라이브러리).

3. **모든 벤치마크에서 SOTA 초과 달성**: 4개 sequential decision-making 벤치마크 전체에서 학습된 메모리 설계가 모든 수작업 baseline을 일관되게 상회한다.

4. **FM 간 전이성 실증**: GPT-5-nano에서 학습된 메모리 설계가 GPT-5-mini로 전이 시 더 큰 성능 향상을 보이며(12.8% vs 6.2%), 더 강력한 FM일수록 학습된 메모리 설계의 이점이 크다.

5. **Open-ended exploration의 우위성 입증**: Greedy selection 대비 open-ended exploration이 더 나은 메모리 설계를 학습함을 ablation으로 검증한다.

---

## Experiment & Results

**벤치마크**: ALFWorld(가사 태스크), TextWorld(텍스트 어드벤처), Baba Is AI(전략 퍼즐), MiniHack(던전 탐험) 등 4개 sequential decision-making 도메인에서 평가.

**Baseline**: Trajectory Retrieval, Reasoning Bank, Dynamic Cheatsheet, G-Memory 등 4개 SOTA 수작업 메모리 설계.

**GPT-5-nano 결과**:
- ALMA 전체 평균 성공률 **12.3%**, no-memory 대비 **+6.2%p** 향상. 모든 수작업 baseline(최고 8.6%) 대비 우위.
- ALFWorld: 12.4% (no-memory 2.9% 대비 +9.5%p), 최고 baseline G-Memory 7.6% 대비 +4.8%p.
- TextWorld: 6.2% (no-memory 5.4% 대비 +0.8%p), 유일하게 no-memory 초과 달성.
- Baba Is AI: 19.0% (no-memory 9.5% 대비 +9.5%p), Trajectory Retrieval과 동률.
- MiniHack: 11.7% (no-memory 6.7% 대비 +5.0%p), 최고 baseline Reasoning Bank 9.8% 대비 +1.9%p.

**GPT-5-mini 전이 결과**:
- ALMA 전체 평균 성공률 **53.9%**, no-memory 대비 **+12.8%p** 향상. 최고 baseline Trajectory Retrieval 48.6% 대비 +5.3%p.
- ALFWorld: **87.1%** (no-memory 67.6% 대비 +19.5%p).
- TextWorld: **75.0%** (no-memory 60.5% 대비 +14.5%p).

**스케일링**: ALFWorld에서 Memory Collection 태스크 수 증가에 따라, ALMA는 적은 데이터에서 더 빠르게 높은 성능에 도달하고, 수작업 baseline보다 더 효과적으로 스케일링.

**비용 효율성**: ALMA의 end-to-end 메모리 비용은 전체 벤치마크 합산 **$0.09**, 검색 콘텐츠 토큰 크기 **1,319 tokens**로, Trajectory Retrieval($1.5+, 9,149 tokens)이나 G-Memory(6,095 tokens) 대비 훨씬 효율적이면서 최고 성능 달성.

**Ablation**: Open-ended exploration이 greedy selection 기반 최적화보다 더 나은 메모리 설계를 학습함을 확인.

---

## Limitation

저자가 명시한 한계로, 현재 ALMA는 메모리 설계만을 학습하며 에이전트 시스템 전체(프롬프트, 도구 사용 등)를 함께 최적화하지 않는다. 또한 코드 공간에서의 메모리 설계 학습은 기반 FM의 코드 생성 능력에 의존하므로, FM의 한계가 곧 탐색 공간의 한계가 된다. 비용 효율성을 명시적으로 최적화하지 않아, multi-objective optimization 도입 시 더 나은 효율-성능 트레이드오프가 가능할 것이다. 실험이 텍스트 기반 sequential decision-making 4개 도메인에 한정되어, 실세계 응용(의료, 금융 등)이나 멀티모달 환경에서의 일반화는 미검증이다. Meta Agent가 GPT-5를 사용하므로 메타 학습 자체의 비용이 상당하며, 학습된 메모리 설계의 해석 가능성이나 안전성 보장에 대한 체계적 방법론이 부재하다. 11 step × 43개 설계라는 비교적 작은 탐색 규모에서의 결과이므로, 대규모 탐색 시의 행동은 추가 검증이 필요하다.

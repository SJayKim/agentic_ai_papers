# τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

> **논문 정보**: Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra AI, Princeton University)
> **arXiv**: 2406.12045 (2024.06)
> **코드**: https://github.com/sierra-research/tau-bench

---

## Problem

기존 언어 에이전트 벤치마크는 에이전트가 도구(API)를 정확히 호출하는지 평가하거나, 혹은 사용자와의 대화를 평가하는 두 흐름으로 나뉘어 왔다.
그러나 실세계 고객 서비스 에이전트는 도구 호출, 다턴 인간 대화, 도메인 정책 준수를 동시에 수행해야 한다.
ToolBench, MetaTool, ToolEmu 등은 단일 턴 사용자 지시만 다루고, MultiWOZ 같은 대화 벤치마크는 정적인 과거 궤적에 한정되어 실시간 도구 호출이 빠져 있다.
또한 대부분의 기존 벤치마크는 평균 성공률(pass^1)만 보고하여, 동일 태스크를 반복했을 때의 안정성(reliability)을 정량화하지 못한다.
실세계 배포 환경에서는 동일한 요청이라도 매번 다른 표현·대화 흐름으로 제공되므로, 확률적 변이 하에서 일관되게 정책을 준수하는 능력이 핵심이다.
기존 체계는 이 세 요소(도구-대화-정책) 및 일관성이라는 네 번째 축을 통합적으로 평가하지 못한다는 근본적 공백이 있다.
이로 인해 최신 function calling 에이전트가 실제로 얼마나 프로덕션에 준비되어 있는지 판단할 근거가 부족하다.

---

## Motivation

저자들은 "에이전트가 수백만 번의 상호작용 중 단 한 번도 정책을 위반해서는 안 된다"는 기업용 요구사항을 벤치마크 설계의 출발점으로 삼는다.
항공권 예약 예시에서 에이전트는 사용자의 의도를 다턴으로 파악하고, 기내 등급·회원 등급·수하물 등의 복잡한 ad-hoc 규칙을 체크하며, 복합 트랜잭션(예: cancel 후 rebook)을 원자적으로 수행해야 한다.
이런 설정에서 LM self-reflection이나 Tree-of-Thoughts 같은 무거운 추론은 실시간 서비스에 부적합하므로, function calling/ReAct 같은 경량 아키텍처가 실제로 얼마나 버티는지 측정해야 한다.
Sierra AI 팀은 시뮬레이션 사용자(LM 기반)와 실 DB를 결합하면, 주관적 human judging 없이도 DB 상태 비교만으로 객관적이면서도 재현 가능한 평가가 가능하다는 통찰을 제시한다.
또한 k번 i.i.d. 시도 모두 성공해야 하는 pass^k라는 새 지표를 통해, 코드 생성의 pass@k와는 정반대 방향(일관성)을 정량화한다.
τ-retail과 τ-airline 두 도메인을 공개하여 커뮤니티가 더 복잡한 의료·법률·세무 등으로 확장할 수 있는 모듈형 프레임워크를 제시한다.

---

## Method

### 1. POMDP 형식화
- 각 태스크를 (S, A, O, T, R, U) POMDP로 정의.
- 상태 S = S_db ⊗ S_user: 데이터베이스 상태와 시뮬레이션 사용자 상태의 결합.
- 행동 A = A_db ∪ A_user: 도구 호출과 사용자 메시지 송신 두 채널.
- 관찰 O = O_db ∪ O_user: DB API 반환값과 사용자 발화.

### 2. 데이터베이스와 API 계층
- DB 내용 s_db는 에이전트·사용자 모두에게 숨겨져 있고, Python 함수로 구현된 tool_name(**kwargs) API로만 접근.
- transition T_db는 결정론적 Python 함수로 구현되어, 동일 action에는 동일 결과가 보장된다.
- 일부 제약(예: 결제 수단 유효성)은 API 내부 체크로, 일부(예: 확인 후 실행)는 정책 문서로 분리.

### 3. 도메인 정책 문서 (partial world model)
- Markdown 형식의 자연어 규칙 문서를 시스템 프롬프트로 주입.
- 예: τ-retail "Exchange or modify order tools can only be called once", τ-airline "Basic economy cannot be modified".
- 에이전트는 이 정책 + API schema만 직접 접근, DB는 오직 API 경유 간접 접근.

### 4. 태스크 인스턴스 구조
- 두 부분: 사용자 시뮬레이터용 instruction(에이전트 비공개) + ground truth DB write actions 및 required outputs.
- instruction은 사용자 identity, intent, preference를 명시해 도메인 정책 하에서 유일한 DB 결과가 산출되도록 설계.

### 5. 보상 함수
- r = r_action × r_output ∈ {0, 1}.
- r_action: 에피소드 종료 시점 DB 상태가 ground truth와 완전 일치하는지.
- r_output: 에이전트의 사용자 응답이 필수 정보(예: "54.04", "41.64")를 substring으로 포함하는지.
- rule-based이므로 빠르고 재현 가능하나, 필요조건일 뿐 충분조건은 아님(무확인 실행 같은 위반은 놓칠 수 있음).

### 6. pass^k 메트릭
- 코드 생성의 pass@k = 1 − E[C(n−c, k)/C(n, k)]와 대비되는 pass^k = E[C(c, k)/C(n, k)].
- k번 i.i.d. 시도 전부 성공해야 성공으로 간주하는 엄격한 신뢰성 지표.
- 동일 태스크에서 사용자 LM과 에이전트 LM의 확률적 샘플링이 자연스러운 대화 변이를 생성.
- 기본 보고 지표는 pass^1 = pass@1 = E[r].

### 7. 3단계 벤치마크 구축 파이프라인
- Stage I — 수작업: DB 스키마, API Python 구현, 정책 Markdown을 실세계 사례를 단순화하여 공동 설계.
- Stage II — LM 자동 생성: gpt-4가 샘플 entry를 주면 대규모 DB를 생성하는 code snippet을 만들어 수동 디버깅.
- Stage III — 수동 검증: gpt-4-turbo FC agent로 각 태스크 40회 이상 시도 → 낮은 성공률 태스크를 재검토 → user instruction 모호성 제거 → ground truth action/output 확정.

### 8. 두 도메인 사양
- τ-retail: 500 users, 50 products, 1,000 orders / 7 write + 8 non-write API / 115 태스크.
- τ-airline: 500 users, 300 flights(20개 미국 도시), 2,000 reservations / 6 write + 7 non-write API / 50 태스크.
- 비-DB 도구: calculate, transfer_to_human_agents.

### 9. 에이전트 구현 (baseline)
- Function Calling (FC): 네이티브 지원 모델의 기본 모드. 시스템 프롬프트 = 도메인 정책, 매 턴 메시지/도구 호출 자율 결정.
- ReAct: "Thought: {reasoning} Action: {JSON}" 텍스트 포맷.
- Act-only: 추론 없이 action JSON만 출력하는 ablation.
- 각 태스크당 최대 30 에이전트 액션 제한.
- self-reflection, ToT 같은 다회 시도 필요 방법론은 real-time customer service 설정과 맞지 않아 제외.

### 10. 평가 프로토콜
- 총 12개 LM(gpt-4o, gpt-4-turbo, gpt-4-32k, gpt-3.5-turbo, claude-3-opus/sonnet/haiku, gemini-1.5-pro/flash, mistral-large, mixtral-8x22b, meta-llama-3-70B).
- 사용자 시뮬레이터는 gpt-4로 고정.
- pass^k 측정을 위해 동일 태스크 반복 실행, k={1, 2, 4, 8, 16, 32}에서 곡선 보고.

---

## Key Contribution

1. **Tool-Agent-User 3자 상호작용 벤치마크 최초 제안**: 도구 호출 + 다턴 대화 + 도메인 정책을 한 프레임워크에서 동시 평가.
2. **pass^k 신뢰성 메트릭 도입**: k번 모두 성공해야 하는 엄격한 지표로 에이전트 일관성을 정량화, 코드 생성의 pass@k와 철학적으로 반대되는 axis를 제시.
3. **DB 상태 기반 객관 평가**: LM judge나 human rater 없이 확정적 Python transition + 고유 outcome 설계로 fast·faithful·reproducible 평가 체계 구축.
4. **모듈형 3단계 구축 파이프라인**: 수작업 스키마 설계 + LM 대규모 데이터 생성 + 40회 이상 trial 기반 검증으로 고품질·확장 가능한 벤치마크 생산 방법론 확립.
5. **실패 유형 taxonomy**: gpt-4o FC 실패 36건을 Wrong argument(19.4%), Wrong info(25.0%), Wrong decision(22.2%), Partial resolution(33.3%) 4범주로 분류하여 향후 연구 방향 제시.
6. **두 공개 도메인 (τ-retail, τ-airline)**: 165개 고품질 태스크와 전체 코드·데이터 오픈소스 공개로 커뮤니티 확장 가능성 확보.

---

## Experiment

- **τ-retail pass^1 (FC)**: gpt-4o 61.2%, gpt-4-turbo 57.7%, gpt-4-32k 56.5%, claude-3-opus 44.2%, mistral-large 30.7%, claude-3-sonnet 26.3%, gemini-1.5-pro 21.7%, gpt-3.5-turbo 20.0%, claude-3-haiku 19.0%, mixtral-8x22b 17.7%, gemini-1.5-flash 17.4%, llama-3-70B 14.8%.
- **τ-airline pass^1 (FC)**: gpt-4o 35.2%, claude-3-opus 34.7%, gpt-4-32k 33.0%, gpt-4-turbo 32.4%, mixtral-8x22b 31.6%, claude-3-sonnet 27.6%, gemini-1.5-flash 26.0%, mistral-large 22.4%, gemini-1.5-pro 14.0%, claude-3-haiku 14.4%, llama-3-70B 14.4%, gpt-3.5-turbo 10.8%.
- **pass^k 급락**: gpt-4o τ-retail pass^1 ≈ 61% → pass^8 < 25% → pass^32 은 추가 하락; 모든 모델에서 k 증가에 따라 기하급수적으로 감소.
- **방법론 비교 (τ-retail)**: 동일 모델에서 FC > ReAct > Act-only 일관 우위. ReAct가 Act-only 대비 reasoning trace로 action 포맷 간극을 메꿈.
- **"think" function 추가**: FC 모델에 think 도구를 추가해도 성능 향상 없음 — FC 모델이 그런 추론 훈련을 받지 않았기 때문으로 추정.
- **정책 ablation (table 3)**: 정책 제거 시 τ-retail gpt-4o 61.2 → 56.8 (−4.4%p), gpt-3.5 20.0 → 14.5 (−5.5%p); τ-airline gpt-4o 33.2 → 10.8 (−22.4%p), gpt-3.5 10.8 → 9.6 (−1.2%p). 복잡 규칙 도메인일수록 policy 의존도 급증.
- **실패 분류 (115 태스크 중 40 failure)**: 4건은 instruction 결함으로 수정, 나머지 36건 중 Partial resolution 33.3%, Wrong info 25.0%, Wrong decision 22.2%, Wrong argument 19.4%.
- **Hallucination rate (τ-retail 태스크당 비존재 ID 도구 호출)**: gpt-4o FC 0.46회, gpt-3.5-turbo FC 2.08회, gpt-3.5-turbo Act 6.34회.
- **복합 요청 난이도 (Figure 6)**: ground truth write action 수가 많을수록 성공률 급락 — 0~1건 task는 고성공률, 4건 이상 task는 성공률 거의 0으로 수렴.
- **비용 분석**: gpt-4o FC agent + gpt-4 user simulation τ-retail 1 trial 당 agent $0.38, user $0.23 → 전체 태스크 1회전 약 $200. 에이전트 비용의 95.9%가 input prompt, 4.1%만 completion (긴 policy + function schema 탓).
- **태스크 난이도 분포 (Figure 7)**: τ-retail 태스크가 0~100% 성공률에 걸쳐 잘 분산되어 있어, 단순/복잡 평가 범위가 균형 잡힘.

---

## Limitation

저자들이 명시적으로 인정하는 시뮬레이션 사용자의 세 가지 한계가 있다.
첫째, 사용자 instruction에 typo나 모호성이 남을 수 있다 — Stage III 검증에서 일부 수정했지만 40회 trial로도 모든 ambiguity를 잡지 못했다.
둘째, 사용자 instruction이 도메인 지식을 전부 담지 못해, §C.2.1처럼 사용자가 "한 번만 교환 가능"이라는 규칙을 모른 채 부분 교환을 승인하는 사례가 발생한다.
셋째, user simulation LM 자체가 수치 계산이나 long-context 기억, 프롬프트 정렬에서 취약해 §C.2.2처럼 추천된 램프의 스펙을 재확인 없이 수락하기도 한다.
도메인은 τ-retail과 τ-airline 두 개로 한정되며 의료·법률 등 고난이도 영역은 미포함이다.
pass^1 보상은 DB 상태 일치만 검사하므로, "사용자 확인 없이 실행" 같은 정책 위반을 완전히 포착하지 못한다 (필요조건이지 충분조건 아님).
태스크 curation에 gpt-4-turbo FC 에이전트를 사용해 user prompt를 튜닝했으므로 해당 모델 계열에 유리한 implicit bias가 있을 수 있다.
self-reflection, ToT 같은 무거운 방법론을 real-time 설정 부적합 이유로 제외했지만, 이들이 적절히 적응되었을 때의 상한선은 측정하지 못했다.
LM judge 기반 부가 rule-following check나 LM-as-critic 평가도 미구현이며, 저자들은 이 확장을 future work로 남긴다.

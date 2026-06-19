# 89. ComplexMCP: Evaluation of LLM Agents in Dynamic, Interdependent, and Large-Scale Tool Sandbox

> 📄 **저자**: Yuanyang Li, Xue Yang, Longyue Wang, Weihua Luo, Hongyang Chen (Zhejiang University, Zhejiang Lab, Alibaba Group)
> 📚 **학회/발표 기관**: arXiv preprint (Alibaba)
> 📅 **발표 날짜**: 2026.05
> 🔗 **arXiv**: https://arxiv.org/abs/2605.10787
> 💻 **코드**: https://github.com/AIDC-AI/complex-mcp

---

## Problem

현재 LLM 에이전트는 고립된(isolated) API를 호출하는 데는 능숙하지만, 상용 소프트웨어 자동화의 "라스트 마일(last mile)"에서 무너진다.
실세계 도구는 서로 독립적이지 않으며, 원자적(atomic)이고 상호의존적(interdependent)이며 환경 노이즈에 취약하다.
구체적으로 엔터프라이즈 환경에서 에이전트는 수백~수천 개의 추상적이고 세분화된 API를 다뤄야 하고, 이들은 파라미터 전달·상태 관리·접근 제어·인증 측면에서 강한 상호의존성을 가진다.
예를 들어 LightTalk에서 "메시지 전송" 하나를 성공시키려면 네트워크 가속 시작 → 대상 UID 해석 → 차단 여부 확인·해제 → 권한 요청이라는 다단계 선행 작업이 필요한데, 기존 에이전트는 이런 잠재(latent) 선행 도구를 호출하지 못한다.
또한 API는 비결정적 실패(네트워크 지연, 일시적 오류)를 일으키므로 에이전트는 오류를 감지하고 대체 경로를 능동적으로 탐색해야 하지만, 현재 모델은 이런 stateful·noisy·interdependent 조건에서 어떤 상황에서 왜 실패하는지 체계적으로 측정된 적이 없다.
기존 벤치마크(ToolBench, AnyToolBench, BFCL, τ-Bench, MCPEval 등)는 대규모이지만 도구가 독립적이거나, 실행 환경을 시뮬레이션하지 않거나(AST 매칭), 도메인·도구 수가 적고 환경이 정적으로 미리 정의되어 실세계의 모호성과 복잡성을 결여한다.

---

## Motivation

핵심 직관은 실세계 소프트웨어 자동화의 난이도가 "개별 API 호출 정확도"가 아니라 "상호의존적 도구 체인을 동적·비결정적 환경에서 끝까지 완수하는 능력"에서 나온다는 것이다.
따라서 (1) 대규모 도구셋(300+), (2) 도구 간 잠재 의존성·stateful 전이, (3) 환경 확률성(API 실패·노이즈 주입), (4) 결정론적·재현 가능한 평가를 동시에 갖춘 샌드박스가 필요하다.
저자들은 환경 로직(구조)과 콘텐츠(인스턴스)를 분리하면, 단일 seed로 환경의 다양성과 비결정성을 주입하면서도 완벽한 과학적 재현성을 유지할 수 있다고 관찰했다.
또한 사후 검증을 LLM-as-a-judge에 맡기면 주관성과 편향이 개입하므로, 환경 상태 전이를 ground truth와 비교하는 규칙 기반 평가가 fine-grained 실패 분석에 필수적이라고 보았다.
이를 통해 단순 이진 성공/실패를 넘어 어떤 도구를 빠뜨렸는지, 어떤 부수효과(collateral damage)를 일으켰는지까지 진단할 수 있는 testbed를 만들고자 했다.

---

## Method

ComplexMCP는 Model Context Protocol(MCP) 위에 구축되며, 태스크를 "Seed-driven Goal-oriented Trajectory" 문제로 형식화한다.

1. **문제 형식화**: 태스크를 튜플 M = ⟨S, T, I, σ, G, Φ⟩로 정의한다.
S는 상태공간, T는 n개 원자 MCP 도구셋(각 도구 t: S×A → S×O), I는 자연어 지시, σ는 확률성을 결정론적으로 통제하는 랜덤 seed, G는 목표 상태, Φ는 평가 함수다.

2. **도구 생태계 규모**: 총 15개 MCP 서버에서 315개 도구를 제공한다.
이 중 7개 stateful 서버(LightOS, LightTalk, LightShop, LightWeather, LightFlight, LightStock, LightNews)가 150개 이상의 상호의존 도구를, 8개 stateless 서버(Math, Crypto, Chem, Time, Network, String, Unit, Graph)가 150개 이상의 독립 도구를 제공한다.

3. **Stateful vs Stateless**: stateless 서버는 수학 계산·단위 변환처럼 호출 간 데이터를 유지하지 않는 원자적 도구다.
stateful 서버는 채팅·거래 이력 등을 담은 고차원 중첩 딕셔너리를 세션 스토어로 유지하며, 부수효과를 가진 행동(메시지 전송, 장바구니 수정)은 결정론적 상태 전이 S_{t+1} = f(S_t, a_t)를 일으킨다.

4. **Seed 기반 상태 인스턴스화**: 초기 상태 s0는 결정론적 매핑 f_init: (σ, C) → S로 생성된다.
여기서 C는 LLM이 실세계 분포를 모방해 사전 생성한 대규모 Synthetic Knowledge Base(사용자 프로필, 메시지 이력, 주식 티커 등)이며, seed σ가 의사난수생성기(PRNG)를 파라미터화해 s0 = Sample(C; PRNG(σ))로 샘플링한다.
환경 구조는 일정하지만 seed마다 구체적 인스턴스(사용자 존재 여부, 권한)가 완전히 달라져, 에이전트가 하드코딩 휴리스틱 대신 능동적 도구 사용으로 환경을 인지하도록 강제한다.

5. **상호의존성·확률성 주입**: 도구 t_j는 현재 상태 s_t가 선행 도구 t_i가 생성한 특정 속성 v를 포함할 때만 유효하다.
각 실행에는 seed 기반 확률성 η(σ)가 적용되어 네트워크 지연·일시적 오류 같은 실세계 교란을 시뮬레이션한다.

6. **결정론적 fine-grained 평가**: 환경 상태를 중첩 딕셔너리로 보고, 초기 상태 env_old, 목표 env_gt, 에이전트 결과 env_new를 key-path 단위로 비교한다.
필요 변경 수 T(목표 달성에 바꿔야 할 요소), 정확 변경 수 M, 오작동 수 Mb(바뀌면 안 되는데 바뀐 요소=부수효과)를 세고, Completion Rate R_c = M/T, Misbehaving Rate R_b = Mb/T를 정의한다.
타임스탬프·랜덤 ID 등 정합성에 무관한 키는 비교에서 제외하며, R_c = 1이고 R_b = 0일 때만 trajectory를 correct로 판정한다.

7. **명령어셋·평가 프로토콜**: 전문가가 수작업으로 47개 고품질 태스크를 큐레이션하고 각각에 ground-truth trajectory를 주석했다.
쿼리에는 도구 이름·힌트를 일절 제공하지 않아 에이전트가 내부 추론과 환경 인지만으로 도구를 찾게 하며, 가장 복잡한 시나리오는 30개 이상의 고유 도구와 60회 이상의 총 호출을 요구한다.
ReAct 패러다임을 기본 프롬프팅으로 쓰며, full-context(300+ 도구 설명 약 30,000 토큰을 시스템 프롬프트에 모두 주입)와 RAG 두 패러다임을 평가한다.

---

## Key Contribution

1. **통합 MCP 생태계**: 7개 stateful 샌드박스의 150+ 상호의존 도구와 150+ stateless API를 합쳐 300+ 도구를 MCP 네이티브로 제공하며, 고립 호출이 아닌 long-chain 추론과 복잡한 상태 전이를 요구한다.
2. **Seed 기반 동역학**: 단일 seed가 고엔트로피 환경 초기화와 실행 시 교란(API 실패)을 동시에 통제해, 실세계 확률성·다양성과 완벽한 재현성을 양립시킨다.
3. **결정론적 fine-grained 평가**: 주관적 LLM 채점 대신 환경 상태 전이를 ground truth와 비교하는 규칙 기반 시스템으로, 이진 성공을 넘어 Completion Rate·Misbehaving Rate 등 객관적 실패 모드 분석 지표를 제공한다.
4. **3대 실패 병목 식별**: trajectory 분석으로 tool retrieval saturation, over-confidence(Clean-Slate bias), strategic defeatism이라는 SOTA 모델 공통 실패 패턴을 정량적으로 규명했다.
5. **공개**: 벤치마크·코드를 https://github.com/AIDC-AI/complex-mcp 에 공개해 차세대 견고한 자율 에이전트 연구의 testbed를 제시한다.

---

## Experiment & Results

평가 모델은 GPT-4o, GPT-5.1, Gemini 시리즈(2.5-Pro, 3-Pro, 3-Flash), Claude 시리즈(Sonnet-3.5/4/4.5, Opus-4), Llama-3 시리즈(8B/70B/405B), Qwen3-Max, DeepSeek-V3, Kimi-K2, GLM-4.7로, 47개 시나리오를 각 3회 독립 실행했다.
**핵심 결과: 최상위 모델조차 60% 성공률을 넘지 못해 인간(93.61%)에 크게 뒤졌다.**
Full-context에서 최고 성능은 Gemini-3-Flash로 성공률 55.31%, Completion Rate 85.79%였고, 그 뒤가 Gemini-3-Pro(44.67%), GLM-4.7(42.55%), Claude-Opus-4(41.84%), Claude-Sonnet-4.5(39.71%), Claude-Sonnet-4(38.29%)였다.
주목할 점은 최상위 추론 모델 GPT-5.1이 성공률 19.14%로 부진했는데, 이는 일시적 토큰/네트워크 오류에서 회복하지 못하고 "정중하게 포기(polite surrender)"하기 때문이다.
하위권은 GPT-4o 14.89%, DeepSeek-V3 19.86%, Llama-3.1-8B-Instruct는 8.51%에 그쳤고 특히 8B는 Misbehaving Rate 14.88%, Syntactic Error 6.46회로 부수효과·문법 오류가 폭발했다.
**토큰 병목**: ReAct는 매 턴 전체 trajectory를 재제출하므로, 11회 도구 호출(12회 모델 호출) 태스크에서 약 30,000 토큰 프롬프트가 12번 청구되어 총 약 360,000 입력 토큰에 달한다.
Gemini-3-Flash 기준 토큰 분포는 프롬프트 91.9% / 도구 피드백 5.4% / LLM 생성 2.8%, 비용 분포는 87.1% / 9.3% / 3.6%로 프롬프트 반복이 비용을 지배했다(평균 프롬프트 29,964 / 생성 901 / 도구 피드백 1,750 토큰).
**RAG 실험**: all-MiniLM-L6-v2 임베딩으로 Gemini-3-Flash·Claude-Opus-4에 standard RAG와 Iterative RAG를 적용했다.
Iterative RAG가 retrieval 계열 중 최고이자 최저 토큰(Gemini 성공률 36.88%, Claude 25.52%)을 기록했으나, 모두 full-context에 미달했다 — 잠재 선행 도구를 의미 기반 검색으로 끌어오지 못하기 때문이다(예: Gemini RAG k=30은 13.47%, k=60은 27.65%로 급락).
**확장성 분석**: distractor 도구를 0→300+로 늘리자 GPT-4o·DeepSeek-V3는 후보 300 초과 시 성공률·Completion Rate가 급락(tool retrieval saturation)했으나, Gemini-3-Flash·Claude-Opus-4는 강화된 long-context 처리로 이를 대부분 완화했다.

---

## Limitation

저자가 명시한 한계는 명령어셋이 47개로 비교적 소규모라는 점인데, 이는 절대적 결정론과 논리적 정합성을 위한 의도적 trade-off다.
자동 생성에 의존하는 벤치마크와 달리 각 태스크는 복잡한 도구 상호의존성을 전문가가 수작업으로 매핑하고 ground-truth trajectory를 정밀 주석해야 하므로, 시간·인력 비용이 크고 규모 확장이 느리다.
향후 연구로 엄격한 수작업 검증 기준을 유지하면서 다중 도메인 시나리오를 추가해 태스크 다양성을 확장할 계획이다.
독자 관점에서 보면, 7개 가상 애플리케이션(LightTalk, LightShop 등)은 LLM이 합성한 환경이라 실제 상용 소프트웨어 API의 문서 모호성·인증 흐름·rate limit과는 차이가 있어 sim-to-real 격차가 존재할 수 있다.
또한 평가가 영어 단일 언어이고 모두 상용 API 모델 중심(오픈소스는 Llama·DeepSeek·Kimi·GLM 일부)이라 결과의 일반성이 제한되며, ReAct 단일 프롬프팅 전략에 묶여 있어 더 정교한 플래닝·메모리·멀티에이전트 하네스의 잠재력은 측정되지 않았다.
실질적 영향으로는, 이 벤치마크가 드러낸 Clean-Slate bias와 strategic defeatism은 엔터프라이즈·금융 자동화에서 중복 결제나 데이터 손상 같은 실제 위험으로 직결되므로, 에이전트의 능동적 환경 인지와 오류 복구 능력이 배포 전 반드시 보강되어야 함을 시사한다.

# AgentBench: Evaluating LLMs as Agents

> **논문 정보**: Xiao Liu, Hao Yu, Hanchen Zhang 외 (Tsinghua University, OSU, UC Berkeley)
> **arXiv**: 2308.03688 (2023.08) | **학회**: ICLR 2024
> **코드**: https://github.com/THUDM/AgentBench

---

## Problem

LLM을 "에이전트"로 활용하려는 응용(AutoGPT, BabyAGI, AgentGPT 등)이 폭발적으로 등장했지만, 이들의 추론·의사결정 능력을 정량적으로 비교할 표준 벤치마크가 부재하다.

기존 텍스트 게임 환경(TextWorld, Jericho, LIGHT)은 닫힌 이산 액션 스페이스와 상식적 grounding에만 초점이 맞춰져 있어 현실 업무 환경을 반영하지 못한다.

Embodied 에이전트 벤치마크(MineDojo, iGibson, BEHAVIOR)는 멀티모달 시뮬레이터를 요구하여 텍스트 전용 LLM 평가가 근본적으로 불가능하다.

기존 에이전트 벤치마크는 대부분 단일 환경(WebShop만, 또는 ALFWorld만)에 국한되어 다양한 응용 시나리오에 걸친 종합적 능력을 평가할 수 없다.

코드 학습이 에이전트 능력에 도움이 되는지, 고품질 정렬 데이터가 얼마나 중요한지 등 LLM 에이전트 개발에 필수적인 질문들이 체계적 데이터 없이 추측 수준에 머물러 있다.

상용 API 모델과 오픈소스 LLM 사이의 실제 성능 격차가 얼마나 큰지, 어떤 환경에서 격차가 더 심한지 정량적으로 밝혀진 바가 없다.

실패 원인(컨텍스트 초과, 형식 오류, 잘못된 액션, 라운드 한도 초과)을 유형별로 분해하여 개선 방향을 제시하는 연구가 없다.

---

## Motivation

LLM-as-Agent는 Partially Observable Markov Decision Process (S, A, T, R, U, O)로 형식화할 수 있으므로, 여러 환경에서 동일한 프로토콜로 다중 라운드 상호작용을 평가하면 비교 가능한 점수 체계를 만들 수 있다.

실제 LLM 활용 시나리오는 코드 기반(터미널, SQL, KG API), 게임 기반(전략, 퍼즐, 가정), 웹 기반(쇼핑, 브라우징)의 세 범주로 자연스럽게 나뉘며, 각 범주가 서로 다른 핵심 능력(계획, 상식, 도구 사용)을 요구한다.

Chain-of-Thought (CoT) prompting과 ReAct 스타일 "Thought + Action" 포맷이 제로샷 LLM-as-Agent의 사실상 표준이 되었으므로, 이를 공통 인터페이스로 사용하면 29개 이질적 LLM을 공평하게 비교할 수 있다.

태스크별 점수 분포가 크게 달라 단순 평균은 WebShop처럼 점수가 높은 태스크에 치우치는 문제가 있는데, 전체 모델 평균의 역수를 가중치로 사용하면 난이도 편향을 상쇄한 공정한 Overall Score를 만들 수 있다.

Server-Client HTTP 프로토콜과 Docker 캡슐화를 결합하면 다양한 환경(Ubuntu bash, MySQL, Freebase, ALFWorld)을 서로 충돌 없이 격리하여 확장 가능한 평가 툴킷을 구축할 수 있다.

8개 환경 × 29개 모델 = 약 3,000개 dev + 11,000개 test 추론 호출로 MMLU와 비슷한 규모의 평가를 달성하면서도 다중 라운드 상호작용까지 포괄할 수 있다.

---

## Method

1. **환경 구성**: 8개 상호작용 환경을 3범주로 조직 — Code-grounded {Operating System (Ubuntu bash), Database (MySQL), Knowledge Graph (Freebase 45M 개체, 3B 사실)}, Game-grounded {Digital Card Game (Aquawar, 2021 THUAC), Lateral Thinking Puzzles (海龟汤, yes/no/irrelevant 질문), House Holding (ALFWorld/TextWorld)}, Web-grounded {Web Shopping (WebShop), Web Browsing (Mind2Web)}. 8개 중 5개가 신규 제안.

2. **POMDP 정형화**: 상호작용 평가를 (S, A, T, R, U, O) 튜플로 정의. 각 에피소드는 대화 히스토리 (u₀, a₀, ..., u_k, a_k) 시퀀스이며, user는 환경 feedback을 제공하고 agent는 Thought+Action을 생성.

3. **평가 프롬프트 규약**: Yao et al. (ReAct, 2023b)의 포맷을 각색하여 "Thought" (CoT 추론) + "Action" (실행)을 한 라운드 안에 묶는다. 채팅 모델은 history를 그대로, text-completion 모델(text-davinci-003 등)은 "USER:", "AGENT:" 프리픽스를 붙여 호환. temperature=0 (greedy decoding).

4. **태스크별 메트릭**: OS/DB/HH는 Success Rate, KG는 F1, DCG는 Reward (win rate), LTP는 Game Progress, WS는 Reward, WB는 Step SR을 사용. 평균 라운드 수는 WS 5, DB 5, OS 8, WB 10, KG 15, LTP 25, DCG 30, HH 35로 다양.

5. **데이터셋 분할**: Dev 269 샘플 / Test 1,014 샘플. 각 샘플당 예상 상호작용 라운드를 곱하면 Dev ~3k, Test ~11k 호출로 MMLU 수준의 규모 확보. 공개 데이터셋 기반으로 재구성.

6. **Overall Score (OA) 계산**: 태스크별 난이도 편향 제거를 위해 Weight⁻¹ 방식 적용 — (1) 각 태스크의 29개 모델 평균 점수를 구하고, (2) 그 역수를 태스크 가중치로 사용하고, (3) 각 모델 점수 × 가중치의 평균을 OA로 정의. 재현성을 위해 fixed weight를 공개(OS 10.8, DB 13.0, KG 13.9, DCG 12.0, LTP 3.5, HH 13.0, WS 30.7, WB 11.6).

7. **실패 유형 분류 체계**: Complete (정상 종료), Context Limit Exceeded (CLE, 컨텍스트 2,048 초과 — text-davinci-002/003만 해당), Invalid Format (IF, 포맷 오류), Invalid Action (IA, 포맷은 맞지만 액션 invalid), Task Limit Exceeded (TLE, 최대 라운드 초과 또는 반복 생성)로 나누어 모든 에피소드를 태그.

8. **Toolkit 아키텍처**: API 중심 Server-Client 구조. 연구자는 HTTP 프로토콜로 접근 가능한 모델 서버만 띄우면 됨. 환경은 Docker 이미지로 캡슐화(충돌 방지), 각 태스크는 별도 worker로 분리되어 환경 격리 보장.

9. **29개 모델 평가**: API-based {GPT-4 (0613), GPT-3.5-turbo (0613), text-davinci-002/003, Claude v1.3/Claude-2/Claude-3 Opus/Claude-instant, chat-bison-001, GLM-4} + OSS (≤70B) {LLaMA-2 70B/13B/7B, CodeLLaMA 34B/13B/7B instruct, Vicuna 33B/13B/7B v1.5, WizardLM 30B/13B, Guanaco 65B/33B, OpenChat 13B, Koala 13B, Dolly 12B, ChatGLM 6B, CodeGeeX 6B, OASST 12B}.

10. **OS 환경 세부**: Ubuntu Docker 기반, SR로 평가. 질문 유형은 deterministic answer ("non-/home 디렉토리 사용자 수") 또는 operations ("재귀적으로 읽기 전용 권한 설정").

11. **DB 환경 세부**: 실제 MySQL 인터페이스 위에 다양한 쿼리(SELECT/INSERT/UPDATE) 평가. 단순 text-to-SQL이 아닌 파이프라인 전체를 end-to-end로 평가.

12. **KG 환경 세부**: Freebase API 제공, 부분 관찰 환경에서 language understanding + planning + tool use를 요구. 대규모 KG의 불완전 정보 아래 의사결정 능력 측정.

13. **DCG (Aquawar)**: 2인 턴제 배틀, 4장의 pet fish card 조작. 카드 텍스트 이해 + 전략적 결정 + 게임 규칙 준수 능력을 종합 평가. Win rate가 메트릭.

14. **LTP 환경 세부**: 자동 judging 호스트 시스템 구축, 웹에서 수집한 다양한 난이도의 海龟汤 퍼즐. 플롯을 여러 point로 단순화하여 game progress로 평가. Lateral reasoning 측정.

15. **WebShop/Mind2Web 적응**: 원래 fine-tuning 기반 평가였던 두 벤치마크를 prompting-only 평가로 재구성 — pure LLM 능력만 측정 가능하도록 수정.

---

## Key Contribution

1. **LLM-as-Agent 평가 패러다임 최초 확립**: 단일 환경 또는 멀티모달 시뮬레이터 의존에서 벗어나, 텍스트 전용 LLM을 8개 실사용 환경에서 통합 평가하는 체계적 벤치마크를 제시. 5개 환경(OS, DB, DCG, LTP, KG setup)을 신규 제안.

2. **29개 모델 대규모 비교 연구**: API 10개(OpenAI, Anthropic, Google, Zhipu) + OSS 19개(≤70B)의 공개 비교를 통해 LLM 에이전트 연구 커뮤니티에 최초의 공통 좌표계를 제공. GPT-4 OA 4.01 vs OSS 평균 0.51로 ~4.5배 격차를 정량화.

3. **난이도 편향 해소 점수 체계**: 태스크별 평균 점수의 역수를 가중치로 고정 공개(OS 10.8, WS 30.7 등)하여, 후속 연구가 동일한 OA 공식으로 공정하게 비교 가능하도록 표준화.

4. **실패 원인 유형론 (CLE/IF/IA/TLE)**: 모든 에피소드를 4가지 실패 + Complete로 분류하여, LLM 에이전트의 근본적 약점이 **장기 추론/의사결정 부족(TLE 지배적)**과 **지시 따르기 부족(IF/IA)**임을 정량적으로 규명. 개선 방향(지시 따르기 향상, 고품질 정렬 데이터) 제시.

5. **코드 학습의 양면성 (Double-edged sword) 실증**: CodeLLaMA vs LLaMA-2 비교를 통해, 코드 튜닝이 정적 절차 태스크(WS)에는 유리하지만 일반 추론/전략 태스크(DCG, OS 상호작용)에는 불리함을 최초로 정량 확인. LLM 튜닝 전략에 재고 요구.

6. **고품질 정렬 데이터 중요성**: Vicuna-13b (ShareGPT GPT-4 데이터로 정렬) vs LLaMA-2-13b (from scratch) 비교로, 동일 base 모델에서 정렬 데이터 품질이 에이전트 능력을 결정함을 입증. Vicuna-13b(OA 0.93)가 3배 큰 CodeLLaMA-34b(OA 0.96)과 비슷.

7. **Server-Client 평가 툴킷 공개**: HTTP 프로토콜 + Docker 격리 기반의 재현 가능한 평가 인프라를 오픈소스로 공개(GitHub THUDM/AgentBench). 후속 연구가 새 모델을 쉽게 추가 가능.

---

## Experiment & Results

**전체 순위 (Overall Agent Score)**: GPT-4 (0613) **4.01**로 압도적 1위, Claude-3 Opus 3.11, GLM-4 2.89, Claude-2 2.49, Claude v1.3 2.44, GPT-3.5-turbo 2.32. OSS 최상위는 CodeLLaMA-34b-instruct **0.96**으로 GPT-3.5의 약 41% 수준. API 평균 **2.32** vs OSS 평균 **0.51**로 4.5배 격차.

**GPT-4 환경별 점수**: OS 42.4, DB 32.0, KG 58.8, DCG 74.5, LTP 16.6, HH 78.0, WS 61.1, WB 29.0 — HH와 DCG에서 특히 강세, LTP/WB에서 약세.

**실패 유형 분포 (전 모델 평균, %)**: TLE가 지배적 — KG 67.9%, LTP 82.5%, WB 35.0%, WS 27.8%, OS 23.9%, HH 22.1%. Invalid Format은 DB 53.3%, DCG 38.5%로 엄격한 포맷 요구 태스크에서 급증. Invalid Action은 HH 64.1%에서 지배적 (사전 정의 액션 공간 벗어남). CLE는 거의 없음(text-davinci-002/003의 2,048 컨텍스트에서만 0.7~3.5%).

**Complete 비율**: OS 75.0%, WB 56.6%, WS 54.9%, DCG 51.2%, DB 37.9%, KG 30.1%, LTP 14.0%, HH 13.1% — LTP/HH는 대다수 에피소드가 해결되지 못하고 종료.

**코드 학습 양면성 (CodeLLaMA-34b vs LLaMA-2-70b)**: WS에서 CodeLLaMA-34b **52.1** vs LLaMA-2-70b 5.6 (절차적 태스크 우세), 그러나 DCG에서 CodeLLaMA-34b 8.4 vs LLaMA-2-70b **21.3** (전략 태스크 열세), OS도 CodeLLaMA-34b 2.8 vs LLaMA-2-70b 9.7.

**정렬 데이터 효과 (Vicuna-13b vs LLaMA-2-13b)**: 동일 base 모델이지만 Vicuna-13b OA 0.93, LLaMA-2-13b OA 0.77로 Vicuna 우세. Vicuna-13b는 OA 0.96의 CodeLLaMA-34b(3배 큰 모델)와 대등.

**LLaMA-2 스케일링 이상 현상**: LLaMA-2-13b (0.77)와 LLaMA-2-70b (0.78)가 거의 동일한 OA — 모델 크기가 에이전트 능력으로 자동 전환되지 않음을 시사.

**데이터셋 규모**: Dev 269 + Test 1,014 샘플 = 총 1,283 샘플, 총 호출 수 약 14,000회 (Dev ~3k, Test ~11k)로 MMLU와 비슷한 추론 비용.

**하위 모델 성능**: OASST-12b 0.03, ChatGLM-6b 0.11, Dolly-12b 0.14로 거의 모든 환경에서 solve 실패 — 당시 소형 OSS 모델들의 에이전트 능력 부재 확인.

---

## Limitation

텍스트 전용 평가로 제한되어 GPT-4V, Gemini 등 멀티모달 에이전트의 비전-언어 통합 능력을 반영하지 못한다. 실제 웹 브라우징/데스크톱 조작은 스크린샷이 핵심인데 이를 배제.

OSS 모델을 70B 이하로 제한한 결과 LLaMA-2-70B 이상의 대형 OSS(예: 이후의 LLaMA-2-70B chat, Mixtral 8x22B, LLaMA-3-405B)에 대한 평가가 누락되어, 상용 vs OSS 격차가 과장되었을 가능성.

temperature=0 고정은 재현성을 보장하지만 self-consistency, best-of-N, MCTS 등 테스트 시간 연산 기법의 이점을 측정하지 못해, 현대 에이전트의 실제 상한 능력을 과소평가한다.

일부 환경(WebShop weight 30.7, LTP weight 3.5)은 난이도 격차가 극심해 역가중 평균이라도 완전한 공정성을 보장하지 못하며, 7개 환경에서 0점인 모델도 WS 한 곳에서 점수를 받아 OA가 비현실적으로 상승할 수 있다.

CoT + "Thought+Action" 단일 라운드 포맷에 고정되어 있어, 계획-실행 분리(Plan-and-Solve), Self-Reflection, 멀티 에이전트 협업 등 고급 harness의 효과를 측정하지 못한다. 순수 LLM 능력과 harness 설계의 기여를 분리 불가능.

KG는 Freebase만, DB는 MySQL만, OS는 Ubuntu bash만 사용하여 특정 플랫폼·쿼리 언어에 편향. Neo4j, PostgreSQL, Windows PowerShell 등 실제 환경 다양성 미반영.

ALFWorld(HH)와 WebShop은 시뮬레이션 환경이며 실제 물리 세계·실제 전자상거래 사이트의 복잡도(동적 변화, 적대적 페이지, 법적 제약)를 반영하지 못한다. Mind2Web도 HTML 스냅샷 기반으로 실시간 동적 요소 미평가.

모든 평가가 2023년 시점의 모델/데이터셋에 고정되어 있어 GPT-4o, Claude-3.5 Sonnet, o1 등 최신 모델의 에이전트 능력은 별도 업데이트 없이 확인 불가능.

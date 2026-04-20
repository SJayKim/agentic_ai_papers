# MemGPT: Towards LLMs as Operating Systems

> **논문 정보**: Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez (UC Berkeley)
> **arXiv**: 2310.08560 (2023.10)
> **코드**: https://research.memgpt.ai

---

## Problem

대규모 언어 모델(LLM)은 고정 길이 컨텍스트 윈도우라는 구조적 제약을 가지고 있어 장기 대화와 대규모 문서 분석에서 성능이 심각하게 제한된다.

Llama 1은 2k, Llama 2는 4k, GPT-4 기본 버전은 8k, GPT-4 Turbo는 128k 토큰으로, 평균 메시지 크기 ~50 토큰 기준으로 2k 모델은 약 20회, 8k 모델은 약 140회의 대화만 지원한다.

반면 실제 법률/재무 문서(SEC 10-K 연차 보고서 등)는 쉽게 100만 토큰을 넘기며, 다중 문서 분석 시 맥락 크기는 기하급수적으로 증가한다.

Self-attention의 이차 시간·메모리 복잡도 때문에 단순히 컨텍스트를 확장하면 연산 비용이 폭발적으로 늘어나, 새로운 장문 아키텍처 설계가 시급한 연구 과제로 남아 있다.

더욱이 Liu et al. (2023a) "Lost in the Middle" 연구는 긴 컨텍스트를 학습한 모델조차 윈도우 중간 부분의 정보를 효과적으로 활용하지 못함을 보여, 단순 확장의 수확 체감(diminishing returns)이 확인되었다.

따라서 학습에 막대한 자원이 드는 state-of-the-art LLM을 재학습하지 않고도, 고정 컨텍스트 모델 위에서 무한 컨텍스트의 환상을 제공할 수 있는 대안적 시스템 설계가 긴요하다.

대화 에이전트에서는 일관된 persona 유지·장기 기억·과거 사실 회상이 어려워지고, 문서 분석에서는 retriever가 golden document를 첫 페이지에서 놓치면 고정 컨텍스트 baseline은 절대 정답에 도달할 수 없다.

## Motivation

전통적인 운영체제(OS)는 물리 메모리(RAM)와 디스크 사이에 가상 메모리(virtual memory)와 페이징 메커니즘을 도입하여, 실제 RAM보다 훨씬 큰 데이터셋을 다룰 수 있는 "무한 메모리의 환상"을 제공해왔다.

저자들은 이 고전적 아이디어를 LLM에 이식하여, 프롬프트 토큰 공간(=main memory)과 외부 저장소(=disk) 사이에 LLM 자신이 데이터를 페이징하도록 만들면 고정 컨텍스트 한계를 극복할 수 있다고 판단했다.

Schick et al. (2023) Toolformer와 Liu et al. (2023b) LLM-as-an-agent 벤치마크에서 입증된 LLM의 function calling 능력은 이 설계의 핵심 메커니즘으로 활용될 수 있다.

즉, LLM은 function call을 통해 외부 데이터 소스를 읽고 쓰고, 자신의 컨텍스트를 수정하며, 사용자에게 응답을 반환할 시점을 스스로 결정할 수 있다.

이러한 능력은 전통적 OS의 인터럽트 처리와 유사하게 이벤트 기반 제어 흐름(event-driven control flow)으로 확장되어, 사용자 메시지·시스템 알림·타이머 이벤트가 모두 LLM 추론을 트리거할 수 있다.

Park et al. (2023) Generative Agents나 Nakano et al. (2021) WebGPT가 보인 바와 같이, LLM을 상호작용형 에이전트로 augment하려는 기존 연구 흐름 위에서, MemGPT는 메모리 계층 전체를 LLM이 자율 관리하는 가장 체계적인 최초의 "LLM OS"를 제안하고자 한다.

## Method

1. **두 단계 메모리 계층 (Main Context vs External Context)**: Main Context는 LLM 프롬프트 토큰으로 inference 시 직접 접근 가능한 영역(RAM 대응), External Context는 프롬프트 밖의 영구 저장소(Disk 대응)이며 둘 사이 이동은 반드시 명시적 function call로 수행된다.

2. **Main Context 3분할 구조**: (a) System Instructions — 읽기 전용, MemGPT 시스템 프롬프트·메모리 계층 설명·함수 스키마 포함, (b) Working Context — 읽기/쓰기, 에이전트가 function call로 직접 편집하는 persona·사용자 핵심 정보 저장소, (c) FIFO Queue — 최근 메시지와 함수 결과가 시간순 적재되는 슬라이딩 윈도우.

3. **External Context 2분할**: (a) Recall Storage — 전체 대화 이력을 시간순으로 영구 저장하며 `conversation_search` 등으로 검색 가능, (b) Archival Storage — 임의 길이의 텍스트 객체(문서, 지식 베이스)를 저장하는 읽기/쓰기 데이터베이스로 `archival_storage.search` + 페이지네이션으로 접근.

4. **Queue Manager와 Memory Pressure 경고**: 프롬프트 토큰이 warning token count(예: 윈도우의 70%)를 넘으면 Queue Manager가 시스템 경고를 큐에 삽입하여 LLM이 중요 정보를 Working Context나 Archival Storage로 이동할 기회를 제공한다.

5. **Queue Flush와 재귀적 요약**: 토큰이 flush threshold(예: 100%)에 도달하면 Queue Manager가 큐의 일정 비율(예: 50%)을 축출하고, 기존 recursive summary와 축출된 메시지를 결합하여 새 recursive summary를 생성하며, 축출 원본은 Recall Storage에 영구 보관되어 언제든 function call로 재접근 가능하다.

6. **Function Executor와 Self-Directed Editing**: LLM 완성 토큰은 function call로 파싱되며, 인자 검증 후 실행되고 결과(runtime error 포함)가 피드백으로 재주입되어, 에이전트가 자율적으로 memory edit/retrieval을 수행하며 실패로부터 학습한다.

7. **Function Chaining via `request_heartbeat`**: `request_heartbeat=true` 플래그가 달린 function call은 실행 후 즉시 제어를 LLM에 돌려주어 다중 페이지 검색·다중 소스 수집 같은 연쇄 호출을 가능케 하며, 플래그 부재(yield) 시 다음 외부 이벤트까지 대기한다.

8. **이벤트 기반 제어 흐름**: 사용자 메시지, 시스템 경고(메모리 압박 등), 사용자 로그인/문서 업로드 알림, 정기 타이머 이벤트가 모두 parser를 거쳐 plain-text 메시지로 main context에 append되고 LLM 추론을 트리거하여, 사용자 개입 없는 "unprompted" 동작도 가능하다.

9. **System Prompt 설계**: 시스템 명령에는 (1) 메모리 계층과 각 계층의 용도에 대한 상세 설명, (2) 호출 가능한 함수들의 스키마와 자연어 description이 포함되어 LLM이 언제 어떤 함수를 호출해야 하는지 학습하도록 유도한다.

10. **DMR/QA용 특화 persona**: "계속 검색하라, 값이 키가 아님을 검증할 때까지 중첩 탐색을 멈추지 말라"와 같은 페르소나 지침으로 조기 종료를 억제한다.

---

## Key Contribution

1. **OS 가상 메모리 개념의 LLM 이식**: 물리 메모리(컨텍스트 윈도우)와 디스크(외부 저장소) 사이 페이징이라는 OS 고전 아이디어를 LLM에 적용하여, 고정 컨텍스트 모델 위에서 무한 컨텍스트의 환상을 제공하는 최초의 체계적 설계를 제시했다.

2. **자율 메모리 관리 에이전트 패러다임**: LLM이 function call로 자신의 컨텍스트를 능동적으로 읽기/쓰기/검색/축출하는 self-directed editing 패러다임을 정립했다.

3. **계층형 메모리 아키텍처 구체화**: Main Context(System Instructions + Working Context + FIFO Queue)와 External Context(Recall + Archival Storage)로 구성된 2-tier 메모리 설계와 Queue Manager, Function Executor, 이벤트 기반 제어 흐름을 포함한 완전한 시스템 청사진을 제공했다.

4. **Function Chaining 메커니즘**: `request_heartbeat` 플래그로 다중 함수 호출을 연쇄 실행하여 다중 페이지 검색과 multi-hop retrieval을 지원하는 새로운 제어 프리미티브를 도입했다.

5. **Deep Memory Retrieval 벤치마크**: MSC 데이터셋 기반으로 장기 대화의 구체적 사실 회상 능력을 엄밀히 평가할 수 있는 새로운 태스크와 LLM-judge 기반 평가 파이프라인을 공개했다.

6. **Nested KV Retrieval 벤치마크**: 값이 다른 키가 되는 다중 홉 조회 태스크를 새로 제안하여, 에이전트가 여러 쿼리를 조합해 정보를 수집하는 능력을 측정하는 표준화된 테스트베드를 제공했다.

7. **오픈 리소스 공개**: 코드, 확장된 MSC 데이터셋, nested KV 데이터셋, 2000만 Wikipedia 기사 임베딩을 공개하여 후속 장기 메모리·장문 에이전트 연구의 기반을 마련했다.

---

## Experiment

**평가 도메인**: 대화형 에이전트(Multi-Session Chat 확장) + 문서 분석(NaturalQuestions-Open retriever-reader QA, KV/nested KV retrieval).

**Baseline**: GPT-3.5 Turbo, GPT-4, GPT-4 Turbo 고정 컨텍스트 모델(과거 대화는 recursive summary로 압축 제공).

**Deep Memory Retrieval (DMR) — 5세션 이전 대화의 특정 사실 회상**: GPT-3.5 Turbo 38.7% → +MemGPT **66.9%**(+28.2%p), ROUGE-L 0.394 → 0.629; GPT-4 32.1% → +MemGPT **92.5%**(+60.4%p), ROUGE-L 0.296 → **0.814**; GPT-4 Turbo 35.3% → +MemGPT **93.4%**, ROUGE-L 0.359 → **0.827**.

**Conversation Opener — persona 일관성 있는 첫 발화 생성**: Human opener 기준 SIM-H 1.000 대비, MemGPT+GPT-3.5 Turbo SIM-1 0.830/SIM-3 0.812/SIM-H 0.817로 인간 수준에 근접하며 SIM-1·SIM-3에서는 오히려 초과.

**Document QA (NaturalQuestions-Open, 50 샘플)**: 고정 컨텍스트 baseline은 retriever 문서 수(0~200) 증가에 따라 정확도가 포화되어 약 0.6~0.7에서 상한에 걸리는 반면, MemGPT(GPT-4/GPT-4 Turbo)는 archival storage를 반복 검색하여 문서 수에 무관하게 안정적 성능을 유지.

**Nested KV Retrieval (140개 UUID 쌍, 8k 토큰)**: GPT-3.5는 nesting 1에서 즉시 0% 정확도(원래 값을 그대로 반환하는 실패 모드); GPT-4와 GPT-4 Turbo는 nesting 3에서 0%로 급락; **MemGPT+GPT-4만 nesting 4까지 일관된 성능 유지**하여 multi-hop 조회 완수.

**실패 모드 관찰**: MemGPT는 retriever의 전체 페이지를 끝까지 소진하기 전에 탐색을 조기 종료하는 경향이 있어, Document QA에서 이론상 상한에 미달하는 사례가 존재.

**샘플 규모**: NaturalQuestions-Open 50 질문, nested KV는 30개 ordering configuration × 5 nesting levels, MSC DMR은 페르소나당 session 6 신규 생성.

---

## Limitation

저자들이 직접 언급한 대로, MemGPT는 retriever 페이지네이션을 끝까지 소진하기 전에 조기 종료하는 경향이 있어, 이론상 상한에 도달하지 못하는 Document QA 성능 손실이 발생한다.

시스템 전체가 기반 LLM의 function calling 능력에 강하게 의존하기 때문에, GPT-3.5처럼 function calling 성능이 낮은 모델은 nested KV에서 0%로 즉시 붕괴하여 오픈소스·소형 모델 적용성이 크게 제한된다.

메모리 관리 결정(무엇을 Working Context로 승격/축출할지)이 전적으로 LLM의 주관적 판단에 맡겨져 있어, 명시적 정책·우선순위 없이 중요 정보가 유실될 가능성이 존재한다.

Function chaining과 recursive summary 생성으로 인해 매 사용자 턴마다 추가 LLM 호출이 여러 회 발생하여, 실시간 대화 에이전트에서의 latency/cost 오버헤드가 크지만 논문은 이를 정량 분석하지 않았다.

평가가 GPT-3.5/GPT-4/GPT-4 Turbo 등 OpenAI 비공개 모델에 집중되어 있으며, Llama 2·Mistral 등 오픈 가중치 모델에서의 성능 재현은 거의 다뤄지지 않는다.

Working Context의 용량이 제한적이고 명시적 슬롯 구조가 없어, 사용자가 많아지거나 persona가 복잡해질 때 정보 충돌·덮어쓰기 문제가 발생할 수 있으나 본 논문은 대규모 persona 시나리오를 탐구하지 않는다.

DMR·Nested KV 등 평가 데이터셋이 상대적으로 소규모(50~140 샘플)이며, LLM-judge 기반 평가는 GPT-4가 자신의 출력에 편향될 위험(evaluator-generator overlap)을 완전히 배제하지 못한다.

Archival Storage는 임베딩 기반 유사도 검색에 의존하므로, embedding retriever의 품질이 낮으면 MemGPT의 장점(반복 페이지네이션)도 실질 효용이 감소하며, 실제 Document QA에서도 retriever 한계가 성능 천장으로 작용함을 저자가 인정한다.

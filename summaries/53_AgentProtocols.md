# A Survey of AI Agent Protocols

> **논문 정보**: Yingxuan Yang, Huacan Chai, Yuanyi Song et al. (Shanghai Jiao Tong University, ANP Community)
> **arXiv**: 2504.16736 (2025.04, v3: 2025.06)
> **코드**: https://github.com/zoe-yyx/Awesome-AIAgent-Protocol

---

## Problem

LLM 에이전트가 고객 서비스, 콘텐츠 생성, 데이터 분석, 의료 지원 등 다양한 산업 전반에 걸쳐 급속히 배포되고 있지만, 에이전트와 외부 도구/데이터 소스 간, 에이전트와 에이전트 간 통신에 표준화된 프로토콜이 존재하지 않는다.
서로 다른 LLM 제공자들은 각자 독자적 tool 호출 형식(function calling schema)과 프롬프트 포맷을 구현하고 있어, 도구·데이터 제공자 또한 각자의 호출 인터페이스를 별도로 구축해야 한다.
이러한 단편화(fragmentation)는 개발자가 수백 가지 상이한 명세를 프롬프트 수준에서 관리해야 하는 부담을 초래하며, 시스템 복잡도와 유지보수 비용을 지수적으로 증가시킨다.
또한 서로 다른 벤더·아키텍처의 에이전트들이 협업해야 하는 다중 에이전트 시스템(MAS)에서는, 에이전트 발견(discovery), 정보 공유, 인증, 과금 등 기본적 상호작용조차 표준화되어 있지 않아 원활한 협업이 불가능하다.
결과적으로 에이전트 네트워크의 확장성(scalability)과 상호운용성(interoperability)이 심각하게 저해되며, 복잡한 실세계 문제 해결 능력이 제한된다.
MCP, A2A, ANP 등 다양한 프로토콜이 급속히 등장하고 있으나, 이들을 체계적으로 분류·비교·평가한 종합 연구가 부재하여 연구자·엔지니어가 적절한 프로토콜을 선택하고 통합하는 데 어려움을 겪고 있다.

---

## Motivation

TCP/IP와 HTTP가 1990년대 초 단편화된 인터넷의 호환성 문제를 해결함으로써 글로벌 연결성, 혁신, 가치 창출의 시대를 연 것처럼, 표준화된 에이전트 프로토콜은 "에이전트 인터넷(Internet of Agents)"의 집단 지성을 실현할 수 있는 잠재력을 가진다.
통일된 프로토콜이 확립되면 "도구 지능(tool intelligence)"과 "에이전트 지능(agent intelligence)" 사이의 인위적 장벽이 허물어지고, 두 지능이 동적으로 병합·증폭되어 개별 요소보다 큰 창발적(emergent) 집단 지능을 형성할 수 있다.
전문화된 에이전트들이 복잡한 문제 해결을 위해 일시적 연합(coalition)을 형성하고, 지능형 도구가 여러 에이전트의 능력을 동시에 확장하는 새로운 인지 아키텍처가 등장할 수 있다.
Anthropic의 MCP는 에이전트-리소스 통신을 표준화하여 에이전트의 "외부 두뇌" 역할을 수행하며, Google의 A2A와 ANP Community의 ANP는 이질적 에이전트 간 협업을 촉진한다.
이러한 프로토콜들이 보안, 확장성, 지연시간(latency) 등 핵심 차원에서 어떻게 다른지 정량적·정성적으로 비교하고, 차세대 프로토콜이 갖춰야 할 특성(적응성, 프라이버시 보존, 그룹 기반 상호작용)을 식별하는 것은 에이전트 생태계 발전의 필수 과제이다.
본 논문은 이러한 공백을 메우기 위해 최초의 종합적 에이전트 프로토콜 서베이를 제공한다.

---

## Method

**1. 2차원 분류 프레임워크 (Two-Dimensional Taxonomy)**
- 제1축 — 객체 지향성(Object Orientation): Context-Oriented (에이전트-리소스 통신) vs. Inter-Agent (에이전트-에이전트 통신)
- 제2축 — 적용 시나리오(Application Scenario): General-Purpose (범용) vs. Domain-Specific (도메인 특화)
- 4개 셀에 총 16개 주요 프로토콜 배치, Figure 3에서 트리 구조로 시각화

**2. 상호작용 방식 비교 (Interaction Manner Comparison)**
- 4가지 방식(API, GUI, XML, Protocol)을 효율성·운영 범위·표준화·AI 네이티브 호환성 차원에서 비교 (Table 1)
- API: 효율 ✓✓ / 운영범위 × / 표준화 × / AI 네이티브 ×
- GUI: 효율 × / 운영범위 ✓ / 표준화 ✓ / AI 네이티브 ×
- XML: 효율 × / 운영범위 ✓ / 표준화 × / AI 네이티브 ×
- Protocol: 모든 차원에서 ✓✓ 최고 점수

**3. Context-Oriented General-Purpose 프로토콜 — MCP (Anthropic, 2024)**
- 4-컴포넌트 아키텍처: Host (LLM 에이전트) ↔ Client (리소스 기술 제공) ↔ Server (리소스 연결) ↔ Resource (데이터/도구/서비스)
- 3단계 호출 사이클: (a) Initial Phase — 호스트가 LLM 추론으로 필요 컨텍스트 식별, 클라이언트가 가용 리소스를 자연어로 기술 (b) Request Phase — 클라이언트→서버 executive context request, 서버가 리소스 조작 후 결과 반환 (c) Response Phase — 호스트가 컨텍스트 결합하여 최종 응답 생성
- RPC + OAuth 기반 인증, 클라이언트-서버 분리로 function calling 방식의 자격정보 클라우드 업로드 위험 제거

**4. Context-Oriented Domain-Specific — agents.json (WildCardAI, 2025)**
- OpenAPI 위에 구축된 머신 리더블 JSON 명세, `/.well-known/agents.json` 경로에 호스팅
- `flows` (API 호출 시퀀스) + `links` (액션 간 데이터 의존성) 도입으로 LLM 오케스트레이션 지원
- Stateless 설계, 기존 API 최소 수정, LLM 소비 최적화

**5. Inter-Agent General-Purpose — ANP (ANP Community, 2024)**
- 탈중앙화 3계층 아키텍처: (a) Identity and Encrypted Communication Layer — W3C DID(Decentralized Identifiers) 기반 trustless end-to-end 암호화 통신 (b) Meta-Protocol Layer — Agora 기반 자연어 메타프로토콜 협상 (c) Application Protocol Layer — 에이전트 발견·기술·도메인별 태스크 수행
- 3대 원칙: Interconnectivity, Native Interfaces (스크린 캡처 배제, API/프로토콜 네이티브), Efficient Collaboration

**6. Inter-Agent General-Purpose — A2A (Google, 2025)**
- 5대 핵심 개념: Agent Card, Task, Artifact, Message, Parts
- HTTP(S) 전송 + JSON-RPC 2.0 메시징 + Server-Sent Events(SSE) 스트리밍 기반
- 5대 설계 원칙: Simplicity (기존 표준 재활용), Enterprise Readiness (인증·권한·감사), Async-First (polling/SSE/push notification), Modality Agnostic (text/file/form/audio/video/iframe), Opaque Execution (내부 사고·계획 비공개)
- 워크플로: 원격 에이전트가 JSON Agent Card로 능력 광고 → 클라이언트가 최적 에이전트 선택 → A2A 통신으로 태스크 수행 → Artifact로 결과 반환

**7. 기타 Inter-Agent 프로토콜**
- **AITP (NEAR, 2025)**: Blockchain 기반 신뢰 경계 횡단, Threads/Transport/Capabilities 3요소, 자율 협상·가치 교환 (예: 항공편 예약 에이전트)
- **AConP (Cisco/LangChain, 2025)**: 5개 API (retrieval, run, interruption/resumption, thread run, output streaming) + Agent ACP Descriptor
- **AComP (IBM, 2025)**: REST 기반, SDK 불필요, 오프라인 디스커버리, async-first, MIME 멀티파트, 토큰 기반 보안
- **Coral Protocol**: 스레드 통신 모델 + Coral Server 코디네이션 + MCP 통신 + 구조화된 identity/role/scoped memory
- **Agora (Oxford, 2024)**: Protocol Documents(PDs) 평문 명세, 에이전트 자율 협상·구현·생성, 빈번 통신은 구조화 프로토콜, 드문 통신은 자연어 전환

**8. Agent Communication Trilemma**
- Versatility (다양한 메시지 유형·포맷 지원) vs. Efficiency (낮은 계산/네트워크 비용) vs. Portability (최소한의 구현 노력) — 동시 최적화 불가
- Agora는 LLM의 NL 이해·코드 생성·자율 협상 능력을 활용해 상황별 프로토콜 전환으로 트릴레마 완화

**9. Domain-Specific Inter-Agent 프로토콜 (3개 하위 범주)**
- Human-Computer: LOKA (CMU, DECP), PXP (BITS Pilani), WAP
- Robot-Agent: CrowdES (GIST.KR), SPPs (Liverpool)
- System-Agent: Agent Protocol (AI Engineer Foundation, RESTful), LMOS (Eclipse Foundation, WOT+DID)

**10. 7차원 평가 프레임워크 (Protocol Evaluation)**
- Efficiency (효율성), Scalability (확장성), Security (보안), Reliability (신뢰성), Extensibility (확장 가능성), Operability (운용성), Interoperability (상호운용성)
- 각 차원별로 프로토콜 강약점을 정성적으로 비교, 프로토콜 진화에 대한 케이스 스터디 포함

**11. 미래 로드맵 3단계**
- Short-Term (Static → Evolvable): 적응형·프라이버시 인식·그룹 조율 프로토콜
- Mid-Term (Rules → Ecosystems): 생태계 수준 조율, 계층화 아키텍처
- Long-Term (Protocols → Intelligence Infrastructure): 집단 지성 인프라, 새로운 인지 아키텍처

---

## Key Contribution

1. **최초의 2차원 에이전트 프로토콜 분류 체계**: 객체 지향성(context-oriented vs. inter-agent) × 적용 시나리오(general-purpose vs. domain-specific) 교차로 16개 주요 프로토콜을 체계적으로 조직화한 최초의 프레임워크.
2. **7개 핵심 차원 정성 비교 분석**: 효율성·확장성·보안·신뢰성·확장가능성·운용성·상호운용성 차원에서 프로토콜별 상대적 강약점을 매핑하여 실무 선택 가이드 제공.
3. **포괄적 프로토콜 카탈로그**: MCP, A2A, ANP, AITP, AConP, AComP, Coral, Agora, agents.json, Agent Protocol, LMOS, LOKA, PXP, WAP, CrowdES, SPPs 등 16개 프로토콜을 제안자·적용 시나리오·핵심 기술·개발 단계별로 정리한 Table 2.
4. **상호작용 방식 4종 비교 분석**: API/GUI/XML/Protocol 4가지 방식을 4개 속성(효율성·운영범위·표준화·AI 네이티브)으로 비교하여 프로토콜 기반 접근의 우위를 정량적으로 입증.
5. **Agent Communication Trilemma 형식화**: Versatility·Efficiency·Portability 3요소의 상충 관계를 공식화하고, Agora의 LLM 활용 동적 프로토콜 전환을 해결책으로 제시.
6. **사용 시나리오별 실용 가이드**: 단일 에이전트-다중 도구 시나리오(MCP), 기업 내 복잡 협업(A2A), 크로스도메인 P2P(ANP), 자연어-프로토콜 동적 생성(Agora) 4개 대표 사례 심층 분석.
7. **미래 전망 3단계 로드맵**: 단기(정적→진화형), 중기(규칙→생태계), 장기(프로토콜→지능 인프라) 발전 궤적을 제시하고 차세대 프로토콜 필수 특성(적응성·프라이버시·그룹 상호작용) 식별.

---

## Experiment

본 논문은 서베이 연구로, 정량적 벤치마크 대신 프로토콜별 속성·개발 성숙도·사용 사례에 대한 정성적 비교 및 케이스 스터디를 수행한다.

**프로토콜 카탈로그 규모**: 총 16개 주요 에이전트 프로토콜을 수집·분류 (Table 2), 범용 컨텍스트 1개(MCP), 도메인 특화 컨텍스트 1개(agents.json), 범용 Inter-Agent 7개(A2A, ANP, AITP, AConP, AComP, Coral, Agora), 도메인 특화 Inter-Agent 7개.

**개발 성숙도 분포 (2025.04 시점 평가)**: Landing(실운영) 5개 — MCP, A2A, ANP, Agent Protocol, LMOS / Drafting(초안) 8개 — agents.json, AITP, AConP, AComP, Coral, Agora 등 / Concept(개념) 3개 — LOKA, PXP, CrowdES, SPPs.

**상호작용 방식 비교 정량 평가 (Table 1)**: Protocol 방식이 4개 속성 모두에서 ✓✓(최고 등급) 획득. API는 효율성만 ✓✓, 나머지 3개 ×. GUI는 운영범위·표준화 ✓, 효율성·AI네이티브 ×. XML은 운영범위만 ✓.

**7차원 프로토콜 비교 (Section 4)**: 효율성·확장성·보안·신뢰성·확장가능성·운용성·상호운용성 7개 차원에 걸쳐 범용 Inter-Agent 프로토콜 7종을 정성적으로 비교. ANP는 상호운용성·확장성 최고이나 성숙도 제한, A2A는 보안·신뢰성·기업 운용성 우수하나 단일 벤더 주도, MCP는 표준화·보안 강점이나 에이전트 간 직접 통신 불가.

**4개 대표 사용 사례 심층 분석 (Section 5)**: (1) MCP — 단일 에이전트의 다중 도구 호출, (2) A2A — 기업 내 복잡한 에이전트 간 협업, (3) ANP — 크로스도메인 에이전트 프로토콜, (4) Agora — 자연어→프로토콜 동적 생성.

**핵심 기술 통계**: 주요 기반 기술은 RPC(MCP, A2A), OAuth(MCP, A2A), JSON-LD(ANP), DID(ANP, LMOS), Blockchain(AITP), OpenAPI(agents.json, AComP, AConP), HTTP/JSON-RPC 2.0/SSE(A2A), WOT(LMOS), RESTful API(Agent Protocol) 등 9종.

**MCP 아키텍처 컴포넌트 수**: 4개 (Host, Client, Server, Resource). **A2A 핵심 개념 수**: 5개 (Agent Card, Task, Artifact, Message, Parts). **ANP 아키텍처 계층 수**: 3개. **AConP API 수**: 5개. **Agent Communication Trilemma 요소 수**: 3개 (Versatility, Efficiency, Portability).

---

## Limitation

에이전트 프로토콜 분야가 2024~2025년에 급속히 진화 중이므로, 서베이가 공개되는 시점에 이미 일부 프로토콜 사양이 갱신되거나 새로운 프로토콜이 등장할 수 있어 최신성 유지가 어렵다.
7개 차원 평가가 전적으로 정성적(qualitative) 비교에 머물며, 동일한 워크로드·하드웨어에서 측정된 지연시간·처리량·자원 소비 등 정량 벤치마크가 부재하여 실증적 성능 순위 도출이 불가능하다.
도메인 특화 프로토콜(LOKA, PXP, CrowdES, SPPs 등)은 대부분 Concept 또는 Drafting 단계로, 실제 배포 사례나 사용자 피드백이 매우 제한적이어서 실효성 검증이 부족하다.
MCP+A2A, ANP+Agora와 같이 여러 프로토콜을 조합해 사용하는 하이브리드 배포 시나리오에서의 상호작용 효과·호환성 충돌·성능 저하 등에 대한 분석이 다루어지지 않았다.
프로토콜이 실세계 공격(프롬프트 인젝션, 에이전트 스푸핑, 데이터 유출, DDoS)에 얼마나 강건한지에 대한 위협 모델링·보안 감사 결과가 포함되지 않아 엔터프라이즈 배포 전 위험 평가가 어렵다.
서베이 구성상 비영어권·비서구 커뮤니티(중국·한국·일본 등 동아시아)에서 독자적으로 개발 중인 에이전트 프로토콜이 과소 대표될 수 있으며, 특정 프로토콜(MCP, A2A)에 비해 Agora 등 학술 기원 프로토콜에 대한 기술적 세부 논의가 편중된 경향이 있다.

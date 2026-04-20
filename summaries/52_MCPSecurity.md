# Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions

> **논문 정보**: Xinyi Hou, Yanjie Zhao, Shenao Wang, Haoyu Wang (Huazhong University of Science and Technology)
> **arXiv**: 2503.23278 (2025.03, 2025.10 개정)
> **코드**: https://github.com/security-pride/MCP_Landscape

---

## Problem

Anthropic이 2024년 말 공개한 Model Context Protocol(MCP)은 AI 에이전트와 외부 도구·리소스 간의 통신을 표준화하는 개방형 프로토콜로서 빠르게 업계 표준으로 자리 잡고 있다.
MCP는 단방향 function calling과 달리 양방향(bi-directional) 통신, 동적 발견(dynamic discovery), 능력 협상(capability negotiation)을 프로토콜 수준에서 제공하므로 공격 표면이 기존 plugin/function calling 대비 훨씬 넓다.
그러나 학계에서는 MCP에 대한 체계적 보안·아키텍처 분석이 거의 이루어지지 않았고, 어떤 생애주기 단계에서 어떤 유형의 위협이 어떻게 발현되는지에 관한 공식적 분류 체계가 부재하다.
산업계에는 OpenAI, Google DeepMind, Microsoft, Baidu 등이 앞다투어 MCP를 도입하고 MCPWorld·MCP.so 등 커뮤니티 마켓에 수만 개의 서버가 등록되었으나, 이들 서버는 대부분 제3자 플랫폼에서 비검증 상태로 유통된다.
저자들은 MCP.so에서 300개 서버를 무작위 샘플링한 결과 10%가 MCP와 무관하고 6%가 접근 불가였다고 보고하며, 생태계 품질에 대한 검증 메커니즘 부재를 지적한다.
또한 서버 제작·배포·운영·유지 전 단계에 걸쳐 네임스페이스 타이포스쿼팅, 도구 중독(tool poisoning), 러그풀(rug pull), 간접 프롬프트 인젝션, 샌드박스 탈출 등 다양한 공격 벡터가 실증적으로 관찰되어 긴급한 분석이 요구된다.

---

## Motivation

기존 AI 도구 통합 방식(수동 API wiring, ChatGPT 플러그인, LangChain 프레임워크, RAG 등)은 통합 파편화, 단방향 통신, 플랫폼 종속성, 수동 유지보수 부담이라는 한계를 가진다.
MCP는 Language Server Protocol(LSP)에서 영감을 받아 "프로토콜 기반 표준"으로 도구 구현과 사용을 분리하고, 런타임에 도구를 발견·조회·호출할 수 있는 모델 무관(model-agnostic) 인터페이스를 제공한다.
이는 "앱별 하드코딩된 도구 바인딩"에서 "조합 가능하고 발견 가능한 네트워크 서비스의 상호운용 생태계"로의 패러다임 전환을 의미하며, AI-native 애플리케이션의 기반 아키텍처로 부상하고 있다.
그러나 이러한 개방성과 동적 발견 메커니즘 자체가 공급망 공격, 서버 스푸핑, 외부 리소스를 통한 간접 프롬프트 인젝션 등 새로운 위협의 온상이 된다.
특히 tool poisoning·rug pull처럼 "생성 단계에서 심어 두고 운영 단계에서 발현되는" 단계 교차형 공격은 단일 단계 감시만으로는 탐지가 어렵다.
본 논문은 MCP 생태계 최초의 포괄적 분석을 표방하며, 4단계 서버 생애주기(creation/deployment/operation/maintenance)와 16개 핵심 활동을 정식 정의하고, 4가지 공격자 유형 × 16개 위협 시나리오의 3차원 위협 분류 체계를 수립하여 단계별·유형별 방어 전략의 설계 근거를 제공한다.

---

## Method

1. **아키텍처 3계층 정의**: MCP Host(Claude Desktop·Cursor·AI Agent 등 실행 환경) → MCP Client(host 내 중개자로 서버와 1:1 통신) → MCP Server(tools·resources·prompts 제공)의 역할·경계·통신 흐름을 공식 문서와 실제 구현 분석을 통해 형식화한다.
2. **전송 계층(Transport Layer) 통신 모델**: initial request → initial response(능력 나열) → 지속적 notification(상태·진행 갱신) → sampling(사용량·성능 측정)의 4단 흐름을 정의하고, 서버 상태 변화를 실시간 동기화하는 메커니즘과 이로 인한 세션 하이재킹 가능성을 분석한다.
3. **MCP Server 5대 컴포넌트 정립**: Metadata(name/version/description), Configuration(source code/config files/manifest), Tool list(기능·입출력·권한), Resources list(엔드포인트·권한), Prompt templates로 분해하여 각 컴포넌트가 위협의 어느 지점에서 악용될 수 있는지 맵핑한다.
4. **4단계 서버 생애주기 + 16개 핵심 활동 도식화**:
   - Creation(①Metadata Definition ②Capability Declaration ③Code Implementation ④Slash Command Definition)
   - Deployment(⑤MCP Server Release ⑥Installer Deployment ⑦Environment Setup ⑧Tool Registration)
   - Operation(⑨Intent Analysis ⑩External Resource Access ⑪Tool Invocation ⑫Session Management)
   - Maintenance(⑬Version Control ⑭Configuration Change ⑮Access Audit ⑯Log Audit)
5. **4 × 16 위협 분류 체계(Threat Taxonomy) 구축**: 공격자 유형별로 위협을 분류하고 각 위협의 "origin 단계"와 "attack consequence"를 명시한다. 단순히 하나의 단계에 묶지 않고 도입 시점과 발현 시점을 분리(예: tool poisoning은 Creation에서 심어지고 Operation에서 발현).
6. **Malicious Developer 7대 위협 정의**: Namespace Typosquatting(Metadata), Tool Name Conflict·Preference Manipulation·Tool Poisoning·Rug Pulls·Cross-Server Shadowing(Capability Declaration 발원), Command Injection(Code Implementation 발원)을 세분화한다.
7. **External Attacker 2대 위협**: Installer Spoofing(Installer Deployment 단계 변조)과 Indirect Prompt Injection(External Resource Access 경유 LLM 워크플로 오염)을 독립 카테고리로 제시.
8. **Malicious User 4대 위협**: Credential Theft·Sandbox Escape·Tool Chaining Abuse(Tool Invocation 발원)와 Unauthorized Access(Session Management 발원)로 runtime 남용을 구조화한다.
9. **Security Flaws 3대 위협**: Vulnerable Versions·Privilege Persistence(Version Control 발원), Configuration Drift(Configuration Change 발원)로 유지보수 단계 취약점을 정리한다.
10. **PoC 실증 방법론**: 각 위협 유형별로 격리 환경에 PoC MCP 서버를 구축하고, 공식 MCP SDK 기반 커스텀 MCP Host를 구현하여 공격 표면·취약점 발현 방식을 재현한다.
11. **생태계 정량 조사**: 2025년 9월 기준 MCPWorld·MCP.so·Glama·Smithery·PulseMCP 등 26개 MCP 서버 컬렉션을 GitHub·커뮤니티 포럼 기반으로 수집하고, 각 컬렉션의 공시된 서버 수를 공개 리스팅과 교차 검증한다.
12. **신뢰성 샘플링 평가**: MCP.so에서 300개 서버를 무작위 추출해 이름·설명·접근 가능성을 수작업 검증하여 잡음(MCP 무관 프로젝트)과 유령 서버 비율을 정량화한다.
13. **Key Adopter 조사**: Anthropic·OpenAI·Google DeepMind·Microsoft Copilot Studio·Cursor·JetBrains·Cloudflare·Tencent Cloud·Alibaba Cloud·Baidu 등을 수동 검증하여 AI Models/Dev Tools/IDEs/Cloud/Web Automation 5개 카테고리로 분류한다.
14. **SDK·툴 매트릭스**: 공식 지원 언어(TypeScript·Python·Java·Kotlin·C#)와 커뮤니티 도구(EasyMCP·FastMCP·FastAPI to MCP Auto Generator·Foxy Contexts·Higress MCP Server Hosting·Mintlify·Speakeasy·Stainless)의 역할을 정리한다.
15. **단계별 방어 전략 도출**: 각 위협의 origin 단계를 기준으로 검증·격리·감사 대응책을 제안하며, "단일 단계 방어"가 아닌 "라이프사이클 연쇄 방어"를 원칙으로 제시한다.

---

## Key Contribution

1. **MCP 최초의 포괄적 학술 분석**: 아키텍처·통신·컴포넌트·라이프사이클을 공식 문서와 실제 워크플로 기반으로 체계화한 최초의 심층 연구를 제시한다.
2. **4단계 × 16활동 라이프사이클 모델**: creation/deployment/operation/maintenance 각 단계를 16개 핵심 활동으로 분해하여 위협 원점 매핑과 세분화된 방어 설계의 공통 기반을 제공한다.
3. **3차원 위협 분류 체계**: 공격자 유형(4) × 위협 시나리오(16) × 라이프사이클 단계의 교차 테이블을 최초로 구축하고, origin-consequence 분리를 통해 단계 교차형 공격을 명시적으로 포착한다.
4. **PoC 실증**: 16개 위협에 대응하는 PoC MCP 서버를 격리 환경에서 구현하고 커스텀 호스트로 공격 표면을 재현하여 이론적 분류를 실증으로 뒷받침한다.
5. **생태계 정량 지도**: 26개 주요 MCP 컬렉션과 수만 개 서버의 분포, 채택 기업·SDK·커뮤니티 도구를 체계적으로 정리하여 산업 현황의 기준 스냅샷을 남긴다.
6. **신뢰성 평가 사례 연구**: MCP.so 300개 샘플링을 통해 10%가 MCP 무관, 6%가 접근 불가라는 생태계 잡음 지표를 제시하고, 큐레이션·검증 기준 부재 문제를 정량화한다.
7. **단계별 실행 가능한 보안 지침**: 각 생애주기 단계·위협 유형에 대응하는 세분화된 방어 전략(least privilege, sandbox policy, capability scanning, installer integrity 등)을 제안하여 실무자에게 직접 적용 가능한 체크리스트를 제공한다.

---

## Experiment

본 논문은 서베이·비전 페이퍼 성격이 강하나, 위협 실증 PoC와 생태계 정량 조사를 경험적 근거로 수행한다.

**생태계 규모 (2025년 9월 스냅샷, 총 26개 컬렉션 집계)**:
- MCPWorld(Baidu): 26,404개 서버 — 단일 플랫폼 기준 최대 규모.
- MCP.so: 16,592개, MCP Servers Repository: 13,596개, AIbase MCP: 12,448개로 상위 4개 웹 플랫폼이 모두 1만 개 이상을 호스팅.
- Glama: 9,415개, Smithery: 6,888개, PulseMCP: 6,072개, ModelScope MCP Marketplace: 5,441개로 중상위권 유지.
- Anthropic 공식 컬렉션(GitHub modelcontextprotocol/servers): 1,204개 — 커뮤니티 대비 상대적으로 작지만 검증된 리스트.
- 하위권: Toolbase 24개, mkinf 23개, Awesome Crypto MCP Servers 12개 등 소규모 전문 컬렉션.

**신뢰성 샘플링 결과(MCP.so 300개 무작위 샘플)**:
- 30개(10%)는 프로젝트명에 "MCP"가 포함되나 Model Context Protocol과 무관한 프로젝트로 확인.
- 18개(6%)는 개발 중 상태이거나 조사 시점에 접근 불가.
- 즉 표본 중 약 16%가 신뢰할 수 없는 항목으로, 생태계 잡음 비율의 하한을 제시.

**채택 현황**: Anthropic(Claude Desktop 전 기능 지원), OpenAI(Agents SDK 및 ChatGPT 개발자 모드), Google DeepMind(Gemini 계열), Baidu Maps, Blender MCP, Replit, Microsoft Copilot Studio(2025년 3월 공식 발표), Sourcegraph Cody, Codeium, Cursor, Cline, Zed, JetBrains, Windsurf Editor, Theia AI/IDE, Emacs MCP, OpenSumi, Cloudflare, Tencent Cloud, Alibaba Cloud Bailian, Huawei Cloud, Block(Square), Stripe, Alipay/Ant Group, Apify MCP Tester, LibreChat, Baidu Create Conference 등 다수.

**SDK 지원**: 공식 5개 언어(TypeScript, Python, Java, Kotlin, C#) + 커뮤니티 프레임워크(EasyMCP, FastMCP, FastAPI to MCP Auto Generator, Foxy Contexts[Go], Higress MCP Server Hosting[Envoy+wasm]) + 서버 생성 플랫폼(Mintlify, Speakeasy, Stainless).

**위협 분류 통계(16개 시나리오)**:
- Malicious Developer: 7개(43.75%)로 최다 — Creation 단계가 공격 도입의 최대 발원지임을 시사.
- External Attacker: 2개(12.5%) — Installer Spoofing(Deployment), Indirect Prompt Injection(Operation).
- Malicious User: 4개(25%) — 전원 Operation 단계 발현(3개 Tool Invocation, 1개 Session Management).
- Security Flaws: 3개(18.75%) — 2개 Version Control(Maintenance), 1개 Configuration Change.

**발원 단계 분포**: Creation 7개, Operation 6개, Maintenance 2개, Deployment 1개 → 전체의 약 44%가 Creation 단계에서 시작되므로, 메타데이터·능력 선언·코드 구현 단계의 검증이 최우선 방어 지점임을 실증 데이터로 제시.

**PoC 환경**: 공식 MCP SDK 기반 커스텀 MCP Host + 각 위협별 PoC 서버를 격리 환경에서 배포하여 Namespace Typosquatting에서 Configuration Drift까지 16개 시나리오의 공격 표면을 재현. 단, 공격 성공률이나 다양한 베이스 LLM 간의 반응 차이에 대한 정량 평가는 후속 작업으로 남김.

---

## Limitation

저자 명시 한계: 본 연구의 PoC는 위협 가능성의 시연에 초점을 두며, 공격 성공률(attack success rate) 정량화나 다양한 베이스 LLM(Claude, GPT, Gemini 등) 사이의 행동 차이 평가는 범위에서 제외되어 있어 실제 배포 환경에서의 위험도 비교가 어렵다.
생태계 조사는 수작업 수집과 공시된 서버 수 교차 검증에 의존하므로 완전성(exhaustiveness)을 보장하지 못하며, 저자도 "대표성 있는 스냅샷이지만 망라적이지는 않다"고 명시한다.
위협 분류는 공격자 유형·라이프사이클 단계 기반의 정성 분석 위주이며, 각 위협이 실제로 발생할 확률·영향도를 수치화한 정량적 위험 모델(CVSS 등)이 부재하다.
독자 관점 한계: MCP 사양과 생태계가 빠르게 진화 중이므로(2024년 말 출시 이후 1년도 안 되어 수만 개 서버 등록) 본 연구의 스냅샷 분석은 수 개월 단위로 유효성이 감소할 수 있다.
제안된 방어 전략은 원칙·체크리스트 수준으로, 실제 구현·자동화 도구나 방어 효과의 실증 평가(예: 방어 적용 전후 공격 성공률 변화)가 제공되지 않는다.
300개 샘플링은 MCP.so 단일 플랫폼에 국한되어, 다른 컬렉션(MCPWorld, Glama 등)의 품질 분포로 일반화하기 어렵다.
마지막으로, 플랫폼 거버넌스·walled garden 문제나 데이터 거주(data residency) 요구처럼 기술 외적 요인이 MCP 확산에 미치는 영향은 논의 수준에 머물며, 정책적 해법이나 거버넌스 프레임워크 설계는 후속 연구로 남겨진다.

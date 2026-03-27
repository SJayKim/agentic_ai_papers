# A Survey of AI Agent Protocols

> **논문 정보**: Yingxuan Yang, Huacan Chai, Yuanyi Song et al. (Shanghai Jiao Tong University)
> **arXiv**: 2504.16736 (2025.04, v3: 2025.06)
> **코드**: https://github.com/zoe-yyx/Awesome-AIAgent-Protocol

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트가 다양한 산업에 배포되고 있지만, 에이전트-도구 간, 에이전트-에이전트 간 통신에 표준 프로토콜이 없어 상호운용성·확장성이 심각하게 저해된다. 각 LLM 제공자가 독자적 tool 호출 형식을 구현하여 개발·유지보수 비용이 급증한다. |
| **Motivation** | TCP/IP·HTTP가 초기 인터넷 단편화를 해결했듯, 표준화된 에이전트 프로토콜은 "에이전트 인터넷"의 집단 지성을 실현할 수 있다. MCP, A2A, ANP 등 프로토콜이 빠르게 등장하고 있으나, 이를 체계적으로 분류·비교한 연구가 없다. |
| **Limitation** | 프로토콜이 급속히 진화 중이라 분석의 최신성 유지가 어려움. 대부분의 비교가 정성적 분석에 그치며, 실제 워크로드 기반의 정량적 성능 측정이 부재함. 도메인 특화 프로토콜의 실증 검증이 제한적이며, 프로토콜 간 조합 사용 시의 상호작용 효과도 미분석. |

---

## Method

**1. 2차원 분류 프레임워크**
- **축 1**: 컨텍스트 지향(Context-Oriented) vs 에이전트 간(Inter-Agent)
- **축 2**: 범용(General-Purpose) vs 도메인 특화(Domain-Specific)
- 4개 셀에 총 16개 프로토콜 배치

**2. 컨텍스트 지향 프로토콜**
- **MCP (Anthropic, 2024)**: Host-Client-Server-Resource 4-컴포넌트. 클라이언트-서버 분리로 데이터 유출 위험 저감, OAuth 기반 인증
- **agents.json (WildCardAI, 2025)**: OpenAPI 위에 구축된 머신 리더블 JSON 명세. `flows`(API 호출 시퀀스)와 `links`(액션 간 의존성) 도입

**3. 에이전트 간 프로토콜**
- **ANP**: 탈중앙화 3계층 — W3C DID 기반 신원 인증, 자연어 메타프로토콜(Agora), 애플리케이션 프로토콜
- **A2A (Google, 2025)**: HTTP(S) + JSON-RPC 2.0 + SSE. Agent Card, Task, Artifact, Message, Parts 5개 핵심 개념. 비동기 우선, 멀티모달 지원
- **AITP (NEAR, 2025)**: Blockchain 기반 신뢰 경계 횡단, 자율 협상 및 가치 교환
- **AConP (Cisco/LangChain)**: 에이전트 검색·실행·중단/재개·스레드 관리·출력 스트리밍 5개 API
- **AComP (IBM/BeeAI)**: REST 기반, SDK 불필요, MIME 멀티파트 메시지
- **Agora (Oxford, 2024)**: 에이전트 통신 트릴레마(다양성·효율성·이식성) 해결 메타프로토콜

**4. 비교 평가 7개 차원**: 효율성, 확장성, 보안성, 신뢰성, 확장 가능성, 운용성, 상호운용성

**5. 상호작용 방식 비교**: API, GUI, XML, Protocol 4가지 중 Protocol만이 효율성·운영 범위·표준화·AI 네이티브 호환성 모두 최고

---

## Key Contribution

1. **최초의 2차원 에이전트 프로토콜 분류 체계**: 16개 프로토콜을 컨텍스트/에이전트간 × 범용/도메인특화로 체계화
2. **7개 차원 정성적 비교 분석**: 프로토콜별 강약점 매핑
3. **미래 연구 로드맵**: 단기(정적→진화형), 중기(규칙→생태계), 장기(프로토콜→지능 인프라) 3단계 전망
4. **실용 가이드**: MCP, A2A, ANP, Agora 사용 시나리오별 프로토콜 선택 기준 제공

---

## Experiment & Results

서베이 논문으로, 정성적 비교 및 케이스 스터디를 수행.

**프로토콜 성숙도 분포**:
- Landing(실사용): MCP, A2A, ANP, Agent Protocol, LMOS — 5개
- Drafting(초안): agents.json, AITP, AConP, AComP, Coral, Agora 등 — 10개
- Concept(개념): LOKA, PXP — 2개

**프로토콜별 강점 요약**:
- **MCP**: 높은 표준화·확장성, 보안 강화. 에이전트 간 직접 통신 불가
- **A2A**: 기업 환경 최적화, 비동기 장기 실행. 단일 제공자 주도 우려
- **ANP**: 탈중앙화 P2P, 크로스도메인 상호운용성 최고. 성숙도 제한
- **Agora**: 통신 트릴레마 해결. 실증 벤치마크 부족

**사용 시나리오별 권장**: 단일 에이전트 → 다중 도구: MCP / 기업 내 협업: A2A / 크로스도메인: ANP / 동적 프로토콜 생성: Agora

**미래 전망**: 단기(적응형 프로토콜), 중기(생태계 수준 조율), 장기(계층화 아키텍처 및 집단 지성 인프라)

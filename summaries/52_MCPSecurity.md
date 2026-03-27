# Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions

> **논문 정보**: Xinyi Hou, Yanjie Zhao, Shenao Wang, Haoyu Wang (Huazhong University of Science and Technology)
> **arXiv**: 2503.23278 (2025.03)
> **코드**: https://github.com/security-pride/MCP_Landscape

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | Anthropic이 2024년 말 출시한 MCP가 AI 에이전트의 표준 프로토콜로 빠르게 확산되고 있지만, 보안 위협에 대한 체계적 분석이 부재하다. MCP 서버·클라이언트 간 통신, 도구 실행, 데이터 접근 전반에 걸쳐 다양한 공격 벡터가 존재하며, 양방향 통신·동적 발견이 가능해 공격 표면이 기존 plugin보다 넓다. |
| **Motivation** | OpenAI, Google DeepMind, Microsoft, Baidu 등 주요 AI 플랫폼이 MCP를 채택하고, Smithery·MCP.so 등 커뮤니티 마켓에 수만 개 서버가 등록될 만큼 성장했다. 그러나 아카데미아에서의 심층 분석은 전무하며, 공급망 공격·프롬프트 인젝션·세션 하이재킹 등 현실적 위협이 실제 배포 환경에서 확인된다. |
| **Limitation** | 저자 언급: PoC는 격리 환경에서의 가능성 시연이며 실제 공격 성공률이나 다양한 LLM 간 행동 차이를 평가하지 않는다. 독자 관점: MCP 사양이 빠르게 진화하므로 분석의 유효 기간이 짧을 수 있고, 정량적 취약점 실험 결과가 아닌 분류·시나리오 분석 위주여서 방어책 효과에 대한 실증이 부족하다. |

---

## Method

1. **MCP 아키텍처 분석**: MCP Host(AI 애플리케이션 환경) → MCP Client(1:1 중개자) → MCP Server(도구·리소스·프롬프트 제공)의 3계층 구조 정의. 전송 계층은 초기 요청-응답과 지속적 알림(notification)으로 구성.

2. **4단계 서버 라이프사이클 정의**:
   - **Creation**: 메타데이터 정의, 능력 선언, 코드 구현, 슬래시 커맨드 정의
   - **Deployment**: 서버 릴리즈, 인스톨러 배포, 환경 설정, 도구 등록
   - **Operation**: 인텐트 분석, 외부 리소스 접근, 도구 호출, 세션 관리
   - **Maintenance**: 버전 관리, 설정 변경, 접근 감사, 로그 감사

3. **16개 핵심 활동 식별**: 4단계 전반의 세부 활동을 체계적으로 분류하여 위협 원점 매핑 기반 제공.

4. **4가지 공격자 유형 × 16개 위협 시나리오 분류**:
   - **Malicious Developer (7개)**: Namespace Typosquatting, Tool Name Conflict, Preference Manipulation, Tool Poisoning, Rug Pulls, Cross-Server Shadowing, Command Injection
   - **External Attacker (2개)**: Installer Spoofing, Indirect Prompt Injection
   - **Malicious User (4개)**: Credential Theft, Sandbox Escape, Tool Chaining Abuse, Unauthorized Access
   - **Security Flaws (3개)**: Vulnerable Versions, Privilege Persistence, Configuration Drift

5. **PoC 검증**: 각 위협 유형에 대응하는 PoC MCP 서버를 격리 환경에서 구축하고, 공식 MCP SDK 기반 커스텀 호스트로 공격 표면 및 취약점 발현 방식 실증.

6. **생태계 현황 분석**: 2025년 9월 기준 26개 MCP 서버 컬렉션 수집·검증, 산업계 채택 현황, SDK 지원 언어, 활용 사례 분석.

---

## Key Contribution

1. **MCP 최초의 포괄적 보안·생태계 분석**: 4단계 라이프사이클 × 4가지 공격자 유형 × 16개 위협 시나리오의 3차원 위협 분류 체계 구축
2. **PoC 기반 취약점 실증**: 이론적 분류를 넘어 격리 환경에서 각 위협 유형별 실제 공격 표면 시연
3. **생태계 정량 조사**: 26개 컬렉션(총 수만 개 서버) 체계적 수집·분류, 300개 서버 샘플링 신뢰도 평가
4. **단계별 보안 대책 제안**: 라이프사이클 각 단계 및 위협 유형에 맞춘 세분화된 방어 전략 제시

---

## Experiment & Results

- 서베이 논문으로, 위협 분류·PoC 시연·생태계 조사에 초점.

**생태계 규모** (2025년 9월 기준):
- MCPWorld: 26,404개, MCP.so: 16,592개, MCP Servers Repository: 13,596개 등 26개 주요 컬렉션
- Anthropic 공식: GitHub에 1,204개 서버 보유

**신뢰성 샘플링**: MCP.so 300개 무작위 샘플링 — 30개(10%)는 MCP와 무관, 18개(6%)는 개발 중/접근 불가

**채택 현황**: Anthropic, OpenAI, Google DeepMind, Microsoft Copilot Studio, Cursor, JetBrains, Cloudflare, Tencent Cloud, Alibaba Cloud, Baidu 등 채택

**공격 유형별 위협 원점**: 7개가 Creation 단계 발원(가장 많음), 4개 Operation, 2개 Maintenance, 1개 Deployment → 초기 설계·선언 단계의 보안 강화가 핵심

| 항목 | 수치 |
|------|------|
| 분석 대상 컬렉션 수 | 26개 |
| 최대 서버 보유 플랫폼 | 26,404개 |
| 식별된 위협 시나리오 수 | 16개 |
| 라이프사이클 단계 수 | 4단계 (16개 활동) |

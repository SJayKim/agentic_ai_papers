---
name: paper
description: 논문 제목/arXiv ID/컨퍼런스 키워드를 받아 PDF 확보 → 요약 → 개요 업데이트 → Notion 업로드까지 전체 파이프라인 실행
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Agent
---

# 논문 정리 전체 파이프라인

대상 논문: **$ARGUMENTS**

---

## 다건 처리 규칙

`$ARGUMENTS`에 여러 논문이 포함될 수 있습니다 (쉼표, 줄바꿈, 또는 공백으로 구분).

**파싱 방법:**
- 쉼표(`,`) 구분: `MemoryBank, RAISE, CoALA`
- 줄바꿈 구분 (여러 줄 입력)
- arXiv ID 혼합: `MemoryBank, 2401.12345, "Cognitive Architectures for Language Agents"`

**처리 순서:**
1. 입력을 개별 논문 단위로 파싱
2. **모든 논문에 대해 Step 0(중복 검사)을 먼저 일괄 수행** → 결과를 사용자에게 한번에 보고
   - 이미 존재하는 논문은 목록에서 제외
   - 유사 논문이 있으면 확인 요청
3. 통과한 논문들에 대해 Step 1~4를 **한 편씩 순서대로** 수행
4. 모든 논문 처리 후 최종 결과를 요약 보고

**번호 관리:** 첫 논문 처리 전 마지막 번호를 확인하고, 이후 논문마다 +1씩 증가

**⚠ 대량 처리 시 배치 분할:** **3편 단위**로 나누어 처리. 한 배치가 끝나면 다음 배치 시작 전 사용자에게 진행 상황 보고.

---

## Step 0: 중복 검사 (필수 — 모든 논문에 대해 먼저 실행)

각 논문이 이미 정리되었는지 확인하세요. 아래 3곳을 모두 체크합니다:

1. **개요 파일**: `agent_memory_papers.md`에서 논문 제목/약칭을 검색 (Grep)
2. **요약 파일**: `summaries/` 디렉토리의 파일명에서 약칭을 검색 (Glob)
3. **PDF 파일**: `summaries/agent_memory_pdfs/` 디렉토리에서 파일명 검색 (Glob)

**판단 기준:**
- 정확히 같은 논문이 이미 존재하면 → "이미 {번호}_{약칭}.md로 정리되어 있습니다"라고 알리고 해당 논문은 **건너뜀**
- 유사한 제목의 다른 논문이 있으면 → "유사한 논문 '{기존 논문명}'이 있습니다. 다른 논문이 맞나요?"라고 확인
- 존재하지 않으면 → Step 1 대상에 포함

**일괄 보고 형식:**
```
중복 검사 결과:
- MemoryBank → 신규 ✅
- A-MEM → 이미 존재 (01_A-MEM.md) ❌
- RAISE → 유사 논문 있음 (AgentRefine) — 확인 필요 ⚠️
```

## Step 1: 논문 PDF 확보

1. 논문을 검색하세요 (WebSearch 활용)
   - 논문 제목, arXiv ID, 컨퍼런스 키워드 등 어떤 형태든 가능
2. arXiv 또는 공식 소스에서 PDF URL을 찾으세요
3. PDF를 다운로드하여 `summaries/agent_memory_pdfs/{논문약칭}.pdf`에 저장하세요
   - 약칭은 논문의 핵심 키워드나 시스템 이름 (예: A-MEM, MAGMA, ChainOfAgents)
4. PDF 텍스트를 추출하세요
   - **⚠ Read 도구의 PDF 지원은 이 환경에서 동작하지 않음** (`pdftoppm` 미설치)
   - **반드시 Bash + PyPDF2로 텍스트 추출 후 파일로 저장**:
     ```
     python -c "
     import PyPDF2, sys
     sys.stdout.reconfigure(encoding='utf-8')
     reader = PyPDF2.PdfReader(r'summaries/agent_memory_pdfs/{논문약칭}.pdf')
     with open(r'summaries/agent_memory_pdfs/{논문약칭}_text.txt', 'w', encoding='utf-8') as f:
         for i in range(min(15, len(reader.pages))):
             text = reader.pages[i].extract_text()
             f.write(f'=== PAGE {i+1} ===\n')
             f.write(text[:4000] if text else '[empty]')
             f.write('\n\n')
     "
     ```

## Step 2: 요약 마크다운 작성 — 서브에이전트 활용

### 핵심 원칙: PDF 분석은 서브에이전트에게 위임하여 컨텍스트를 분리한다.

**서브에이전트는 파일을 쓸 수 없지만, PDF를 읽고 분석한 결과를 텍스트로 반환할 수 있다.**
이를 활용하여 메인 컨텍스트의 오염 없이 각 논문을 독립적으로 분석한다.

### 실행 절차

1. **서브에이전트 실행** (Agent 도구, subagent_type="general-purpose"):
   ```
   프롬프트:
   "아래 논문의 텍스트 파일을 읽고, summarize_instruction.md의 템플릿에 맞는 완전한 요약 마크다운을 작성하여 반환하세요.

   - 텍스트 파일 경로: summaries/agent_memory_pdfs/{약칭}_text.txt
   - 템플릿 참조: summarize_instruction.md

   품질 기준 (전체 80줄 이상):
   - Problem: 5~8줄, 기존 접근법의 구체적 실패 원인
   - Motivation: 5~8줄, 핵심 직관/관찰, 왜 이 접근이 합리적인지
   - Method: 15~25줄, 번호 매긴 단계별 설명, 각 컴포넌트 동작 방식
   - Key Contribution: 5~10줄, 각 기여가 어떤 기존 한계를 해결하는지
   - Experiment: 10~20줄, 데이터셋/baseline/구체적 수치/ablation 포함
   - Limitation: 5~8줄, 저자 언급 + 독자 관점 + 실제 영향 분석

   반환 형식: 완전한 마크다운 텍스트 (파일 쓰기는 하지 말 것, 텍스트만 반환)"
   ```

2. **메인 대화에서 파일 저장**: 서브에이전트가 반환한 마크다운을 Write로 저장
   ```
   summaries/{번호}_{논문약칭}.md
   ```

3. **다건 처리 시**: 각 논문마다 별도의 서브에이전트를 실행하여 컨텍스트 격리. 병렬 실행도 가능(단, 파일 쓰기는 메인에서 순차).

## Step 2.5: 품질 평가 루프 (필수 — 건너뛰지 않는다)

**논문 1편당 1개 평가 에이전트**를 실행하여 컨텍스트 오버로드를 방지한다.
요약 작성과 분리된 새 세션에서 평가하여 편향 없는 판단을 보장한다.

### 컨텍스트 관리 원칙

1. **1 에이전트 = 1 논문**: 평가·보강 에이전트는 반드시 논문 1편만 담당
2. **병렬 실행**: 배치 내 논문들의 평가/보강 에이전트를 동시에 실행
3. **메인 컨텍스트 최소화**: Write 저장 후 즉시 다음으로 진행, 이전 논문 상세 재참조 안 함

### 평가 루프

```
[배치 요약 완료 (3편)]
  → 논문 1편당 1개 평가 에이전트 (3개 병렬)
    → 각 에이전트: 요약 1편 + 원본 PDF 1편만 읽고 평가
    → PASS / FAIL + 피드백 반환
  → FAIL 논문에 대해 1편당 1개 보강 에이전트 (병렬)
  → 메인에서 Write 반영 → 재평가 (최대 2회, 역시 1편당 1개)
  → 전수 PASS → Step 3
```

### 평가 에이전트 (1편당 1개)

```
Agent 도구 (subagent_type="general-purpose") 프롬프트:

"논문 요약 품질 평가자입니다. 1편의 요약을 원본 PDF 텍스트와 비교 평가하세요.

평가 대상:
- 요약: summaries/{번호}_{약칭}.md
- 원본: agent_memory_pdfs/{약칭}_text.txt

평가 기준:
[A] 분량 — 전체 80줄↑, Problem 5줄↑, Motivation 5줄↑, Method 15줄↑, Experiment 10줄↑, Limitation 5줄↑, 수치 5개↑
[B] 충실도 — 6개 섹션 각각의 구체성 평가

반환:
## {번호}_{약칭}
- 판정: PASS / FAIL
- 각 섹션 줄수, 수치 개수
- [A] 분량: PASS/FAIL (사유)
- [B] 충실도: PASS/FAIL (사유)
- 보강 필요 사항: (FAIL 시 구체적 지시)

파일 수정하지 말고 텍스트로만 반환."
```

### FAIL 시 보강 (1편당 1개)

FAIL 논문마다 **별도 보강 에이전트** 실행:

```
Agent 도구 프롬프트:

"아래 논문 요약을 보강하세요.
- 현재 요약: summaries/{번호}_{약칭}.md
- 원본 PDF: agent_memory_pdfs/{약칭}_text.txt
- 평가 피드백: {피드백 내용}

보강 기준: Problem 5~8줄, Motivation 5~8줄, Method 15~25줄, Experiment 10~20줄, Limitation 5~8줄.
평가에서 지적된 부분만 보강. 보강된 전체 마크다운을 텍스트로 반환."
```

메인에서 Write 반영 후 재평가. 최대 2회 반복 후 Step 3 진행.

## Step 3: 개요 파일 업데이트

`agent_memory_papers.md`의 적절한 카테고리 테이블에 새 행을 추가하세요.

- 5열 구조: | 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |
- 아래 6개 카테고리 중 택1:
  1. **Memory Management** — 메모리 저장/검색/구조화/진화
  2. **Tool Use & MCP** — 외부 도구 호출, function calling, MCP
  3. **Planning & Task Decomposition** — 작업 분할, 계획 수립, 오케스트레이션
  4. **Self-Correction & Test-Time Compute** — 자가 교정, 추론 시간 연산, RL 기반 학습
  5. **Agentic RAG & Graph RAG** — 지식 그래프, 그래프 RAG, 능동적 검색
  6. **General** — 위 5개에 해당하지 않는 에이전트 아키텍처/서베이/기타

## Step 4: Notion 업로드

@notion_mcp_instruction.md 를 참고하여 Notion에 반영하세요.

1. 기존 블록 구조 조회 (GET /blocks/{메인페이지ID}/children)
2. 메인 페이지 카테고리 테이블 업데이트
3. **하위 논문 상세 페이지 생성 — 반드시 로컬 마크다운 파일을 Read로 읽어서 내용 반영**
   - `summaries/{번호}_{약칭}.md`를 Read로 읽는다
   - 각 섹션(Problem, Motivation, Method, Key Contribution, Experiment, Limitation)을 파싱하여 Notion 토글 블록으로 변환
   - **내용을 별도로 재작성하거나 하드코딩하지 않는다**
4. Callout 업데이트 (논문 수/카테고리 수)
5. 블록 순서 검증

**⚠ 실행 방식 — Python `requests` 직접 호출:**
- MCP 서버나 에이전트 대신, **Bash에서 Python 스크립트로 Notion API를 직접 호출**할 것
- 토큰 읽기: `.claude/.mcp.json` → `mcpServers.notion.env.NOTION_TOKEN`
- 필수 헤더: `Authorization: Bearer {TOKEN}`, `Notion-Version: 2022-06-28`
- 대량 페이지 생성 시 하나의 Python 스크립트에서 루프로 처리 (rate limit 준수: `time.sleep(0.5)`)

**기술적 주의사항:**
- `python` 사용 (`python3` 아님)
- 파일 인코딩: 항상 `encoding='utf-8'`
- rich_text 2000자 제한, children 100개 제한
- Rate Limit: API 호출 간 0.3~0.5초
- 블록 위치: `after` 파라미터 필수 사용
- **에이전트(subagent)로 Notion 업로드를 위임하지 말 것** — 권한 문제로 실패함

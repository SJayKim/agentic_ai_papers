---
name: paper-summary
description: 논문 요약만 수행 (Notion 업로드 제외). PDF 확보 → 요약 작성 → 개요 업데이트
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Agent
---

# 논문 요약 파이프라인 (Notion 제외)

대상 논문: **$ARGUMENTS**

---

## 다건 처리 규칙

`$ARGUMENTS`에 여러 논문이 포함될 수 있습니다 (쉼표, 줄바꿈, 또는 공백으로 구분).

**처리 순서:**
1. 입력을 개별 논문 단위로 파싱
2. **모든 논문에 대해 Step 0(중복 검사)을 먼저 일괄 수행** → 결과를 사용자에게 한번에 보고
3. 통과한 논문들에 대해 Step 1~3을 **한 편씩 순서대로** 수행
4. 모든 논문 처리 후 최종 결과를 요약 보고

**⚠ 대량 처리 시 배치 분할:** **3편 단위**로 나누어 처리. 한 배치 완료 후 사용자에게 진행 보고.

---

## Step 0: 중복 검사 (필수 — 모든 논문에 대해 먼저 실행)

각 논문이 이미 정리되었는지 확인하세요. 아래 3곳을 모두 체크합니다:

1. **개요 파일**: `agent_memory_papers.md`에서 논문 제목/약칭을 검색 (Grep)
2. **요약 파일**: `summaries/` 디렉토리의 파일명에서 약칭을 검색 (Glob)
3. **PDF 파일**: `summaries/agent_memory_pdfs/` 디렉토리에서 파일명 검색 (Glob)

**판단 기준:**
- 정확히 같은 논문이 이미 존재하면 → 해당 논문은 **건너뜀**
- 유사한 제목의 다른 논문이 있으면 → 확인 요청
- 존재하지 않으면 → Step 1 대상에 포함

## Step 1: 논문 PDF 확보

1. 논문을 검색하세요 (WebSearch 활용)
2. arXiv 또는 공식 소스에서 PDF를 다운로드
3. `summaries/agent_memory_pdfs/{논문약칭}.pdf`에 저장
4. PDF 텍스트를 추출하여 `{논문약칭}_text.txt`로 저장
   - **⚠ Read 도구의 PDF 지원은 이 환경에서 동작하지 않음** (`pdftoppm` 미설치)
   - **반드시 Bash + PyPDF2로 텍스트 추출** (CLAUDE.md의 "PDF 읽기" 섹션 참조)

## Step 2: 요약 마크다운 작성 — 서브에이전트 활용

### 핵심 원칙: PDF 분석은 서브에이전트에게 위임하여 컨텍스트를 분리한다.

서브에이전트는 파일을 쓸 수 없지만, PDF를 읽고 분석한 결과를 텍스트로 반환할 수 있다.

### 실행 절차

1. **서브에이전트 실행** (Agent 도구):
   - 프롬프트에 텍스트 파일 경로와 품질 기준을 명시
   - 서브에이전트가 PDF 텍스트를 읽고 요약 마크다운을 텍스트로 반환
   - 품질 기준 (전체 80줄 이상): Problem 5~8줄, Motivation 5~8줄, Method 15~25줄, Experiment 10~20줄, Limitation 5~8줄, 구체적 수치 5개↑

2. **메인 대화에서 파일 저장**: 서브에이전트가 반환한 마크다운을 Write로 저장

3. **다건 처리 시**: 각 논문마다 별도의 서브에이전트를 실행하여 컨텍스트 격리

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
Agent 프롬프트: "요약 품질 평가자. 1편의 요약을 원본 PDF와 비교.
- 요약: summaries/{번호}_{약칭}.md
- 원본: agent_memory_pdfs/{약칭}_text.txt
[A] 분량 — 전체 80줄↑, Problem 5줄↑, Motivation 5줄↑, Method 15줄↑, Experiment 10줄↑, Limitation 5줄↑, 수치 5개↑
[B] 충실도 — 6개 섹션 각각의 구체성 평가
PASS/FAIL + 보강 사항 반환. 파일 수정 안 함."
```

### FAIL 시 보강 에이전트 (1편당 1개)

```
Agent 프롬프트: "요약 보강. 현재 요약+원본 PDF+피드백을 읽고 부족한 부분만 보강.
Problem 5~8줄, Motivation 5~8줄, Method 15~25줄, Experiment 10~20줄, Limitation 5~8줄.
보강된 전체 마크다운 텍스트 반환."
```

메인에서 Write 반영 후 재평가. 최대 2회.

## Step 3: 개요 파일 업데이트

`agent_memory_papers.md`의 적절한 카테고리 테이블에 새 행 추가 (5열 구조).
- 카테고리 7개 중 택1: Memory Management / Tool Use & MCP / Planning & Task Decomposition / Self-Correction & Test-Time Compute / Agentic RAG & Graph RAG / General / Harness Engineering

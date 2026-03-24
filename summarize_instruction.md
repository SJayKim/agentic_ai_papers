# 논문 정리 전체 파이프라인

## 개요

논문 정리 요청이 들어오면 아래 파이프라인을 **순서대로** 수행한다.

```
[논문 정리 요청]
  → Step 1: 논문 PDF 확보 및 저장
  → Step 2: 요약(Summary) 마크다운 작성
  → Step 3: 개요 파일(agent_memory_papers.md) 업데이트
  → Step 4: Notion 업로드
```

---

## Step 1: 논문 PDF 확보 및 저장

1. 사용자가 논문 제목, arXiv ID, 또는 PDF 파일을 제공
2. PDF가 없으면 arXiv 등에서 다운로드
3. `agent_memory_pdfs/` 폴더에 저장
   - 파일명 규칙: `{논문약칭}.pdf` (예: `A-MEM.pdf`, `MAGMA.pdf`)
4. PDF가 텍스트 추출이 어려운 경우 `{논문약칭}_text.txt`로 텍스트 버전도 저장

## Step 2: 요약(Summary) 마크다운 작성

### 파일 위치 및 명명 규칙

- 경로: `summaries/{번호}_{논문약칭}.md`
- 번호: `agent_memory_papers.md`의 기존 논문 수 + 1 (2자리, 01~99)
- 예: `summaries/14_NewPaper.md`

### 요약 템플릿

아래 구조를 따라 작성한다. PDF를 읽고 각 항목을 채운다.

```markdown
# {논문 정식 제목}

> **논문 정보**: {저자} ({소속})
> **arXiv**: {arXiv ID} ({날짜})
> **코드**: {GitHub URL 있으면 기재}

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | {이 논문이 해결하려는 문제. 기존에 왜 안 됐는가} |
| **Motivation** | {왜 이 문제가 중요한가. 실제 한계/실패 사례} |
| **Method** | {핵심 메커니즘: 아키텍처, 알고리즘, 파이프라인} |
| **Key Contribution** | {기존 대비 novelty. 번호 매겨서 나열} |
| **Experiment/Results** | {벤치마크, 주요 수치, 비교 결과} |
| **Limitation** | {저자가 밝힌 한계 + 읽으면서 느낀 한계} |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | {비교 대상과 수치 차이} |
| **Ablation Study** | {컴포넌트 제거 시 성능 변화} |
| **Taxonomy/분류 체계** | {서베이 논문의 경우 분류 축} |
| **Threat Model** | {보안 논문의 경우 공격자 모델} |
```

### 작성 가이드라인

1. **Problem → Method → Result 흐름**을 유지하면 논문 간 비교가 쉬워진다
2. **Method는 핵심 메커니즘 위주로 구조적으로** 작성한다. 번호를 매겨 단계별로 설명
3. **Experiment는 구체적 수치를** 포함한다. "성능이 좋다" 대신 "F1=45.85 vs MemGPT 25.52"
4. **Limitation은 저자 언급 + 독자 관점** 두 가지 모두 기록한다

## Step 3: 개요 파일 업데이트

`agent_memory_papers.md`에 새 논문을 추가한다.

1. 논문이 속하는 카테고리를 판단 (기존 4개 카테고리 중 택1, 또는 새 카테고리 생성)
2. 해당 카테고리 테이블에 새 행 추가:
   ```
   | **{논문약칭}** | {학회/날짜} | {핵심 아이디어 1줄 요약} |
   ```

## Step 4: Notion 업로드

`notion_mcp_instruction.md`의 파이프라인을 따라 Notion에 반영한다.

1. **메인 페이지 개요 테이블에 새 행 추가**
2. **하위 논문 상세 페이지 생성** (토글 블록 형태)
3. **검증**: 생성된 페이지가 정상적으로 표시되는지 확인

상세 Notion API 호출 방법은 `notion_mcp_instruction.md` 참조.

---

## 디렉토리 구조

```
paper_listup/
├── CLAUDE.md                    # Claude 에이전트 지침서
├── summarize_instruction.md     # 이 파일 (전체 파이프라인)
├── notion_mcp_instruction.md    # Notion 업로드 상세 가이드
├── agent_memory_papers.md       # 전체 논문 개요 (카테고리별 테이블)
├── agent_memory_pdfs/           # 원본 PDF 저장소
│   ├── A-MEM.pdf
│   ├── MAGMA.pdf
│   └── ...
└── summaries/                   # 개별 논문 요약 마크다운
    ├── 01_A-MEM.md
    ├── 02_MAGMA.md
    └── ...
```

# Notion 논문 정리 파이프라인

## Notion 워크스페이스 구조

```
📁 Notion Workspace
└── 🧠 LLM Agent Memory 관련 논문 정리 (메인 페이지)
    ├── [Callout] 개요 설명
    ├── [H1 + Table] 1. Memory Management
    ├── [H1 + Table] 2. Tool Use & MCP
    ├── [H1 + Table] 3. Planning & Task Decomposition
    ├── [H1 + Table] 4. Self-Correction & Test-Time Compute
    ├── [H1 + Table] 5. Agentic RAG & Graph RAG
    ├── [H1 + Table] 6. General
    ├── [Divider]
    ├── [H2] 개별 논문 상세 Summary
    ├── [Paragraph] 설명 텍스트
    └── 📄 하위 페이지들 (논문별 상세, 번호 순 나열)
        ├── 01. A-MEM ~ 13. Memory Survey (기존)
        └── 14. MASS ~ 18. AgentRefine (추가)
```

> **중요**: 카테고리 테이블 영역(H1+Table)과 하위 페이지 나열 영역(child_page)은 Divider로 구분된다.
> 새 블록 추가 시 반드시 올바른 위치에 삽입해야 한다 (아래 파이프라인 참조).

## 각 하위 페이지 구조

```
📄 {번호}. {논문명}
├── [Callout 📄] 저자, arXiv, 학회, 코드 링크
├── [H2] 필수 요소
│   ├── [Toggle H3] Problem    → 내용
│   ├── [Toggle H3] Motivation → 내용
│   ├── [Toggle H3] Method     → 내용
│   ├── [Toggle H3] Key Contribution → 내용
│   ├── [Toggle H3] Experiment → 내용
│   └── [Toggle H3] Limitation → 내용
├── [Divider]
├── [H2] 선택 요소
│   ├── [Toggle H3] Baseline 비교 → 내용
│   └── [Toggle H3] Ablation Study / Taxonomy / Threat Model → 내용
└── [Divider]
```

## Notion API 연동 정보

- **Integration Token**: 환경변수 `NOTION_TOKEN` 또는 `.claude/.mcp.json`에서 참조
- **API Version**: `2022-06-28`
- **메인 페이지 ID**: `32d736a2-7192-815f-a75e-f771df5934c5`
- **API Base URL**: `https://api.notion.com/v1`

## Notion 업로드 파이프라인

### Step 0 (필수): 기존 블록 구조 조회

**반드시 먼저** 메인 페이지의 현재 블록 목록을 조회하여 구조를 파악한다.

```
GET /blocks/{메인페이지ID}/children?page_size=100
```

조회 결과에서 다음을 확인한다:
- 마지막 카테고리 테이블의 block_id → 새 카테고리 삽입 위치 (after)
- Divider의 block_id → 카테고리와 하위 페이지 영역의 경계
- 기존 카테고리 목록 → 새 논문이 기존 카테고리에 속하는지 판단

### Step 1: 메인 페이지 개요 테이블 업데이트

`agent_memory_papers.md`의 카테고리별 테이블 내용을 메인 페이지에 반영한다.

**테이블 컬럼 구조** (5열):
| 논문 | 발표 날짜 | 학회/발표기관 | 1저자 | 핵심 아이디어 |

**경우 A: 기존 카테고리에 논문 추가**
1. 해당 카테고리의 table block_id를 찾는다
2. 해당 테이블을 삭제 후 새 행이 포함된 테이블로 재생성 (Notion API는 기존 테이블에 행 추가를 지원하지 않음)
3. 재생성 시 `after` 파라미터로 해당 카테고리 heading 뒤에 삽입

**경우 B: 새 카테고리 생성**
1. 마지막 카테고리 테이블의 block_id를 확인
2. `PATCH /blocks/{메인페이지ID}/children`에 **`after` 파라미터**를 사용하여 해당 위치 뒤에 삽입
   ```json
   {
     "children": [H1 블록, Table 블록, ...],
     "after": "마지막_카테고리_테이블_block_id"
   }
   ```
3. **절대 단순 append 하지 않는다** — Divider 아래(하위 페이지 영역)에 카테고리가 끼어들게 됨

### Step 2: 하위 논문 상세 페이지 생성

`summaries/{번호}_{이름}.md`의 내용을 Notion 하위 페이지로 생성한다.
하위 페이지는 `POST /pages`로 생성하면 자동으로 하위 페이지 목록 맨 뒤에 추가된다.

1. `POST /pages` 로 새 하위 페이지 생성
   - parent: `{ "page_id": "메인 페이지 ID" }`
   - icon: 📄 (모든 논문 공통)
   - title: `"{번호}. {논문 정식 명칭}"`
2. children 블록 구성:
   - **Callout** (📄): 저자, arXiv, 학회, 코드 URL
   - **Heading 2**: "필수 요소"
   - **Toggle Heading 3** × 6: Problem, Motivation, Method, Key Contribution, Experiment, Limitation
     - 각 토글 안에 paragraph 블록으로 내용 삽입
   - **Divider**
   - **Heading 2**: "선택 요소"
   - **Toggle Heading 3** × N: Baseline 비교, Ablation Study 등 (해당하는 것만)
   - **Divider**

### Step 3: Callout 업데이트

메인 페이지 최상단 Callout의 논문 수/카테고리 수를 현재 상태에 맞게 업데이트한다.

```
PATCH /blocks/{callout_block_id}
```

### Step 4: 검증

- `GET /blocks/{메인페이지ID}/children`로 전체 구조를 다시 조회
- 카테고리 블록들이 Divider 위에, 하위 페이지들이 Divider 아래에 있는지 확인
- 블록 순서: `[Callout] → [H1+Table] × N → [Divider] → [H2] → [Paragraph] → [child_page] × M`

## API 호출 시 주의사항

1. **rich_text 2000자 제한**: 하나의 rich_text 요소는 최대 2000자. 초과 시 여러 요소로 분할
2. **children 100개 제한**: 한 번의 PATCH/POST에 최대 100개 블록. 초과 시 분할 호출
3. **Rate Limit**: 요청 간 0.3~0.5초 간격 유지
4. **인코딩**: JSON 파일은 반드시 UTF-8로 작성. Windows 환경에서 `encoding='utf-8'` 명시 필요
5. **Toggle 블록**: `heading_3`에 `"is_toggleable": true`와 `"children": [...]`을 함께 지정
6. **블록 위치 지정 (after)**: `PATCH /blocks/{parent}/children`에서 `"after": "block_id"`를 사용하면 특정 블록 뒤에 삽입된다. 생략하면 **맨 끝에 append**되므로, 기존 페이지 중간에 삽입할 때는 반드시 `after`를 지정한다.
7. **블록 삭제**: `DELETE /blocks/{block_id}`로 잘못 배치된 블록을 삭제한 뒤 올바른 위치에 재생성한다.
8. **Python 스크립트 출력**: Windows cp949 환경에서 한글/이모지 출력 시 `sys.stdout.buffer.write(line.encode('utf-8'))`을 사용하거나 `PYTHONIOENCODING=utf-8` 환경변수를 설정한다.

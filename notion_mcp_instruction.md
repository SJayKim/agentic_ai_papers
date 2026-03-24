# Notion 논문 정리 파이프라인

## Notion 워크스페이스 구조

```
📁 Notion Workspace
└── 🧠 LLM Agent Memory 관련 논문 정리 (메인 페이지)
    ├── [Callout] 개요 설명
    ├── [H1 + Table] 1. Knowledge Graph & Graph RAG
    ├── [H1 + Table] 2. Meta-Learning & Evolution
    ├── [H1 + Table] 3. Long-term & Multi-Agent
    ├── [H1 + Table] 4. Management, Benchmark & Privacy
    ├── [Divider]
    ├── [H2] 개별 논문 상세 Summary
    └── 📄 하위 페이지들 (논문별 상세)
        ├── 01. A-MEM: Agentic Memory for LLM Agents
        ├── 02. MAGMA: ...
        ├── ...
        └── 13. Memory in the Age of AI Agents: A Survey
```

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

### Step 1: 메인 페이지 개요 테이블 업데이트

`agent_memory_papers.md`의 카테고리별 테이블 내용을 메인 페이지에 반영한다.

1. 메인 페이지의 기존 블록을 조회: `GET /blocks/{메인페이지ID}/children`
2. 해당 카테고리 테이블을 찾아서 새 행(row)을 추가하거나, 테이블을 재생성
3. 새 논문 정보 (논문명, 발표, 핵심 아이디어) 를 행으로 추가

### Step 2: 하위 논문 상세 페이지 생성

`summaries/{번호}_{이름}.md`의 내용을 Notion 하위 페이지로 생성한다.

1. `POST /pages` 로 새 하위 페이지 생성
   - parent: `{ "page_id": "메인 페이지 ID" }`
   - icon: 번호에 맞는 이모지 (1️⃣~🔟, 이후 📊🔒📖 등)
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

### Step 3: 검증

- 생성된 페이지 URL을 `GET /pages/{page_id}` 로 확인
- 블록 수와 내용이 원본 마크다운과 일치하는지 검증

## API 호출 시 주의사항

1. **rich_text 2000자 제한**: 하나의 rich_text 요소는 최대 2000자. 초과 시 여러 요소로 분할
2. **children 100개 제한**: 한 번의 PATCH/POST에 최대 100개 블록. 초과 시 분할 호출
3. **Rate Limit**: 요청 간 0.3~0.5초 간격 유지
4. **인코딩**: JSON 파일은 반드시 UTF-8로 작성. Windows 환경에서 `encoding='utf-8'` 명시 필요
5. **Toggle 블록**: `heading_3`에 `"is_toggleable": true`와 `"children": [...]`을 함께 지정

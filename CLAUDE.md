# Paper Listup 프로젝트

## 프로젝트 개요

AI Agent Memory 관련 논문들을 체계적으로 정리하고, 로컬 마크다운과 Notion에 동기화하는 프로젝트.

## 핵심 파일 안내

| 파일 | 역할 |
|------|------|
| `summarize_instruction.md` | 논문 정리 전체 파이프라인 (PDF 확보 → 요약 작성 → 개요 업데이트 → Notion 업로드) |
| `notion_mcp_instruction.md` | Notion API 연동 상세 가이드 (페이지 구조, API 호출 방법, 주의사항) |
| `agent_memory_papers.md` | 전체 논문 개요 (카테고리별 테이블) |
| `summaries/` | 개별 논문 요약 마크다운 |
| `agent_memory_pdfs/` | 원본 PDF 저장소 |

## 태스크별 행동 지침

| 사용자 요청 | 실행할 Skill | 설명 |
|-------------|-------------|------|
| "논문 정리해줘" / "이 논문 추가해줘" | `/paper {제목}` | PDF 확보 → 요약 → 개요 업데이트 → Notion 업로드 |
| "요약만 해줘" (Notion 없이) | `/paper-summary {제목}` | PDF 확보 → 요약 → 개요 업데이트 |
| "Notion에 올려줘" / "Notion 업데이트해줘" | `/notion-upload {대상}` | 로컬 요약을 Notion에 반영 |

각 Skill의 상세 파이프라인은 `.claude/skills/` 디렉토리에 정의되어 있다.
Notion 업로드는 반드시 메인 대화에서 Python `requests`로 직접 수행할 것 (subagent 사용 금지).

## Notion 연동 정보

- **메인 페이지 ID**: `32d736a2-7192-815f-a75e-f771df5934c5`
- **토큰**: `.claude/.mcp.json`의 `NOTION_TOKEN` 참조
- **API Version**: `2022-06-28`
- **페이지 구조**: 토글 Heading 3 블록 사용 (테이블 대신, 전체 너비 활용)
- **블록 순서**: `[Callout] → [H1+Table] × N → [Divider] → [H2] → [Paragraph] → [child_page] × M`

## 기술적 주의사항

- **Python**: 이 환경에서는 `python` 명령 사용 (`python3` 아님)
- **인코딩**: 파일 읽기/쓰기 시 항상 `encoding='utf-8'` 지정
- **Notion API rich_text**: 하나의 요소당 최대 2000자. 초과 시 분할
- **Notion API children**: 한 요청당 최대 100개 블록. 초과 시 분할 호출
- **Rate Limit**: API 호출 간 0.3~0.5초 간격 유지
- **블록 위치 지정**: `PATCH /blocks/{parent}/children`에서 `"after": "block_id"` 필수 사용. 생략 시 맨 끝 append되어 구조 깨짐

## 환경 제약 및 워크플로우 원칙 (Lessons Learned)

### PDF 읽기
- **Read 도구의 PDF 지원이 이 Windows 환경에서 동작하지 않음** (`pdftoppm` 미설치)
- **대안**: `PyPDF2` 라이브러리를 사용하여 Bash에서 Python으로 텍스트 추출
  ```python
  python -c "
  import PyPDF2, sys
  sys.stdout.reconfigure(encoding='utf-8')
  reader = PyPDF2.PdfReader(r'path/to/file.pdf')
  for i in range(len(reader.pages)):
      print(reader.pages[i].extract_text())
  "
  ```
- PyPDF2는 이미 설치되어 있음 (`pip install PyPDF2` 불필요)

### 백그라운드 에이전트 제약
- **백그라운드 에이전트는 파일 쓰기(Write/Edit) 권한을 얻지 못함** — 사용자가 프롬프트를 승인할 수 없기 때문
- **따라서**: 파일 쓰기가 필요한 작업은 반드시 **메인 대화에서 직접** 수행해야 함
- 에이전트는 **읽기 전용 조사(research)** 용도로만 사용:
  - PDF 내용 분석, 웹 검색, 코드베이스 탐색 등
- **대량 파일 작성이 필요한 경우**: 메인 대화에서 순차적으로 처리. 병렬화 시도하지 말 것

### Notion API 호출
- **MCP 서버 대신 Python `requests`로 직접 호출**이 더 안정적
- 토큰 위치: `.claude/.mcp.json` → `mcpServers.notion.env.NOTION_TOKEN`
- 대량 페이지 생성 시 Python 스크립트를 Bash로 실행 (rate limit 준수)

### 대량 작업 시 워크플로우
1. **PDF 텍스트 추출**: Bash + PyPDF2로 모든 PDF를 한번에 텍스트 파일로 변환
2. **요약 작성**: 메인 대화에서 텍스트 파일을 읽고 Write 도구로 순차 작성
3. **Notion 업로드**: Python 스크립트로 일괄 처리 (에이전트 사용 금지)
4. 에이전트를 파일 쓰기 목적으로 실행하지 말 것 — 반드시 실패함

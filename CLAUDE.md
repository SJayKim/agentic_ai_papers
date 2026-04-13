# Paper Listup 프로젝트

## 프로젝트 개요

LLM Agentic AI 관련 논문들을 체계적으로 정리하고, 로컬 마크다운과 Notion에 동기화하는 프로젝트.

## 카테고리 체계

| # | 카테고리 | 범위 |
|---|---------|------|
| 1 | **Memory Management** | 메모리 저장/검색/구조화/진화 |
| 2 | **Tool Use & MCP** | 외부 도구 호출, function calling, MCP |
| 3 | **Planning & Task Decomposition** | 작업 분할, 계획 수립, 오케스트레이션 |
| 4 | **Self-Correction & Test-Time Compute** | 자가 교정, 추론 시간 연산, RL 기반 학습 |
| 5 | **Agentic RAG & Graph RAG** | 지식 그래프, 그래프 RAG, 능동적 검색 |
| 6 | **General** | 위 6개에 해당하지 않는 에이전트 아키텍처/서베이/기타 |
| 7 | **Harness Engineering** | 에이전트 하네스/스캐폴딩 설계 및 최적화 |

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

### 서브에이전트 활용 원칙
- **백그라운드 에이전트는 파일 쓰기(Write/Edit) 권한을 얻지 못함** — 사용자가 프롬프트를 승인할 수 없기 때문
- **그러나 서브에이전트는 Read로 파일을 읽고, 분석 결과를 텍스트로 반환할 수 있음**
- **논문 요약 작성 시 권장 패턴**:
  1. 서브에이전트: `_text.txt` 파일을 Read로 읽고 → 요약 마크다운을 텍스트로 반환 (Write 불필요)
  2. 메인 대화: 반환된 텍스트를 Write로 파일 저장 → 품질 검증 → Notion 업로드
- **이 패턴의 장점**: 각 논문 분석이 독립된 컨텍스트에서 수행되어, 대량 처리 시에도 후반부 품질이 저하되지 않음
- 에이전트를 파일 쓰기 목적으로 실행하지 말 것 — 반드시 실패함

### Notion API 호출
- **MCP 서버 대신 Python `requests`로 직접 호출**이 더 안정적
- 토큰 위치: `.claude/.mcp.json` → `mcpServers.notion.env.NOTION_TOKEN`
- 대량 페이지 생성 시 Python 스크립트를 Bash로 실행 (rate limit 준수)

### 대량 작업 시 워크플로우
1. **배치 분할**: **3편 단위**로 나누어 처리. 한 배치 완료 후 사용자에게 진행 보고
2. **PDF 텍스트 추출**: Bash + PyPDF2로 배치 내 PDF를 한번에 `_text.txt`로 변환
3. **요약 작성 (서브에이전트 활용)**: 각 논문마다 서브에이전트가 `_text.txt`를 읽고 요약 반환 → 메인에서 Write
4. **품질 평가 루프 (필수)**: **논문 1편당 1개 평가 에이전트** 실행 (배치 내 병렬)
   - 평가 에이전트는 요약 작성 컨텍스트와 **완전히 분리된 새 세션**에서 실행
   - **1 에이전트 = 1 논문** — 여러 논문을 한 에이전트에 넣지 않는다
   - 평가 기준: [A] 분량(80줄↑, Problem/Motivation/Limitation 각 5줄↑, Method 15줄↑, Experiment 10줄↑, 수치 5개↑) + [B] 충실도(각 섹션별 구체성)
   - FAIL 논문 → 1편당 1개 보강 에이전트가 PDF 재독 후 보강 텍스트 반환 → 메인에서 Write
   - 재평가 최대 2회, 전수 PASS 시 다음 단계 진행
5. **메인 컨텍스트 관리**: 서브에이전트 반환값을 Write로 저장한 직후 다음 논문으로 진행. 이전 논문 상세 내용을 메인에서 재참조하지 않는다
6. **Notion 업로드**: 로컬 마크다운 파일을 Read로 읽어서 내용 반영. 별도 재작성/하드코딩 금지
7. Notion 업로드는 Python `requests` 스크립트로 메인 대화에서 직접 수행 (에이전트 사용 금지)

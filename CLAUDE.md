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

### "논문 정리해줘" / "이 논문 추가해줘"

`summarize_instruction.md`의 파이프라인을 순서대로 따른다:

1. **PDF 확보**: `agent_memory_pdfs/`에 저장. 파일명은 `{논문약칭}.pdf`
2. **요약 작성**: PDF를 읽고 `summaries/{번호}_{약칭}.md`에 템플릿에 맞춰 작성
   - 번호는 기존 마지막 번호 + 1
   - 필수 요소 6개 (Problem, Motivation, Method, Key Contribution, Experiment, Limitation)
   - 선택 요소 (Baseline 비교, Ablation Study, Taxonomy, Threat Model 중 해당하는 것)
3. **개요 업데이트**: `agent_memory_papers.md`의 적절한 카테고리 테이블에 새 행 추가
4. **Notion 업로드**: `notion_mcp_instruction.md`에 따라 Notion에 반영
   - 메인 페이지 테이블에 행 추가
   - 하위 상세 페이지 생성 (토글 블록 형태)

### "Notion에 올려줘" / "Notion 업데이트해줘"

`notion_mcp_instruction.md`를 참고하여 실행한다.

- Notion API를 curl로 직접 호출 (MCP 서버 불안정 시)
- JSON payload는 Python 스크립트로 생성하면 효율적
- `python` 사용 (`python3`은 이 환경에서 동작하지 않음)
- JSON 파일 읽기 시 `encoding='utf-8'` 필수 (Windows cp949 이슈)

### "요약만 해줘" (Notion 없이)

Step 1~3만 수행한다. (PDF 확보 → 요약 작성 → 개요 업데이트)

## Notion 연동 정보

- **메인 페이지 ID**: `32d736a2-7192-815f-a75e-f771df5934c5`
- **토큰**: `.claude/.mcp.json`의 `NOTION_TOKEN` 참조
- **API Version**: `2022-06-28`
- **페이지 구조**: 토글 Heading 3 블록 사용 (테이블 대신, 전체 너비 활용)

## 기술적 주의사항

- **Python**: 이 환경에서는 `python` 명령 사용 (`python3` 아님)
- **인코딩**: 파일 읽기/쓰기 시 항상 `encoding='utf-8'` 지정
- **Notion API rich_text**: 하나의 요소당 최대 2000자. 초과 시 분할
- **Notion API children**: 한 요청당 최대 100개 블록. 초과 시 분할 호출
- **Rate Limit**: API 호출 간 0.3~0.5초 간격 유지

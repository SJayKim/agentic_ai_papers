# AI Agent Memory 논문 정리

AI Agent Memory 관련 논문을 체계적으로 정리하고 Notion에 동기화하는 프로젝트.

## 구조

```
agent_memory_papers.md          # 전체 논문 개요 (카테고리별 테이블)
summaries/                      # 개별 논문 요약 (26편)
summaries/agent_memory_pdfs/    # 원본 PDF
summarize_instruction.md        # 요약 파이프라인 정의
notion_mcp_instruction.md       # Notion API 연동 가이드
```

## 사용법 (Claude Code)

| 커맨드 | 설명 |
|--------|------|
| `/paper {논문}` | PDF 확보 → 요약 → 개요 업데이트 → Notion 업로드 |
| `/paper-summary {논문}` | 위와 동일하되 Notion 업로드 제외 |
| `/notion-upload {대상}` | 로컬 요약을 Notion에 반영 |

논문 제목, 약칭, arXiv ID 모두 가능하며 쉼표로 여러 편 동시 처리 가능.

```
/paper MemoryBank
/paper MemoryBank, RAISE, CoALA
/paper 2401.12345
```

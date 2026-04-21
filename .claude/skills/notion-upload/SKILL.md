---
name: notion-upload
description: 로컬에 이미 작성된 요약을 Notion에 업로드. 특정 논문 지정 또는 미반영 논문 전체 업로드
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep, Edit
---

# Notion 업로드 파이프라인

대상: **$ARGUMENTS**

@notion_mcp_instruction.md 를 참고하여 Notion에 반영하세요.

---

## 실행 순서

1. **대상 파악**: `$ARGUMENTS`가 특정 논문이면 해당 논문만, 비어있으면 사용자에게 확인
2. **기존 블록 구조 조회**: `GET /blocks/{메인페이지ID}/children`
3. **메인 페이지 카테고리 테이블 업데이트**: 기존 테이블 삭제 후 재생성 (after 파라미터 사용)
4. **하위 논문 상세 페이지 생성**: `summaries/{번호}_{이름}.md` 내용을 토글 블록 형태로
5. **Callout 업데이트**: 논문 수/카테고리 수 반영
6. **검증**: 블록 순서 `[카테고리] → [Divider] → [하위 페이지]` 확인

## 주의사항

- `python` 사용 (`python3` 아님)
- `encoding='utf-8'` 필수
- rich_text 2000자, children 100개 제한
- Rate Limit: 0.3~0.5초 간격
- `after` 파라미터 필수 — 단순 append 금지

## ⚠ 실행 방식 제약

- **MCP 서버나 subagent를 사용하지 말 것** — 권한 문제로 실패함
- **반드시 Bash에서 Python `requests`로 Notion API를 직접 호출**할 것
- 토큰: `.claude/.mcp.json` → `mcpServers.notion.env.NOTION_TOKEN`
- 필수 헤더: `Authorization: Bearer {TOKEN}`, `Notion-Version: 2022-06-28`
- 대량 처리 시 하나의 Python 스크립트에서 루프로 처리

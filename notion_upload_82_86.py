"""Upload papers 82-86 (DSPy, MIPROv2, TextGrad, ProTeGi, GEPA) to Notion.

1. Replace Harness Engineering table (10 existing + 5 new = 15 rows)
2. Create 5 child sub-pages with Callout + 6 Toggle H3 sections
3. Update main Callout: "81편" -> "86편"
"""
import json, re, sys, time, urllib3, requests, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding="utf-8")

TOKEN = json.load(open(r"C:/Users/cyon1/.claude/.mcp.json", encoding="utf-8"))["mcpServers"]["notion"]["env"]["NOTION_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
BASE = "https://api.notion.com/v1"
PAGE_ID = "32d736a2-7192-815f-a75e-f771df5934c5"
HARNESS_H1 = "341736a2-7192-81e8-b478-f3f5c7b77aba"
HARNESS_TABLE = "341736a2-7192-81b3-a574-f362f49b17e4"
CALLOUT_ID = "32d736a2-7192-81b4-a019-cd37cee3a3aa"
SLEEP = 0.4


def api(method, url, **kwargs):
    kwargs["verify"] = False
    for _ in range(3):
        r = requests.request(method, url, headers=H, **kwargs)
        if r.status_code == 429:
            time.sleep(2.0)
            continue
        if 500 <= r.status_code < 600:
            time.sleep(1.0)
            continue
        r.raise_for_status()
        time.sleep(SLEEP)
        return r.json()
    raise RuntimeError(f"Failed {method} {url}: {r.status_code} {r.text[:200]}")


def split_text(t, limit=1900):
    if len(t) <= limit:
        return [t]
    out = []
    while t:
        if len(t) <= limit:
            out.append(t); break
        cut = t.rfind(". ", 0, limit)
        if cut < limit // 2:
            cut = t.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        out.append(t[:cut+1].strip())
        t = t[cut+1:].strip()
    return out


def rich_text(content, bold=False):
    return [{"type": "text", "text": {"content": c}, "annotations": {"bold": bold}} for c in split_text(content)]


def paragraph(t):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(t)}}


def toggle_h3(title, paras):
    children = [paragraph(p) for p in paras if p.strip()][:100]
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": rich_text(title, bold=True), "is_toggleable": True, "children": children}}


def heading_2(t):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich_text(t, bold=True)}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def callout(t):
    return {"object": "block", "type": "callout",
            "callout": {"icon": {"type": "emoji", "emoji": "📄"}, "rich_text": rich_text(t), "color": "gray_background"}}


def table_row(cells):
    return {"object": "block", "type": "table_row",
            "table_row": {"cells": [rich_text(c) for c in cells]}}


def table_block(header, rows):
    children = [table_row(header)] + [table_row(r) for r in rows]
    return {"object": "block", "type": "table",
            "table": {"table_width": len(header), "has_column_header": True, "has_row_header": False, "children": children}}


# ============ Parse summaries ============

def parse_summary(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = m.group(1).strip() if m else path
    info_parts = re.findall(r"^>\s*(.+)$", content, re.MULTILINE)
    info = " | ".join(info_parts) if info_parts else ""
    SECTIONS = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]
    sections = {}
    for sec in SECTIONS:
        pat = re.compile(rf"(?mi)^##\s*{re.escape(sec)}[^\n]*$(.*?)(?=^##\s|\Z)", re.DOTALL)
        m = pat.search(content)
        if m:
            body = re.sub(r"^---+$", "", m.group(1).strip(), flags=re.MULTILINE)
            paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            sections[sec] = paras
        else:
            sections[sec] = []
    return title, info, sections


# ============ Harness Engineering table replacement ============

HARNESS_HEADER = ["논문", "발표 날짜", "학회/발표기관", "1저자", "핵심 아이디어"]

HARNESS_ROWS_EXISTING = [
    ["Externalization Survey", "2026.04", "arXiv / SJTU", "Chenyu Zhou", "메모리/스킬/프로토콜/하네스를 인지적 외재화 관점에서 통합 정리한 최초의 서베이"],
    ["NLAH", "2026.03", "Tsinghua / HIT", "Linyue Pan", "하네스 제어 로직을 자연어로 표현한 이식 가능 실행 아티팩트 + IHR 런타임 제안"],
    ["AutoHarness", "2026.03", "Google DeepMind", "Xinghua Lou", "Thompson sampling 트리 탐색으로 LLM이 자기 자신을 위한 코드 하네스를 자동 합성"],
    ["TerminalCodingAgent", "2026.03", "OpenDev", "Nghi D. Q. Bui", "터미널 코딩 에이전트의 스캐폴딩/하네스/컨텍스트 엔지니어링 실전 기술 보고서"],
    ["InsideScaffold", "2026.04", "Huawei Canada", "Benjamin Rombaut", "13개 코딩 에이전트 소스코드 분석 → 3계층 12차원 분류 체계 + 5개 루프 프리미티브"],
    ["MetaHarness", "2026.03", "Stanford", "Yoonho Lee", "코딩 에이전트가 파일시스템 기반 실행 이력을 탐색하여 하네스를 자동 최적화"],
    ["CompilerHarness", "2026.03", "SUSTech / ETH Zurich", "Yingwei Zheng", "컴파일러 특화 에이전트 하네스(llvm-autofix) + 334개 LLVM 버그 벤치마크"],
    ["LLM Readiness Harness", "2026.03", "Lumytics", "Alexandre Maiorano", "평가·관측성·CI 게이트를 통합한 LLM/RAG 배포 준비도 하네스"],
    ["PromptwareEng", "2025.03", "Tsinghua / NTU / PKU", "Zhenpeng Chen", "프롬프트 개발에 SE 원칙을 적용하는 프롬프트웨어 엔지니어링 프레임워크 + 27개 연구 기회"],
    ["ConfuciusCodeAgent", "2025.12", "Meta / Harvard", "Sherman Wong", "AX/UX/DX 3축 설계 + 계층적 메모리 + Meta-agent로 대규모 코드베이스 스캐폴딩"],
]

HARNESS_ROWS_NEW = [
    ["DSPy", "2023.10", "ICLR 2024 / Stanford", "Omar Khattab", "Signature·Module·Teleprompter 추상화 + BootstrapFewShot으로 LLM 파이프라인의 prompt를 자동 컴파일"],
    ["MIPROv2", "2024.06", "EMNLP 2024 / Stanford", "Krista Opsahl-Ong", "Bootstrap demo + Grounded instruction proposal + Bayesian(TPE) joint 최적화, 7개 task에서 최대 +13%"],
    ["TextGrad", "2024.06", "Nature 2025 / Stanford", "Mert Yuksekgonul", "LLM 비판을 텍스트 gradient로 backprop, PyTorch-style API로 코드·프롬프트·분자·치료계획 통합 최적화"],
    ["ProTeGi", "2023.05", "EMNLP 2023 / Microsoft", "Reid Pryzant", "실패 사례에 대한 LLM 비판을 textual gradient로 사용, beam search + bandit selection으로 prompt 최적화"],
    ["GEPA", "2025.07", "arXiv / Stanford-UCB", "Lakshya A Agrawal", "Reflective mutation + Pareto-based candidate selection + System-aware Merge, GRPO 대비 35× rollout 효율로 평균 +6%"],
]


def replace_harness_table():
    """Delete existing Harness Engineering table and insert new one with 15 rows."""
    print("1) Harness Engineering 테이블 교체 중...")
    print(f"  - 기존 테이블 삭제: {HARNESS_TABLE[:8]}...")
    api("DELETE", f"{BASE}/blocks/{HARNESS_TABLE}")

    new_table = table_block(HARNESS_HEADER, HARNESS_ROWS_EXISTING + HARNESS_ROWS_NEW)
    print(f"  - 새 테이블 삽입 (after H1, {len(HARNESS_ROWS_EXISTING)+len(HARNESS_ROWS_NEW)}행)")
    api("PATCH", f"{BASE}/blocks/{PAGE_ID}/children",
        json={"children": [new_table], "after": HARNESS_H1})


# ============ Child page creation ============

PAPERS = [
    (82, "summaries/82_DSPy.md"),
    (83, "summaries/83_MIPROv2.md"),
    (84, "summaries/84_TextGrad.md"),
    (85, "summaries/85_ProTeGi.md"),
    (86, "summaries/86_GEPA.md"),
]
SECTIONS = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]


def create_subpage(num, path):
    title, info, sections = parse_summary(path)
    print(f"2.{num}) '{title[:60]}' 페이지 생성 중...")

    children = []
    if info:
        children.append(callout(info))
    children.append(heading_2("필수 요소"))
    for sec in SECTIONS:
        paras = sections.get(sec) or ["(내용 없음)"]
        children.append(toggle_h3(sec, paras))
    children.append(divider())

    body = {
        "parent": {"page_id": PAGE_ID},
        "icon": {"type": "emoji", "emoji": "📄"},
        "properties": {"title": [{"type": "text", "text": {"content": title}}]},
        "children": children[:100],
    }
    page = api("POST", f"{BASE}/pages", json=body)
    # If toggles have children > 100 limit individually, helper above caps at 100; safe.
    print(f"  -> page_id={page['id'][:8]}...")
    return page["id"]


def update_callout():
    print("3) 메인 Callout 업데이트: 81편 -> 86편")
    new_text = "LLM Agentic AI 관련 최신 논문 86편을 7개 카테고리로 분류하여 정리한 문서입니다. 각 논문의 상세 요약은 하위 페이지에서 확인할 수 있습니다."
    api("PATCH", f"{BASE}/blocks/{CALLOUT_ID}",
        json={"callout": {"rich_text": rich_text(new_text), "icon": {"type": "emoji", "emoji": "📚"}, "color": "gray_background"}})


def main():
    replace_harness_table()
    print()
    for num, path in PAPERS:
        create_subpage(num, path)
    print()
    update_callout()
    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()

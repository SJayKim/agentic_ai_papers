"""Upload papers 87-97 (11 new papers) to Notion.

1. Discover the 6 affected category tables at runtime (match by H1 text).
2. Append new table_row(s) to each category table (Memory+1, Tool+2, Planning+2, RAG+4, General+1, Harness+1).
3. Create 11 child sub-pages (Callout + H2 + 6 Toggle H3 + Divider), parsed from local summary markdown.
4. Update main Callout: "86편" -> "97편".

Reuses the patterns from notion_upload_82_86.py / notion_resync.py.
Run once: python notion_upload_87_97.py
"""
import json, re, sys, time, urllib3, requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding="utf-8")

TOKEN = json.load(open(r"C:/Users/cyon1/.claude/.mcp.json", encoding="utf-8"))["mcpServers"]["notion"]["env"]["NOTION_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
BASE = "https://api.notion.com/v1"
PAGE_ID = "32d736a2-7192-815f-a75e-f771df5934c5"
CALLOUT_ID = "32d736a2-7192-81b4-a019-cd37cee3a3aa"
SLEEP = 0.4


def api(method, url, **kwargs):
    kwargs["verify"] = False
    for _ in range(3):
        r = requests.request(method, url, headers=H, **kwargs)
        if r.status_code == 429:
            time.sleep(2.0); continue
        if 500 <= r.status_code < 600:
            time.sleep(1.0); continue
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
        out.append(t[:cut + 1].strip())
        t = t[cut + 1:].strip()
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
    return {"object": "block", "type": "table_row", "table_row": {"cells": [rich_text(c) for c in cells]}}


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


SECTIONS = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]


def text_of(b):
    t = b["type"]
    return "".join(x.get("plain_text", "") for x in b.get(t, {}).get("rich_text", []))


def get_children_all(block_id):
    blocks, cur = [], None
    while True:
        url = f"{BASE}/blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else "")
        d = api("GET", url)
        blocks.extend(d["results"])
        if not d.get("has_more"):
            break
        cur = d["next_cursor"]
    return blocks


# New rows per category (matched by keyword in the H1 heading text). 5 columns each.
CATEGORY_ROWS = {
    "Memory Management": [
        ["REMem", "2026.02", "ICLR 2026 / Ohio State-Intuit", "Yiheng Shu",
         "시간 파싱 gist + n-ary fact 하이브리드 메모리 그래프와 에이전틱 시간여행 검색으로 episodic 회상·추론, HippoRAG2·Mem0 능가"],
    ],
    "Tool Use": [
        ["MCP-Bench", "2025.08", "arXiv / Accenture", "Zhenting Wang",
         "28개 라이브 MCP 서버·250개 도구로 의존성 사슬·cross-server 오케스트레이션을 fuzzy 지시로 평가(20개 LLM 중 gpt-5 0.749 최고)"],
        ["ComplexMCP", "2026.05", "arXiv / Alibaba", "Yuanyang Li",
         "315개 stateful·상호의존 도구 샌드박스 + seed 기반 결정론적 평가로 상용 SW 자동화 'last mile' 측정(최상위 <60% vs 인간 93.6%)"],
    ],
    "Planning": [
        ["EvoMAS", "2026.02", "arXiv / Amazon AWS", "Yuntong Hu",
         "MAS 생성을 구조적 config 진화로 정식화, 실행 트레이스 기반 변이·교차로 코드 없이 견고한 멀티에이전트 설계(실행성공률 ~99%)"],
        ["O-Researcher", "2026.01", "arXiv / OPPO", "Yi Yao",
         "병렬 멀티에이전트 distillation + GRPO RLAIF로 오픈 deep-research 모델 학습, RACE 48.48로 오픈웨이트 SOTA"],
    ],
    "Agentic RAG": [
        ["Graph-R1", "2025.07", "ICML 2026 / BUPT-NTU", "Haoran Luo",
         "지식 하이퍼그래프 + 멀티턴 검색을 end-to-end GRPO로 최적화하는 에이전틱 GraphRAG(7B 평균 F1 57.82)"],
        ["EvoGraph-R1", "2026.06", "CVPR 2026 / NPU-Shanghai AI Lab", "Jiashi Lin",
         "멀티모달 지식 하이퍼그래프를 MDP 환경으로 모델링, 검색·추론·지식진화(GRAPHEDIT)를 단일 RL 루프로 통합"],
        ["AgentGL", "2026.04", "ACL 2026 Main / NYU Shanghai", "Yuanfu Sun",
         "graph-native 도구를 가진 RL 에이전트로 그래프 학습(노드분류/링크예측) 확장(노드분류 최대 +17.5%, 링크예측 +28.4%)"],
        ["TESSERA", "2026.05", "IJCAI-ECAI 2026 / Maastricht", "Rishabh Jakhar",
         "LLM-guided MCTS로 KG 위에서 약물-질병 기전 설명을 합성하는 neuro-symbolic 프레임워크(listwise prior + 비교적 평가)"],
    ],
    "General": [
        ["Agent Reliability", "2026.02", "ICML 2026 / Princeton", "Stephan Rabanser",
         "신뢰성을 4차원(일관성/강건성/예측가능성/안전성) 12지표로 정식화, 24개월 역량 향상(r=0.92)이 신뢰성으론 거의 이어지지 않음 실증"],
    ],
    "Harness": [
        ["Less-Context", "2026.06", "arXiv / Microsoft", "Abhilasha Lodha",
         "frozen 에이전트 컨텍스트를 recent-5 도구쌍+요약으로 가지치기, GPT-5 완료율 71%→91.6%를 토큰 62.7%↓로 달성"],
    ],
}

PAPERS = [
    (87, "summaries/87_REMem.md"),
    (88, "summaries/88_MCP-Bench.md"),
    (89, "summaries/89_ComplexMCP.md"),
    (90, "summaries/90_EvoMAS.md"),
    (91, "summaries/91_O-Researcher.md"),
    (92, "summaries/92_Graph-R1.md"),
    (93, "summaries/93_EvoGraph-R1.md"),
    (94, "summaries/94_AgentGL.md"),
    (95, "summaries/95_TESSERA.md"),
    (96, "summaries/96_Agent-Reliability.md"),
    (97, "summaries/97_Less-Context.md"),
]


def discover_tables():
    """Return {keyword: table_block_id} by pairing each H1 with the next table block."""
    blocks = get_children_all(PAGE_ID)
    found = {}
    last_head = None
    for b in blocks:
        if b["type"] == "heading_1":
            last_head = text_of(b)
        elif b["type"] == "table" and last_head:
            for kw in CATEGORY_ROWS:
                if kw in last_head:
                    found[kw] = b["id"]
            last_head = None
    return found


def append_rows():
    print("1) 카테고리 테이블 행 추가 (런타임 테이블 탐색)...")
    tables = discover_tables()
    for kw, rows in CATEGORY_ROWS.items():
        tid = tables.get(kw)
        if not tid:
            print(f"  ! '{kw}' 테이블을 찾지 못함 — 건너뜀")
            continue
        children = [table_row(r) for r in rows]
        api("PATCH", f"{BASE}/blocks/{tid}/children", json={"children": children})
        print(f"  - {kw}: {len(rows)}행 추가 (table {tid[:8]})")


def create_subpage(num, path):
    title, info, sections = parse_summary(path)
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
    print(f"  - {num}: '{title[:55]}' -> {page['id'][:8]}")
    return page["id"]


def update_callout():
    print("3) 메인 Callout 업데이트: 86편 -> 97편")
    new_text = "LLM Agentic AI 관련 최신 논문 97편을 7개 카테고리로 분류하여 정리한 문서입니다. 각 논문의 상세 요약은 하위 페이지에서 확인할 수 있습니다."
    api("PATCH", f"{BASE}/blocks/{CALLOUT_ID}",
        json={"callout": {"rich_text": rich_text(new_text), "icon": {"type": "emoji", "emoji": "📚"}, "color": "gray_background"}})


def main():
    append_rows()
    print("\n2) 하위 페이지 11개 생성...")
    for num, path in PAPERS:
        create_subpage(num, path)
    print()
    update_callout()
    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()

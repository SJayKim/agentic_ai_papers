"""Resync all re-summarized papers (01-71) to Notion sub-pages.

For each paper:
1. Find existing sub-page ID by title prefix (e.g., "01.")
2. Delete all existing children blocks
3. Parse summary markdown into 6 sections
4. Build Notion block structure (Callout + H2 + 6 Toggle H3 + Divider)
5. POST new blocks via PATCH /blocks/{page_id}/children

Rate limits: 0.4s between API calls.
rich_text max 2000 chars → auto-split.
children max 100 → batched.
"""
import json
import re
import sys
import time
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\cyon1\.claude\.mcp.json", encoding="utf-8") as f:
    TOKEN = json.load(f)["mcpServers"]["notion"]["env"]["NOTION_TOKEN"]
PAGE_ID = "32d736a2-7192-815f-a75e-f771df5934c5"
H = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
BASE = "https://api.notion.com/v1"
SLEEP = 0.4


def api(method, url, **kwargs):
    kwargs["verify"] = False
    for attempt in range(3):
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


def split_text(text, limit=1900):
    """Split text into chunks each <= limit chars (Notion rich_text 2000 max, leave margin)."""
    if len(text) <= limit:
        return [text]
    out = []
    while text:
        if len(text) <= limit:
            out.append(text)
            break
        # Try to break on sentence end
        cut = text.rfind(". ", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        out.append(text[:cut + 1].strip())
        text = text[cut + 1:].strip()
    return out


def rich_text(content, bold=False):
    """Return a list of rich_text objects handling 2000-char limit."""
    chunks = split_text(content)
    return [
        {
            "type": "text",
            "text": {"content": c},
            "annotations": {"bold": bold},
        }
        for c in chunks
    ]


def paragraph(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(text)}}


def toggle_h3(title, paragraphs):
    """Build a toggleable heading_3 block with paragraph children."""
    children = [paragraph(p) for p in paragraphs if p.strip()]
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": rich_text(title, bold=True),
            "is_toggleable": True,
            "children": children[:100],  # Notion limit
        },
    }


def build_callout(info_line):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "📄"},
            "rich_text": rich_text(info_line),
            "color": "gray_background",
        },
    }


def heading_2(text):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": rich_text(text, bold=True)},
    }


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def parse_summary(path):
    """Parse summary markdown into:
    - title (str, from # line)
    - info (str, from > lines joined)
    - sections: dict {name: [paragraph, ...]}
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Title
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = m.group(1).strip() if m else path

    # Info block (consecutive > lines after title)
    info_parts = re.findall(r"^>\s*(.+)$", content, re.MULTILINE)
    info = " | ".join(info_parts) if info_parts else ""

    # Sections: ## X ... (until next ## or EOF)
    SECTIONS = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]
    sections = {}
    for sec in SECTIONS:
        pat = re.compile(
            rf"(?mi)^##\s*{re.escape(sec)}\s*$(.*?)(?=^##\s|\Z)",
            re.DOTALL,
        )
        m = pat.search(content)
        if m:
            body = m.group(1).strip()
            # Remove horizontal rules and empty lines
            body = re.sub(r"^---+$", "", body, flags=re.MULTILINE)
            # Paragraphs: split by blank lines
            paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            sections[sec] = paras
        else:
            sections[sec] = []

    return title, info, sections


def get_children_all(block_id):
    blocks = []
    cursor = None
    while True:
        url = f"{BASE}/blocks/{block_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        data = api("GET", url)
        blocks.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return blocks


def delete_block(block_id):
    api("DELETE", f"{BASE}/blocks/{block_id}")


def append_children(page_id, children):
    """POST children, batched in chunks of 80 (safety margin)."""
    for i in range(0, len(children), 80):
        batch = children[i : i + 80]
        api("PATCH", f"{BASE}/blocks/{page_id}/children", json={"children": batch})


def resync_page(page_id, summary_path):
    title, info, sections = parse_summary(summary_path)

    # Step 1: delete all existing children blocks
    existing = get_children_all(page_id)
    for b in existing:
        try:
            delete_block(b["id"])
        except Exception as e:
            print(f"    ! delete error {b['id'][:8]}: {str(e)[:100]}")

    # Step 2: build new blocks
    SECTIONS = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]
    new_blocks = []
    if info:
        new_blocks.append(build_callout(info))
    new_blocks.append(heading_2("필수 요소"))
    for sec in SECTIONS:
        paras = sections.get(sec, [])
        if not paras:
            paras = [f"(내용 없음)"]
        new_blocks.append(toggle_h3(sec, paras))
    new_blocks.append(divider())

    # Step 3: append
    append_children(page_id, new_blocks)


def main():
    import os
    # Query main page children
    print("메인 페이지 블록 조회 중...")
    blocks = get_children_all(PAGE_ID)
    child_pages = {b["id"]: b["child_page"]["title"] for b in blocks if b["type"] == "child_page"}
    print(f"  하위 페이지 {len(child_pages)}개 발견")

    # Map "NN." prefix to page id
    page_by_num = {}
    for pid, title in child_pages.items():
        m = re.match(r"^(\d+)\.\s", title)
        if m:
            num = int(m.group(1))
            page_by_num[num] = (pid, title)

    # Get summary file paths
    summ_dir = "summaries"
    summary_files = {}
    for f in os.listdir(summ_dir):
        m = re.match(r"^(\d+)_.*\.md$", f)
        if m:
            summary_files[int(m.group(1))] = os.path.join(summ_dir, f)

    # Only process re-summarized papers: 1-71
    targets = sorted([n for n in range(1, 72) if n in page_by_num and n in summary_files])
    print(f"처리 대상: {len(targets)}편 (1-71)\n")

    # Allow range filter via args
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 71
    targets = [n for n in targets if start <= n <= end]
    print(f"실제 처리 범위: {start}-{end} = {len(targets)}편\n")

    success, failed = [], []
    for i, num in enumerate(targets, 1):
        pid, title = page_by_num[num]
        spath = summary_files[num]
        label = f"[{i}/{len(targets)}] {num:02d}: {title[:50]}"
        try:
            print(f"{label} ... ", end="", flush=True)
            resync_page(pid, spath)
            print("OK")
            success.append(num)
        except Exception as e:
            print(f"FAIL: {str(e)[:200]}")
            failed.append((num, str(e)[:200]))

    print(f"\n=== 완료 ===")
    print(f"성공: {len(success)}편")
    print(f"실패: {len(failed)}편")
    for num, err in failed:
        print(f"  {num:02d}: {err}")


if __name__ == "__main__":
    main()

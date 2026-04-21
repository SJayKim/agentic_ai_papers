"""PostToolUse hook: summaries/*.md 파일 작성 후 품질 1차 검증.

통과 조건:
- 전체 80줄 이상
- 6개 필수 섹션 존재: Problem, Motivation, Method, Key Contribution, Experiment, Limitation

FAIL 시 exit 2 + stderr로 Claude에게 피드백 전달. 이미 저장된 파일은 유지된다.
"""
import sys
import json
import os
import re

try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    norm = file_path.replace("\\", "/")

    if not norm.endswith(".md"):
        sys.exit(0)

    marker = "/summaries/"
    if marker in norm:
        rel = norm.split(marker, 1)[1]
    elif norm.startswith("summaries/"):
        rel = norm[len("summaries/"):]
    else:
        sys.exit(0)

    if "/" in rel:
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    line_count = len(content.splitlines())

    required = ["Problem", "Motivation", "Method", "Key Contribution", "Experiment", "Limitation"]
    missing = [s for s in required if not re.search(rf"(?mi)^#+\s*{re.escape(s)}", content)]

    issues = []
    if line_count < 80:
        issues.append(f"전체 {line_count}줄 (80줄 이상 필요)")
    if missing:
        issues.append(f"누락 섹션: {', '.join(missing)}")

    if not issues:
        sys.exit(0)

    sys.stderr.write(f"[요약 품질 자동 검증 실패] {os.path.basename(file_path)}\n")
    for i in issues:
        sys.stderr.write(f"  - {i}\n")
    sys.stderr.write("Step 2.5 품질 평가 에이전트를 실행하거나 보강한 뒤 재저장하세요.\n")
    sys.exit(2)


if __name__ == "__main__":
    main()

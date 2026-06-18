#!/usr/bin/env bash
# PreToolUse hook for Edit|Write|NotebookEdit
# Blocks modification of secret/credential files in this project.
#
# Protected:
#   - .claude/.mcp.json        (contains NOTION_TOKEN)
#   - any *.env / *.env.*      (API keys)
#   - any *.pem / *.key        (generic secrets)
#
# Reads tool input JSON from stdin, extracts file_path, exits 2 to block.

FILE=$(python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ti = data.get('tool_input', {})
    print(ti.get('file_path', '') or ti.get('notebook_path', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$FILE" ] && exit 0

# Normalize to forward slashes for matching
NORM=$(echo "$FILE" | tr '\\' '/')

case "$NORM" in
    *"/.claude/.mcp.json"|*".claude/.mcp.json")
        echo "Blocked: .claude/.mcp.json contains NOTION_TOKEN. Edit manually outside Claude." >&2
        exit 2 ;;
    *.env|*.env.*)
        echo "Blocked: .env contains API keys. Edit manually outside Claude." >&2
        exit 2 ;;
    *.pem|*.key)
        echo "Blocked: secret file ($FILE)." >&2
        exit 2 ;;
esac

exit 0

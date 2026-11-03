#!/usr/bin/env bash
# A/B: claude -p с MCP codebase-memory-mcp / с плагином boost / без ничего.
# Использование: run_ab.sh <arm: none|boost|mcp> <qid> <cwd> <out-dir>
# Вопросы: questions.md. Переменные: REPO (корень claude_-skills), CBM_BIN,
# CBM_HOME (каталог кэша сервера), MODEL (по умолчанию sonnet).
set -euo pipefail
arm=$1 qid=$2 cwd=$3 out=$4
REPO=${REPO:-/home/user/claude_-skills}
MODEL=${MODEL:-sonnet}
prompt=$(python3 -I - "$REPO/pilot-notes/codebase-memory-mcp/questions.md" "$qid" <<'PY'
import re,sys
t=open(sys.argv[1]).read()
m=re.search(r'^## '+re.escape(sys.argv[2])+r'\..*?\n\n((?:> .*\n)+)',t,re.M)
print(" ".join(l[2:] for l in m.group(1).splitlines()))
PY
)
tools=(Read Grep Glob 'Bash(git diff:*)' 'Bash(git status:*)' 'Bash(python3 -I:*)')
extra=()
case $arm in
  none) ;;
  boost) extra=(--plugin-dir "$REPO/plugins/boost") ;;
  mcp)
    cfg=$out/cbm-mcp.json
    cat > "$cfg" <<JSON
{"mcpServers":{"codebase-memory-mcp":{"command":"$CBM_BIN","args":[],
 "env":{"CBM_CACHE_DIR":"$CBM_HOME/cache","XDG_CONFIG_HOME":"$CBM_HOME/config","CBM_ALLOWED_ROOT":"$cwd"}}}}
JSON
    extra=(--mcp-config "$cfg")
    tools+=(mcp__codebase-memory-mcp)
    prompt="$prompt (Репозиторий уже проиндексирован в codebase-memory-mcp: $cwd.)"
    ;;
esac
mkdir -p "$out"
cd "$cwd"
t0=$(date +%s.%N)
claude -p "$prompt" --model "$MODEL" --setting-sources project \
  --strict-mcp-config "${extra[@]}" --allowedTools "${tools[@]}" \
  --max-budget-usd 0.8 --output-format json < /dev/null > "$out/$arm-$qid.json" 2> "$out/$arm-$qid.err" || true
echo "$(date +%s.%N) - $t0" | bc > "$out/$arm-$qid.time"
python3 -I -c "import json,sys;d=json.load(open(sys.argv[1]));u=d.get('usage',{});print(sys.argv[2],d.get('total_cost_usd'),d.get('num_turns'),u.get('input_tokens'),u.get('cache_creation_input_tokens'),u.get('cache_read_input_tokens'),u.get('output_tokens'))" "$out/$arm-$qid.json" "$arm-$qid"

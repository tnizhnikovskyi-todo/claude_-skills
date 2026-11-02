#!/usr/bin/env bash
# A/B прогон: run_ab.sh <arm: base|rtk> <out_dir> [task_id...]
# base — без хука; rtk — PreToolUse-хук `rtk hook claude` через --settings,
# rtk берётся из $RTK_BIN_DIR (по умолчанию <scratch>/bin).
set -euo pipefail
ARM=$1; OUT=$2; shift 2
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../.." && pwd)
SCR=${SCR:?set SCR to scratch dir}
ODOO_MAP=$REPO/plugins/boost/skills/odoo-model-map/scripts/odoo_map.py
mkdir -p "$OUT" "$SCR/work"
EXTRA=()
if [ "$ARM" = rtk ]; then
  export PATH=${RTK_BIN_DIR:-$SCR/bin}:$PATH
  export RTK_TELEMETRY_DISABLED=1 XDG_CONFIG_HOME=$SCR/xdg/config XDG_DATA_HOME=$SCR/xdg/data
  EXTRA=(--settings "$HERE/settings-rtk.json")
fi
IDS=("$@"); [ ${#IDS[@]} -eq 0 ] && IDS=($(python3 -c "import json;print(' '.join(t['id'] for t in json.load(open('$HERE/tasks.json'))))"))
for id in "${IDS[@]}"; do
  W=$SCR/work/$ARM-$id; rm -rf "$W"; cp -a "$SCR/stand" "$W"
  P=$(python3 -c "import json,sys;t=[t for t in json.load(open('$HERE/tasks.json')) if t['id']=='$id'][0];print(t['prompt'].replace('ODOO_MAP','$ODOO_MAP'))")
  (cd "$W" && claude -p "$P" --allowedTools "Bash" --disallowedTools "Read Grep Glob Edit Write WebFetch WebSearch Task" \
     --output-format stream-json --verbose --model "${MODEL:-claude-sonnet-5-5}" "${EXTRA[@]}" --max-turns 15 > "$OUT/$id.jsonl" 2> "$OUT/$id.err") || true
  echo "done $ARM $id"
done

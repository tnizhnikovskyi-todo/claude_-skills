#!/usr/bin/env bash
# Плечо MCP. Запускать ТОЛЬКО после разрешения на запуск бинарника.
# 1) повторная сверка SHA-256; 2) индексация с замером времени и размера;
# 3) пробы графа на связи Odoo через `cli`; 4) прогоны A/B плеча mcp.
# Переменные: S (scratchpad), CBM_BIN, CBM_HOME.
set -euo pipefail
: "${S:?}" "${CBM_BIN:?}" "${CBM_HOME:?}"
HERE=$(cd "$(dirname "$0")" && pwd)
SHA=8453015145f072c1b9b019cbdd02cea8cc6f18cc5e116036dd20992631c638c7
echo "$SHA  $S/cbm-dl/cbm.tar.gz" | sha256sum -c -
export CBM_CACHE_DIR=$CBM_HOME/cache XDG_CONFIG_HOME=$CBM_HOME/config CBM_SEMANTIC_ENABLED=${CBM_SEMANTIC_ENABLED:-1}
mkdir -p "$CBM_CACHE_DIR" "$XDG_CONFIG_HOME" "$S/probe"
cli() { "$CBM_BIN" cli "$@"; }
"$CBM_BIN" --version | tee "$S/probe/version.txt"
for t in pilot pilot-diff odoo19; do
  export CBM_ALLOWED_ROOT=$S/$t
  t0=$(date +%s.%N)
  cli index_repository "{\"repo_path\":\"$S/$t\"}" > "$S/probe/index-$t.json" 2>&1 || true
  echo "$t $(echo "$(date +%s.%N) - $t0" | bc) s" | tee -a "$S/probe/index-times.txt"
done
du -sh "$CBM_CACHE_DIR" | tee -a "$S/probe/index-times.txt"
cli list_projects '{}' > "$S/probe/projects.json"
# Пробы (имя проекта берётся из list_projects; подставить вручную при расхождении)
P=$(python3 -I -c "import json,sys;d=json.load(open(sys.argv[1]));print(d)" "$S/probe/projects.json" | head -c 2000)
echo "$P"

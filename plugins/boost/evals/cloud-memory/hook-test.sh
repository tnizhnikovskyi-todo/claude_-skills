#!/usr/bin/env bash
# Детерминированная проверка хуков cloud-memory без модели и сети.
# Запуск: bash plugins/boost/evals/cloud-memory/hook-test.sh
set -u
H="$(cd "$(dirname "$0")/../../hooks" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok()   { echo "ok   $1"; }
bad()  { echo "FAIL $1"; fail=1; }
start() { echo '{"hook_event_name":"SessionStart","source":"startup"}' | CLAUDE_PROJECT_DIR="$T" "$@" bash "$H/memory-start.sh"; }
stop()  { echo '{"hook_event_name":"Stop","stop_hook_active":false}' | CLAUDE_PROJECT_DIR="$T" bash "$H/memory-stop.sh"; }

cd "$T" && git init -q && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init

# 1. Нет memory/ -> обе молчат, код 0
out="$(start)"; rc=$?; [ $rc -eq 0 ] && [ -z "$out" ] && ok "start: без memory/ молчит" || bad "start: без memory/"
out="$(stop)";  rc=$?; [ $rc -eq 0 ] && [ -z "$out" ] && ok "stop: без memory/ молчит"  || bad "stop: без memory/"

# 2. memory/ без INDEX.md -> start молчит
mkdir memory; echo x > memory/note.md
out="$(start)"; [ -z "$out" ] && ok "start: без INDEX.md молчит" || bad "start: без INDEX.md"

# 3. INDEX + HANDOFF подмешиваются, <private> маскируется
printf '# Память\n\n- 2026-11-01 decision [deploy] Деплой по вторникам → a.md\n- x <private>pw=123</private> y\n' > memory/INDEX.md
printf '# Handoff\nДальше: экспорт.\n' > memory/HANDOFF.md
out="$(start)"
grep -q 'Деплой по вторникам' <<<"$out" && ok "start: индекс в выводе" || bad "start: индекс"
grep -q 'Дальше: экспорт' <<<"$out" && ok "start: handoff в выводе" || bad "start: handoff"
grep -q 'pw=123' <<<"$out" && bad "start: <private> утёк" || ok "start: <private> замаскирован"

# 4. Лимит размера: строки целые, есть пометка об обрезке
for i in $(seq 1 500); do echo "- 2026-10-01 discovery [t] Запись номер $i → x$i.md"; done >> memory/INDEX.md
out="$(start)"; n=$(printf '%s' "$out" | wc -c)
[ "$n" -lt 10000 ] && ok "start: вывод ограничен ($n байт)" || bad "start: вывод $n байт"
grep -q 'обрезан на 6000 байт' <<<"$out" && ok "start: пометка об обрезке" || bad "start: нет пометки"
printf '%s' "$out" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1 && ok "start: валидный UTF-8" || bad "start: битый UTF-8"
out="$(start env CLOUD_MEMORY_INDEX_MAX=200)"; grep -q 'обрезан на 200' <<<"$out" && ok "start: лимит из env" || bad "start: лимит из env"

# 5. Stop: незакоммиченная memory/ -> JSON systemMessage, без коммита
out="$(stop)"
printf '%s' "$out" | grep -q '"systemMessage"' && ok "stop: напоминание при изменениях" || bad "stop: нет напоминания"
if command -v jq >/dev/null; then printf '%s' "$out" | jq -e .systemMessage >/dev/null && ok "stop: валидный JSON" || bad "stop: JSON"; fi
[ "$(git rev-list --count HEAD)" = 1 ] && ok "stop: ничего не закоммичено" || bad "stop: появился коммит"
git add memory && git -c user.email=t@t -c user.name=t commit -qm mem
out="$(stop)"; [ -z "$out" ] && ok "stop: после коммита молчит" || bad "stop: после коммита"

# 6. Скорость
s=$(date +%s%N); start >/dev/null; e=$(( ($(date +%s%N)-s)/1000000 ))
[ "$e" -lt 500 ] && ok "start: ${e} мс" || bad "start: медленно ${e} мс"

exit $fail

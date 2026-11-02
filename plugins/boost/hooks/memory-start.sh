#!/usr/bin/env bash
# boost / cloud-memory: SessionStart hook.
# If the project has memory/INDEX.md, print it (size-capped) and memory/HANDOFF.md
# to stdout; Claude Code adds SessionStart stdout to the session context.
# No memory/INDEX.md -> print nothing, exit 0. No network, bash + coreutils + awk.

cat >/dev/null 2>&1   # drain the hook JSON on stdin; we do not need it

root="${CLAUDE_PROJECT_DIR:-$PWD}"
dir="$root/memory"
[ -f "$dir/INDEX.md" ] || exit 0

INDEX_MAX="${CLOUD_MEMORY_INDEX_MAX:-6000}"     # bytes of INDEX.md to inject
HANDOFF_MAX="${CLOUD_MEMORY_HANDOFF_MAX:-3000}" # bytes of HANDOFF.md to inject

# Print whole lines until the byte budget is spent; never cut a line (or a
# UTF-8 character) in half. Single-line <private>...</private> spans are masked.
capped() {
  LC_ALL=C awk -v max="$2" -v name="$3" '
    { gsub(/<private>.*<\/private>/, "[private]") }
    used + length($0) + 1 > max { cut = 1; exit }
    { print; used += length($0) + 1 }
    END { if (cut) printf "… [%s обрезан на %d байт; полный текст: cat %s]\n", name, max, name }
  ' "$1"
}

echo "<cloud-memory>"
echo "Память проекта в git: memory/. Ниже индекс (по строке на запись) и передача от прошлой сессии."
echo "Подробности по запросу: grep -ril '<слово>' memory/ → прочитать нужный файл. Правила записи: скилл cloud-memory."
echo
echo "## memory/INDEX.md"
capped "$dir/INDEX.md" "$INDEX_MAX" "memory/INDEX.md"
if [ -f "$dir/HANDOFF.md" ]; then
  echo
  echo "## memory/HANDOFF.md"
  capped "$dir/HANDOFF.md" "$HANDOFF_MAX" "memory/HANDOFF.md"
fi
echo "</cloud-memory>"
exit 0

#!/usr/bin/env bash
# boost / cloud-memory: Stop hook. Reminder only, never commits.
# If memory/ has uncommitted or untracked changes, show the user a one-line
# reminder (systemMessage, not added to Claude's context, does not block).
# No memory/ or no git -> nothing. No network, bash + git.

cat >/dev/null 2>&1

root="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$root/memory" ] || exit 0
command -v git >/dev/null 2>&1 || exit 0

changes="$(git -C "$root" status --porcelain -uall -- memory 2>/dev/null)" || exit 0
[ -n "$changes" ] || exit 0

n="$(printf '%s\n' "$changes" | wc -l | tr -d ' ')"
printf '{"systemMessage":"cloud-memory: файлов в memory/ с незакоммиченными изменениями: %s. В облачной сессии они пропадут вместе с контейнером: закоммитьте и запушьте (или попросите Claude)."}\n' "$n"
exit 0

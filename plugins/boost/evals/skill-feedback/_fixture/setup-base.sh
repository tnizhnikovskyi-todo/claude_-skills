#!/usr/bin/env bash
# Общая подготовка: git-репозиторий скиллов без observations/.
set -e
FIX="$1"
cp -r "$FIX/README.md" "$FIX/skills" .
git init -q
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm init

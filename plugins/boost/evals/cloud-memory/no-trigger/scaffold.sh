#!/usr/bin/env bash
# Пустой git-репозиторий без memory/ (кейсы remember-decision, no-trigger).
set -e
git init -q
echo "# demo project" > README.md
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm init

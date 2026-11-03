#!/usr/bin/env bash
# git-репозиторий с маленьким Python-проектом (кейс long-plan).
set -e
git init -q
echo "# demo project" > README.md
cat > utils.py <<'PY'
import re


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]", "-", text.lower())).strip("-")
PY
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm init

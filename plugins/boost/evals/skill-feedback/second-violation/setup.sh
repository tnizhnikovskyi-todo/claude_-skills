#!/usr/bin/env bash
set -e
FIX="$(dirname "$0")/../_fixture"
bash "$FIX/setup-base.sh" "$FIX"
mkdir -p observations && cp "$FIX/prior/"*.md observations/
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm "prior observation"

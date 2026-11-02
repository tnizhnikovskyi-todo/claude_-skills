#!/usr/bin/env bash
# Копия pilot/ (Odoo 19, шаблон CLAUDE.md уже применён) в рабочий каталог.
set -euo pipefail
cp -r "$(dirname "$0")/../_fixture/pilot/." .

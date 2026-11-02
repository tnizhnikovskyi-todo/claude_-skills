#!/usr/bin/env bash
# Кладёт общую фикстуру (три модуля Odoo 19) в рабочий каталог eval-прогона.
set -euo pipefail
cp -r "$(dirname "$0")/../_fixture/addons" .

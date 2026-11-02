#!/usr/bin/env bash
# Кладёт фикстуру в рабочий каталог eval-прогона.
set -euo pipefail
cp -r "$(dirname "$0")/fixture/." .

#!/usr/bin/env bash
# Кладёт фикстуру (модуль td_rental, Odoo 19, 7 ловушек установки) в рабочий каталог прогона.
set -euo pipefail
cp -r "$(dirname "$0")/../_fixture/addons" .

#!/usr/bin/env bash
# Использует фикстуру соседнего кейса odoo-module.
set -euo pipefail
cp -r "$(dirname "$0")/../odoo-module/fixture/." .

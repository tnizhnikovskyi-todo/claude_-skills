#!/usr/bin/env bash
# Использует фикстуру соседнего кейса keep-validation.
set -euo pipefail
cp -r "$(dirname "$0")/../keep-validation/fixture/." .

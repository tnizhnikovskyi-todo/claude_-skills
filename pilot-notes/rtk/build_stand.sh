#!/usr/bin/env bash
# Собирает стенд для A/B rtk: копия pilot/ в отдельном git-репозитории
# с заложенными «тихими потерями». Использование: build_stand.sh <repo> <dest>
set -euo pipefail
REPO=$1; D=$2
rm -rf "$D"; mkdir -p "$D"; cp -r "$REPO/pilot/." "$D/"; cd "$D"
git init -q -b main; git config user.email pilot@example.com; git config user.name pilot
git add -A; git commit -qm "Initial import of workshop modules"

# L1: важное только в ТЕЛЕ коммита (git log в rtk оставляет тему)
python3 - <<'PY'
import re
p='addons/td_workshop/models/workshop_order.py'
s=open(p).read()
s=s.replace("class ","# priority handling\nclass ",1)
open(p,'w').write(s)
PY
git commit -qam "Refactor workshop order priority handling" \
  -m "MIGRATION: run scripts/migrate_priority.py BEFORE upgrade, otherwise priority 3 orders are lost. Ticket WS-4471."
for i in $(seq 1 25); do echo "# note $i" >> README.md; git commit -qam "Docs: update readme section $i"; done

# L2: большой незакоммиченный дифф, ключевая правка далеко в конце
python3 - <<'PY'
lines=[f"    # generated constant {i}\n    CONST_{i} = {i}\n" for i in range(400)]
p='addons/td_workshop/models/workshop_order_line.py'
s=open(p).read()
s+= "\n\nclass _Generated:\n" + "".join(lines) + "    DEFAULT_DISCOUNT = 0.35  # was 0.0\n"
open(p,'w').write(s)
PY

# L3: find — файл в скрытом каталоге и gitignored XML
mkdir -p .github/workflows addons/td_workshop/data/local
printf 'name: ci\non: push\n' > .github/workflows/odoo-ci.yml
printf '<odoo><record id="demo_override" model="res.partner"><field name="name">X</field></record></odoo>\n' > addons/td_workshop/data/local/override_demo.xml
echo 'addons/td_workshop/data/local/' >> .gitignore
printf '<odoo/>\n' > .github/workflows/report_template.xml

# L4: py_compile — синтаксическая ошибка в одном файле
printf 'def broken(:\n    return 1\n' > addons/td_workshop_sale/models/legacy_hooks.py

# L5: длинный вывод с одной ошибкой в середине
mkdir -p tools
cat > tools/run_checks.py <<'PY'
import sys
for i in range(1, 1201):
    if i == 637:
        print(f"[check {i:04d}] ERROR td.workshop.order.line: amount_total mismatch on record id=8842 (expected 1180.00 got 1118.00)")
    else:
        print(f"[check {i:04d}] OK   model td.workshop.order field state consistent")
print("SUMMARY: 1200 checks done")
PY

# L6: grep — много совпадений, нужное одно за лимитом
mkdir -p addons/td_workshop/legacy
for f in $(seq 1 30); do
  { for i in $(seq 1 12); do echo "    # TODO cleanup item $f.$i"; done; } > addons/td_workshop/legacy/mod_$f.py
done
echo "    # TODO SECURITY: remove sudo() bypass before go-live" >> addons/td_workshop/legacy/mod_27.py
git add tools addons/td_workshop/legacy .github .gitignore
git commit -qm "Add checks tool, legacy stubs, CI"
# legacy_hooks.py и дифф остаются незакоммиченными
echo "stand ready: $D"

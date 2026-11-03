| задача | ключи | ходы | вход (вкл. кэш) | выход | байт вывода Bash | $ |
|---|---|---|---|---|---|---|
| T1-gitlog | 2/2 | 2 | 70396 | 256 | 166 | 0.0105 |
|   | `git log --all -i -E --grep='priorit|приоритет' -n 20 --format='%h %s%n%b---'` |
| T2-gitdiff | 2/2 | 3 | 124004 | 727 | 20667 | 0.0570 |
|   | `git diff` |
|   | `git grep -n "DEFAULT_DISCOUNT" HEAD -- . ; git status --short` |
| T3-gitstatus | 2/2 | 2 | 70306 | 168 | 101 | 0.0095 |
|   | `git status --porcelain=v1 -uall` |
| T4-grep | 2/2 | 2 | 83669 | 320 | 24179 | 0.0644 |
|   | `grep -rn TODO addons` |
| T5-find | 2/2 | 2 | 70486 | 605 | 234 | 0.0143 |
|   | `find . -type f -name '*.xml' -not -path './addons/*/views/*' | sort; echo "---total:"; find . -type f -name '*.xml' | wc -l` |
| T6-pycompile | 2/2 | 2 | 70496 | 376 | 128 | 0.0122 |
|   | `export PYTHONPYCACHEPREFIX=/tmp/pyc_x; n=0; find addons -name '*.py' -print0 | while IFS= read -r -d '' f; do python3 -m py_compile "$f" 2>&1 || true;` |
| T7-odoomap | 2/2 | 2 | 74191 | 323 | 8335 | 0.0110 |
|   | `python3 -I /home/user/claude_-skills/plugins/boost/skills/odoo-model-map/scripts/odoo_map.py addons` |
| T8-longlog | 4/4 | 3 | 120022 | 840 | 20169 | 0.0499 |
|   | `python3 tools/run_checks.py 2>&1 | head -c 20000; echo; echo "EXIT: ${PIPESTATUS[0]}"` |
|   | `python3 tools/run_checks.py > $TMPDIR/out.txt 2>&1; echo "EXIT: $?"; wc -l $TMPDIR/out.txt; grep -v ' OK ' $TMPDIR/out.txt | head -100` |
| **итого** | 18/18 | | 683570 | | 73979 | 0.2288 |

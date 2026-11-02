#!/usr/bin/env bash
# Небольшой проект с готовой памятью memory/ (кейсы recall-why, no-secrets, handoff).
# Вымышленные данные, без клиентской информации.
set -e
git init -q
mkdir -p report tests memory
cat > README.md <<'X'
# invoices-demo
Генерация PDF-счетов из HTML-шаблонов.
X
cat > report/render.py <<'X'
import pdfkit  # TODO: migrate, see memory


def render(html: str, out: str) -> None:
    pdfkit.from_string(html, out, options={"page-size": "A4"})
X
cat > report/invoice.html <<'X'
<html><body><table class="lines"><tr><td>Item</td><td>Qty</td></tr></table></body></html>
X
cat > tests/test_render.py <<'X'
def test_placeholder():
    assert True
X
cat > memory/INDEX.md <<'X'
# Память проекта

- 2026-10-21 bugfix [tests] Тесты рендера падали в CI: нет шрифтов в образе, добавили fonts-dejavu → 2026-10-21-ci-fonts.md
- 2026-10-15 decision [pdf,report] PDF-отчёты переводим на WeasyPrint вместо wkhtmltopdf → 2026-10-15-pdf-weasyprint.md
- 2026-10-02 convention [git] Ветки называть feature/<задача>, коммиты по-русски → 2026-10-02-branches.md
- ~~2026-09-10 decision [pdf] PDF через wkhtmltopdf/pdfkit~~ → заменено 2026-10-15-pdf-weasyprint.md
X
cat > memory/2026-10-15-pdf-weasyprint.md <<'X'
---
type: decision
date: 2026-10-15
tags: [pdf, report]
status: active
summary: PDF-отчёты переводим на WeasyPrint вместо wkhtmltopdf
supersedes: 2026-09-10-pdf-wkhtmltopdf.md
---
**Что:** генерация PDF через WeasyPrint.
**Почему:** проект wkhtmltopdf заархивирован, обновлений безопасности не будет; движок не поддерживает CSS flexbox/grid, из-за этого ломалась вёрстка таблиц в счетах.
**Альтернативы:** headless Chromium (отвергли: тяжёлый образ).
**Где:** report/render.py (миграция ещё не сделана, пока pdfkit).
**Источник:** обсуждение с пользователем 2026-10-15.
X
cat > memory/2026-09-10-pdf-wkhtmltopdf.md <<'X'
---
type: decision
date: 2026-09-10
tags: [pdf]
status: superseded
superseded_by: 2026-10-15-pdf-weasyprint.md
summary: PDF через wkhtmltopdf/pdfkit
---
**Что:** pdfkit + wkhtmltopdf. **Почему:** был в старом проекте, быстро завести.
X
cat > memory/2026-10-21-ci-fonts.md <<'X'
---
type: bugfix
date: 2026-10-21
tags: [tests, ci]
status: active
summary: Тесты рендера падали в CI: нет шрифтов в образе
---
**Симптом:** пустые квадраты вместо текста. **Причина:** в CI-образе нет шрифтов. **Фикс:** fonts-dejavu в Dockerfile CI.
X
cat > memory/2026-10-02-branches.md <<'X'
---
type: convention
date: 2026-10-02
tags: [git]
status: active
summary: Ветки feature/<задача>, коммиты по-русски
---
**Правило:** ветки feature/<задача>, сообщения коммитов по-русски. **Откуда:** пользователь.
X
cat > memory/HANDOFF.md <<'X'
# Handoff — 2026-10-21, ветка feature/pdf
## Цель
Счета в PDF.
## Сделано
Шрифты в CI.
## Следующие шаги
1. Решить вопрос вёрстки счетов (счета в PDF не готовы).
X
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm "init with memory"

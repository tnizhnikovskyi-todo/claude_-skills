#!/usr/bin/env python3
"""skill_prescan.py — детерминированный префильтр безопасности скилла/плагина.

Прототип из разбора catalog/semia (идеи Semia @379bc25, Apache-2.0: словарь
эффектов и классов, «неразрешённая цель», «заявление против поведения»;
код и шаблоны свои). Только stdlib. Ничего не исполняет и не ходит в сеть:
читает файлы как байты, base64-блоки декодирует и сканирует повторно.

Это НЕ замена ручного разбора по чек-листу: ловит грубые и известные
шаблоны и показывает, какие файлы исполняются без вызова скилла. Чистый
вывод не значит «безопасно» (см. «Граница покрытия» в README карточки).

Запуск:  python3 -I skill_prescan.py <папка-скилла-или-плагина> [--json]
Код выхода: 2 — есть BLOCK, 1 — есть HIGH, 0 — иначе.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import re
import sys
from pathlib import Path

MAX_BYTES = 2_000_000
SEV_ORDER = {"BLOCK": 0, "HIGH": 1, "REVIEW": 2, "INFO": 3}

# (класс, уровень, регулярка). Регулярки без учёта регистра.
RULES: list[tuple[str, str, str]] = [
    # Удалённое исполнение и дропперы
    ("remote-exec", "BLOCK", r"\b(curl|wget|iwr|Invoke-WebRequest)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"),
    ("remote-exec", "BLOCK", r"\bbase64\s+(-d|-D|--decode)\b[^\n]*\|\s*(sudo\s+)?(ba|z)?sh\b"),
    ("remote-exec", "BLOCK", r"\b(eval|source)\s+[\"']?\$\((curl|wget)\b"),
    ("remote-exec", "BLOCK", r"\b(iex|Invoke-Expression)\b"),
    ("remote-exec", "HIGH", r"\b(exec|eval)\s*\(\s*(base64|codecs|zlib|bytes\.fromhex|atob)"),
    # Неразрешённая или подозрительная цель
    ("unresolved-target", "BLOCK", r"https?://(\d{1,3}\.){3}\d{1,3}"),
    ("unresolved-target", "BLOCK", r"\b(glot\.io|pastebin\.com|paste\.ee|hastebin|transfer\.sh|webhook\.site|requestbin|ngrok(-free)?\.(io|app)|trycloudflare\.com)"),
    ("exfil-channel", "HIGH", r"\b(discord(app)?\.com/api/webhooks|api\.telegram\.org/bot|hooks\.slack\.com)"),
    ("social-engineering", "BLOCK", r"\.(zip|7z|rar)\b[^\n]{0,200}\b(pass(word)?|пароль)\b\s*[:=`'\"]"),
    ("social-engineering", "HIGH", r"\b(download|скачай|завантаж)\w*\b[^\n]{0,120}\.(exe|dmg|pkg|msi|zip)\b"),
    ("social-engineering", "HIGH", r"(copy|paste|скопируй|вставь)[^\n]{0,80}(terminal|терминал)"),
    ("social-engineering", "HIGH", r"\b(must|needs? to) be installed before\b|\bbefore (using this skill|proceeding)\b"),
    # Секреты и чувствительные локальные данные
    ("secret-access", "HIGH", r"~/\.(ssh|aws|gnupg|kube|docker/config|netrc|npmrc|pypirc)|\bid_(rsa|ed25519)\b|\.git-credentials|Login Data|Cookies\.binarycookies|keychain|wallet\.dat"),
    ("secret-access", "HIGH", r"--browser\s+real\b|user-data-dir|/Chrome/(Default|Profile)|\breal (browser|chrome) (profile|session)"),
    ("secret-access", "REVIEW", r"\b(printenv|env\s*\||os\.environ\b|process\.env\b|\$\{?[A-Z_]*(TOKEN|SECRET|API_KEY|PASSWORD)\}?)"),
    # Снятие защит харнесса
    ("permission-bypass", "HIGH", r"bypassPermissions|dangerously-skip-permissions|--permission-mode\s+(bypass|dontAsk)|\"defaultMode\"\s*:\s*\"bypass"),
    ("permission-bypass", "REVIEW", r"allowed-tools:[^\n]*\bBash\b(?!\()|Bash\(\*\)|\"allow\"\s*:\s*\[[^\]]*\"Bash\""),
    # Инструкции, меняющие поведение агента (прямая инъекция)
    ("instruction-override", "HIGH", r"\b(ignore|disregard|override)\b[^\n]{0,40}\b(previous|prior|above|system|all)\b[^\n]{0,20}\b(instruction|prompt|rule)s?"),
    ("instruction-override", "HIGH", r"\b(do not|don't|never)\b[^\n]{0,30}\b(tell|inform|notify|mention|reveal to|ask)\b[^\n]{0,20}\b(the )?user"),
    ("instruction-override", "HIGH", r"\bwithout (asking|confirmation|telling|the user'?s? (knowledge|permission))"),
    ("instruction-override", "HIGH", r"(игнорируй|не сообщай пользовател|не спрашивай подтвержд|без подтверждения|не говори пользовател)"),
    # Цепочка поставки
    ("supply-chain", "REVIEW", r"@latest\b|\bnpx\s+(-y|--yes)\b|\bpip3?\s+install\s+(?![^\n]*==)[^\n-]|\buvx\s+(?![^\n]*[@=]=?\d)|--break-system-packages|\bsudo\b|\bchmod\s+\+x\b"),
    ("supply-chain", "REVIEW", r"\bgit\s+clone\b(?![^\n]*(--branch\s+v?\d|@[0-9a-f]{7,}|&&\s*git\s+checkout))"),
    # Телеметрия
    ("telemetry", "REVIEW", r"\b(posthog|sentry_sdk|@sentry/|mixpanel|segment\.(io|com)|amplitude|telemetry|analytics\.track)\b"),
    # Обфускация
    ("obfuscation", "HIGH", r"\\x[0-9a-f]{2}(\\x[0-9a-f]{2}){15,}|String\.fromCharCode\((\d+,\s*){10,}|\bchr\(\d+\)\s*\+\s*chr\("),
]
COMPILED = [(c, s, re.compile(p, re.I)) for c, s, p in RULES]
# Отрицание («never … without confirmation») — это защита, а не инъекция.
NEGATED = re.compile(r"\b(no|never|not|nothing|don't|do not)\b[^\n]{0,50}\bwithout\b|(^|\s)не\s[^\n]{0,50}\sбез\s|игнорируй;\s*не\s", re.I)
# Запрет перед совпадением («Никаких `curl | bash`», «never run …») — правило, а не действие.
FORBID = re.compile(r"(никаких|нельзя|запрещ\w*|не запускай|не выполняй|\bnever\b|\bavoid\b|\bdo not\b|\bdon't\b)", re.I)
# Шаблон инъекции в кавычках/коде — скорее всего сканер или документация о защите.
QUOTED = re.compile(r"(r?[\"'`])[^\"'`]{0,80}(ignore|disregard|override)[^\"'`]{0,80}\1", re.I)
DOC_CONTEXT = re.compile(r"\b(injection|инъекц|detect|pattern|example|attack|атак)\w*", re.I)

HIDDEN_CHARS = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿\U000e0000-\U000e007f]")
B64_BLOB = re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")
URL = re.compile(r"https?://[^\s\"'<>)\]`]+")
HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
BROAD_DESC = re.compile(r"\b(always|any task|every (task|request|session)|proactively|in all cases|всегда|любой задач)\b", re.I)

# Поверхности, которые исполняются без явного вызова скилла
EXEC_SURFACES = [
    (re.compile(r"(^|/)hooks/hooks\.json$|(^|/)\.claude/settings(\.local)?\.json$|(^|/)settings\.json$"), "hooks/settings: исполняются харнессом"),
    (re.compile(r"(^|/)\.mcp\.json$"), "MCP-сервер: процесс/сеть при старте сессии"),
    (re.compile(r"(^|/)\.claude-plugin/(plugin|marketplace)\.json$"), "манифест плагина: проверить hooks/mcpServers/источники"),
    (re.compile(r"(^|/)package\.json$"), "package.json: pre/postinstall выполняются при установке"),
    (re.compile(r"(^|/)(setup\.py|pyproject\.toml|Makefile|install\.sh|setup\.sh)$"), "установщик/сборка"),
]
SKIPPED_BY_SEMIA = {"build", "dist", "vendor", "out", "target", "node_modules", "coverage"}
BINARY_EXT = {".exe", ".dll", ".so", ".dylib", ".bin", ".pyz", ".pyc", ".jar", ".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".whl", ".dmg", ".pkg", ".msi", ".wasm"}


def iter_files(root: Path):
    for cur, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(files):
            yield Path(cur, name)


def scan_text(rel: str, text: str, findings: list, origin: str = "", base_line: int = 0) -> None:
    for i, line in enumerate(text.splitlines(), 1):
        lineno = base_line or i
        for cls, sev, rx in COMPILED:
            m = rx.search(line)
            if not m:
                continue
            if sev in ("BLOCK", "HIGH") and FORBID.search(line[: m.start()]):
                sev, cls = "REVIEW", cls + "(negated)"
            elif cls == "instruction-override":
                if NEGATED.search(line):
                    continue
                if QUOTED.search(line) or DOC_CONTEXT.search(line):
                    sev, cls = "REVIEW", "instruction-override(quoted)"
            findings.append((sev, cls, rel, lineno, origin + line.strip()[:160]))
        if HIDDEN_CHARS.search(line):
            findings.append(("HIGH", "hidden-text", rel, lineno, origin + "невидимые/bidi-символы: " + repr(line.strip()[:80])))
        for blob in B64_BLOB.findall(line):
            if origin or len(blob) < 40:
                continue
            try:
                dec = base64.b64decode(blob + "=" * (-len(blob) % 4), validate=True).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError):
                continue
            if sum(ch.isprintable() for ch in dec) / max(1, len(dec)) < 0.9:
                continue
            findings.append(("REVIEW", "encoded-blob", rel, lineno, "base64 → " + dec[:120]))
            scan_text(rel, dec, findings, origin="[из base64] ", base_line=lineno)
    if rel.endswith(".md") and not origin:
        for m in HTML_COMMENT.finditer(text):
            body = m.group(1).strip()
            if len(body) > 20:
                lineno = text.count("\n", 0, m.start()) + 1
                findings.append(("REVIEW", "hidden-text", rel, lineno, "HTML-комментарий: " + body[:120]))


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0
    root = Path(argv[0]).resolve()
    as_json = "--json" in argv
    findings: list[tuple[str, str, str, int, str]] = []
    surfaces, hosts, unread = [], {}, []
    files = list(iter_files(root))
    for path in files:
        rel = path.relative_to(root).as_posix()
        parts = set(rel.split("/")[:-1])
        if parts & SKIPPED_BY_SEMIA:
            findings.append(("REVIEW", "inventory", rel, 0, "в папке, которую многие сканеры пропускают"))
        for rx, why in EXEC_SURFACES:
            if rx.search(rel):
                surfaces.append((rel, why))
        if path.suffix.lower() in BINARY_EXT:
            findings.append(("HIGH", "opaque-binary", rel, 0, "бинарь/архив: прочитать нельзя, сверить с исходниками или не ставить"))
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            unread.append(f"{rel}: {exc}")
            continue
        if len(data) > MAX_BYTES or b"\0" in data[:4096]:
            unread.append(f"{rel}: двоичный или больше {MAX_BYTES} байт")
            continue
        text = data.decode("utf-8", errors="replace")
        if os.access(path, os.X_OK) and not path.suffix:
            findings.append(("REVIEW", "inventory", rel, 0, "исполняемый файл без расширения"))
        scan_text(rel, text, findings)
        if rel.endswith("package.json") and re.search(r"\"(pre|post)?install\"\s*:", text):
            findings.append(("HIGH", "install-hook", rel, 0, "скрипт npm (pre/post)install"))
        if "SKILL.md" in rel:
            m = re.search(r"^description:\s*(.+)$", text, re.M)
            if m and BROAD_DESC.search(m.group(1)):
                findings.append(("REVIEW", "broad-trigger", rel, 0, "широкий description: " + m.group(1)[:120]))
        for url in URL.findall(text):
            host = url.split("/")[2].lower()
            hosts.setdefault(host, rel)

    findings.sort(key=lambda f: (SEV_ORDER[f[0]], f[1], f[2], f[3]))
    worst = min((SEV_ORDER[f[0]] for f in findings), default=9)
    if as_json:
        print(json.dumps({"root": str(root), "files": len(files), "findings": findings,
                          "exec_surfaces": surfaces, "hosts": sorted(hosts), "unread": unread},
                         ensure_ascii=False, indent=1))
    else:
        print(f"# prescan: {root.name} ({len(files)} файлов)\n")
        print("## Поверхности исполнения без вызова скилла\n")
        print("\n".join(f"- `{r}` — {w}" for r, w in surfaces) or "- нет")
        print("\n## Находки\n\n| Уровень | Класс | Файл:строка | Фрагмент |\n|---|---|---|---|")
        for sev, cls, rel, ln, frag in findings:
            frag = frag.replace("|", "\\|")
            print(f"| {sev} | {cls} | `{rel}:{ln}` | `{frag}` |")
        print("\n## Внешние хосты\n")
        print(", ".join(f"`{h}`" for h in sorted(hosts)) or "нет")
        print("\n## Не прочитано\n")
        print("\n".join(f"- {u}" for u in unread) or "- всё прочитано")
    return 2 if worst == 0 else 1 if worst == 1 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""skill-prescan.py: детерминированная проверка плагина или папки скиллов
до установки (шаг -1 сессий анализа) и перед публикацией в маркетплейс.

Только stdlib. Ничего из проверяемого не исполняет и не импортирует, в сеть
не ходит: читает файлы как текст, base64/hex-блоки декодирует и сканирует
повторно. Чистый вывод не значит «безопасно»: поток данных, сила ворот и
семантику инструкций смотрит человек или модель по чек-листу.

Запуск:
  python3 -I scripts/skill-prescan.py <путь> [<путь> ...] [опции]
  python3 -I scripts/skill-prescan.py plugins/boost --exclude evals
  python3 -I scripts/skill-prescan.py --roots plugins/boost ../sale/plugins   # только дубли и lint имён

Опции:
  --roots A B ...      дополнительные корни для поиска дублей триггеров
                       (их безопасность не сканируется)
  --descriptions F     TSV «имя<TAB>description» для скиллов, которых нет на
                       диске (листинг сессии, скиллы аккаунта claude.ai)
  --exclude NAME ...   пропустить папки с таким именем (например, evals)
  --dup-threshold X    порог Unicode-Jaccard для дублей (по умолчанию 0.30)
  --fail-on warn       выход 1 и при WARN (по умолчанию только при BLOCK)
  --verbose            печатать все INFO, а не только сводку по классам
  --json               машинный вывод

Код выхода: 1 есть BLOCK (или WARN при --fail-on warn), 0 иначе, 2 ошибка
запуска.

Атрибуция. Часть регулярок взята дословно из khendzel/skills-janitor
(scripts/security.sh @ 4b42f391fd537b791d1c09c7825be0bc641fd41c, строки
93-134), MIT, Copyright (c) 2026 Krzysztof Hendzel; они помечены
`src="janitor"`. Текст лицензии: scripts/tests/skill-prescan/LICENSE-skills-janitor.
Идеи классов (неразрешённая цель, канал наружу, заявление против поведения,
закодированный мёртвый код, слепые зоны описи): berabuddies/Semia @ 379bc25,
Apache-2.0, пересказ, код свой. Прототип: catalog/semia/items/skill_prescan.py.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import itertools
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

VERSION = "1.0"
RANK = {"BLOCK": 0, "WARN": 1, "INFO": 2}
DOWN = {"BLOCK": "WARN", "WARN": "INFO", "INFO": "INFO"}
MAX_BYTES = 2_000_000
DESC_LIMIT = 1536          # Claude Code: description + when_to_use в листинге
SPEC_DESC_LIMIT = 1024     # открытая спецификация Agent Skills

INSTR_EXT = {".md", ".markdown", ".mdx", ".txt", ".rst"}
CODE_EXT = {".sh", ".bash", ".zsh", ".fish", ".py", ".js", ".mjs", ".cjs", ".ts",
            ".tsx", ".rb", ".pl", ".php", ".ps1", ".psm1", ".bat", ".cmd", ".lua"}
SHELL_EXT = {".sh", ".bash", ".zsh", ".fish"}
BINARY_EXT = {".exe", ".dll", ".so", ".dylib", ".bin", ".pyz", ".pyc", ".jar",
              ".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".xz", ".whl",
              ".dmg", ".pkg", ".msi", ".wasm", ".deb", ".rpm", ".apk"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".pdf",
             ".ttf", ".otf", ".woff", ".woff2", ".mp3", ".mp4", ".wav"}
OFFICE_EXT = {".docx", ".xlsx", ".pptx", ".odt"}
TEST_DIRS = {"evals", "tests", "test", "__tests__", "fixtures", "_fixture", "fixture", "spec"}
SKIPPED_ELSEWHERE = {"build", "dist", "vendor", "out", "target", "node_modules", "coverage"}

I, S = re.I, re.S
R = re.compile


@dataclass
class Finding:
    level: str
    cls: str
    rule: str
    file: str
    line: int
    text: str
    note: str = ""


# ---------------------------------------------------------------------------
# Правила по строкам: (rule, cls, уровень в коде/конфиге, уровень в
# инструкциях .md, регулярка, src). None = к этому виду файла не применять.
# ---------------------------------------------------------------------------
NET_CMD = r"(curl|wget|fetch)"
SHELLS = r"((ba|z|da|k|fi)?sh|python[23]?|node|perl|ruby|iex|pwsh|powershell)"

LINE_RULES = [
    # --- skills-janitor, дословно (MIT) ---
    ("inj-ignore", "injection", "WARN", "BLOCK", R(r"(ignore|disregard|forget)\s+(all\s+|any\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)", I), "janitor"),
    ("inj-conceal", "injection", "WARN", "BLOCK", R(r"do\s+not\s+(tell|inform|mention)(\s+(this|it|anything))?\s+(to\s+)?the\s+(user|human|operator)|do\s+not\s+(reveal|disclose)\s+(this|it|that|these\s+instructions|what\s+you\s+did)\s+(to\s+)?the\s+(user|human|operator)", I), "janitor"),
    ("inj-secrecy", "injection", "WARN", "BLOCK", R(r"\b(secretly|covertly)\s+(run|execute|send|upload|install|delete|download|call|post|report|collect|copy|read)\b|\bwithout\s+the\s+user('|')?s\s+knowledge\b", I), "janitor"),
    ("inj-exfil-word", "injection", "WARN", "WARN", R(r"\b(exfiltrate|keylog|beacon\s+home)\b", I), "janitor"),
    ("inj-noconfirm", "injection", None, "WARN", R(r"\b(without\s+(asking|confirming|confirmation|approval))\b.{0,80}\b(delete|remove|send|upload|post|execute|run|install)\b|\b(delete|remove|send|upload|post|execute|run|install)\b.{0,80}\bwithout\s+(asking|confirming|confirmation|approval)\b", I | S), "janitor"),
    ("inj-newrole", "injection", "WARN", "WARN", R(r"\byou\s+are\s+no\s+longer\b|\bnew\s+system\s+prompt\b|\boverride\s+(the\s+)?system\s+prompt\b", I), "janitor"),
    ("sh-curlpipe", "remote-exec", "BLOCK", "BLOCK", R(r"\b(curl|wget)\b[^\n|;&]*\|\s*(sudo\s+)?(ba)?sh\b"), "janitor"),
    ("sh-b64exec", "remote-exec", "BLOCK", "BLOCK", R(r"base64\s+(-d|--decode)[^\n]*\|\s*(sudo\s+)?(ba)?sh\b|echo\s+[A-Za-z0-9+/=]{40,}\s*\|\s*base64\s+(-d|--decode)"), "janitor"),
    ("sh-creds", "secret-access", "WARN", "WARN", R(r"(~|\$HOME|/Users/[^/\s]+|/home/[^/\s]+)/(\.ssh/|\.aws/credentials|\.netrc|\.gnupg/)|security\s+find-generic-password|\.config/gh/hosts\.yml", I), "janitor"),
    ("sh-shortener", "unresolved-target", "BLOCK", "WARN", R(r"https?://(bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|cutt\.ly|rb\.gy)/", I), "janitor"),
    ("sh-http", "network", "WARN", None, R(r"\b(curl|wget)\b[^\n]*\bhttp://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)"), "janitor"),
    ("sh-postout", "outbound-data", "WARN", "INFO", R(r"\bcurl\b[^\n]*(-d|--data|--data-binary|-F|--form|-T|--upload-file)[^\n]*\$"), "janitor"),
    ("sh-eval", "dangerous-cmd", "WARN", None, R(r"\beval\s+[\"']?\$"), "janitor"),
    ("sh-history", "secret-access", "WARN", "WARN", R(r"(~|\$HOME)/\.(bash_history|zsh_history|claude/history\.jsonl|claude\.json)\b"), "janitor"),

    # --- инъекции: русский и украинский (наше) ---
    ("inj-ignore-ru", "injection", "WARN", "BLOCK", R(r"(игнорируй|игнорировать|проигнорируй|забудь|отбрось|не\s+обращай\s+внимания\s+на)\s+(все\s+|любые\s+|свои\s+)?(предыдущ\w*|прежн\w*|вышеуказанн\w*|вышеизложенн\w*|системн\w*|исходн\w*|ранее\s+данн\w*)\s+(инструкц\w*|указани\w*|правил\w*|промпт\w*)", I), "ours"),
    ("inj-ignore-uk", "injection", "WARN", "BLOCK", R(r"(ігноруй|ігнорувати|проігноруй|забудь|відкинь|не\s+зважай\s+на)\s+(всі\s+|усі\s+|будь-які\s+|свої\s+)?(попередн\w*|вищезазначен\w*|вищенаведен\w*|системн\w*|початков\w*|раніше\s+надан\w*)\s+(інструкці\w*|вказівк\w*|правил\w*|промпт\w*)", I), "ours"),
    ("inj-ignore-en", "injection", "WARN", "BLOCK", R(r"\b(ignore|disregard|forget|override)\s+(all\s+|any\s+|the\s+|your\s+)*(system|original|developer)\s+(instructions?|prompts?|rules?|guidelines?)", I), "ours"),
    ("inj-conceal-ru", "injection", "WARN", "BLOCK", R(r"\bне\s+(говори|сообщай|рассказывай|упоминай|раскрывай)\s+(об\s+этом\s+|этого\s+|ничего\s+)?(пользовател\w*|человек\w*|оператор\w*)|\b(скрой|скрывай|утаи)\w*\s+[^\n]{0,30}\bот\s+пользовател", I), "ours"),
    ("inj-conceal-uk", "injection", "WARN", "BLOCK", R(r"\bне\s+(кажи|повідомляй|розповідай|згадуй|розкривай)\s+(про\s+це\s+|цього\s+|нічого\s+)?(користувач\w*|людин\w*|оператор\w*)|\b(приховай|приховуй|утаї)\w*\s+[^\n]{0,30}\bвід\s+користувач", I), "ours"),
    ("inj-secrecy-ru", "injection", "WARN", "BLOCK", R(r"\b(тайно|скрытно|незаметно|втихую)\s+(запусти|выполни|отправь|загрузи|установи|удали|скачай|вызови|собери|скопируй|прочитай|перешли)|\bбез\s+ведома\s+пользовател", I), "ours"),
    ("inj-secrecy-uk", "injection", "WARN", "BLOCK", R(r"\b(таємно|приховано|непомітно|потай)\s+(запусти|виконай|надішли|відправ|завантаж|встанови|видали|скачай|виклич|збери|скопіюй|прочитай|перешли)|\bбез\s+відома\s+користувач", I), "ours"),
    ("inj-noconfirm-ru", "injection", None, "WARN", R(r"\bбез\s+(подтверждени\w*|спрос\w*|согласи\w*|разрешени\w*)[^\n]{0,80}\b(удал|отправ|запуст|выполн|установ|опубликуй|запушь|push)\w*|\b(удал|отправ|запуст|выполн|установ|опубликуй|запушь)\w*[^\n]{0,80}\bбез\s+(подтверждени\w*|спрос\w*|согласи\w*|разрешени\w*)|\bне\s+спрашивай\s+(подтверждени|разрешени|согласи)", I), "ours"),
    ("inj-noconfirm-uk", "injection", None, "WARN", R(r"\bбез\s+(підтвердженн\w*|дозвол\w*|згод\w*|запит\w*)[^\n]{0,80}\b(видал|надісл|відправ|запуст|викон|встанов|опублікуй|запуш)\w*|\b(видал|надісл|надішли|відправ|запуст|викон|встанов|опублікуй|запуш)\w*[^\n]{0,80}\bбез\s+(підтвердженн\w*|дозвол\w*|згод\w*|запит\w*)|\bне\s+питай\s+(підтвердженн|дозвол|згод)", I), "ours"),
    ("inj-noconfirm-en2", "injection", None, "WARN", R(r"\b(do\s+not|don't|never)\s+ask\s+(the\s+user\s+)?(for\s+)?(confirmation|permission|approval)", I), "ours"),
    ("inj-newrole-ru", "injection", "WARN", "WARN", R(r"\bты\s+больше\s+не\b|\bнов(ый|ая)\s+системн\w+\s+(промпт|инструкц\w*)|\bпереопредели\s+системн|\bти\s+більше\s+не\b|\bнов(ий|а)\s+системн\w+\s+(промпт|інструкці\w*)", I), "ours"),
    ("inj-exfil-word-ru", "injection", "WARN", "WARN", R(r"эксфильтр|ексфільтр|кейлог", I), "ours"),

    # --- удалённое исполнение (наше, шире janitor) ---
    ("remote-pipe", "remote-exec", "BLOCK", "BLOCK", R(NET_CMD + r"\b[^\n|;&]*\|\s*(sudo\s+(-\S+\s+)*)?(env\s+)?" + SHELLS + r"\b"), "ours"),
    ("remote-subst", "remote-exec", "BLOCK", "BLOCK", R(r"\b((ba|z)?sh|eval|source|python[23]?)\s+(-c\s+)?[\"']?(\$\(|<\(|`)\s*(curl|wget)\b"), "ours"),
    ("remote-iex", "remote-exec", "BLOCK", "BLOCK", R(r"\b(iex|Invoke-Expression)\b[^\n]*\b(iwr|irm|Invoke-WebRequest|Invoke-RestMethod|DownloadString|Net\.WebClient)\b|\b(iwr|irm|Invoke-WebRequest|Invoke-RestMethod|DownloadString)\b[^\n]*\|\s*(iex|Invoke-Expression)\b", I), "ours"),
    ("remote-b64", "remote-exec", "BLOCK", "BLOCK", R(r"\bbase64\s+(-d|-D|--decode)\b[^\n]*\|\s*(sudo\s+)?(ba|z)?sh\b"), "ours"),
    ("decode-exec", "encoded-code", "BLOCK", "BLOCK", R(r"\b(exec|eval)\s*\(\s*(base64\.\w*decode|codecs\.decode|zlib\.decompress|marshal\.loads|bytes\.fromhex|bytearray\.fromhex|atob|Buffer\.from|__import__\(\s*['\"](base64|zlib|codecs))|\bnew\s+Function\s*\(\s*atob|\bexec\s*\(\s*(urllib\.request\.urlopen|requests\.get)\b"), "ours"),
    ("obfuscation", "encoded-code", "WARN", "WARN", R(r"\\x[0-9a-f]{2}(\\x[0-9a-f]{2}){15,}|String\.fromCharCode\((\d+,\s*){10,}|\bchr\(\d+\)\s*\+\s*chr\(\d+\)\s*\+\s*chr\(", I), "ours"),

    # --- опасные команды ---
    ("rm-root", "dangerous-cmd", "BLOCK", "BLOCK", R(r"\brm\s+-(?:[a-zA-Z]*r[a-zA-Z]*f|[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s+(--no-preserve-root\s+)?[\"']?(/|~/?|\$HOME/?|\$\{HOME\}/?|/\*|~/\*|\*)[\"']?(\s|$|;|&|\|)"), "ours"),
    ("disk-wipe", "dangerous-cmd", "BLOCK", "BLOCK", R(r"\bmkfs(\.\w+)?\s+/dev/|\bdd\s+[^\n]*\bof=/dev/(sd|nvme|hd|disk|mmcblk|xvd)|:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:|\bchmod\s+-R\s+777\s+/(\s|$)|>\s*/dev/sd[a-z]\b"), "ours"),
    ("force-push", "dangerous-cmd", "WARN", "WARN", R(r"\bgit\s+push\b[^\n]*(\s--force\b|\s-f\b)"), "ours"),
    ("sudo", "supply-chain", "INFO", "INFO", R(r"\bsudo\s+\w"), "ours"),

    # --- неразрешённая цель, каналы наружу ---
    ("paste-tunnel", "unresolved-target", "BLOCK", "BLOCK", R(r"\b(glot\.io|pastebin\.com|paste\.ee|hastebin\.com|ghostbin|transfer\.sh|webhook\.site|requestbin|pipedream\.net|ngrok(-free)?\.(io|app)|trycloudflare\.com|interact\.sh|oast\.(fun|me|pro|live|site)|burpcollaborator\.net)\b", I), "ours"),
    ("exfil-webhook", "exfil-channel", "WARN", "WARN", R(r"\b(discord(app)?\.com/api/webhooks|api\.telegram\.org/bot|hooks\.slack\.com/services)", I), "ours"),
    ("outbound-py", "outbound-data", "WARN", "INFO", R(r"\brequests\.(post|put|patch)\s*\(|\burllib\.request\.urlopen\s*\([^\n]*data\s*=|\bhttpx\.(post|put)\s*\(|\bfetch\s*\([^\n]*method\s*:\s*['\"](POST|PUT)|\bnc\s+(-\w+\s+)*[\w.-]+\s+\d{2,5}\b|/dev/tcp/|\bwget\s+[^\n]*--post-(data|file)|\bInvoke-RestMethod\b[^\n]*-Method\s+Post", I), "ours"),
    ("secret-file", "secret-access", "WARN", "WARN", R(r"~/\.(ssh|aws|gnupg|kube|docker/config|netrc|npmrc|pypirc)\b|\bid_(rsa|ed25519|ecdsa)\b|\.git-credentials\b|\bLogin Data\b|Cookies\.binarycookies|\bwallet\.dat\b|\.claude/\.credentials\.json|--browser\s+real\b|/Chrome/(Default|Profile)", I), "ours"),
    ("env-secret", "secret-access", "INFO", "INFO", R(r"\bprintenv\b|\benv\s*\|\s*(curl|nc|base64)|\bos\.environ\s*\)|\bdict\(\s*os\.environ\s*\)|\bos\.environ(\.get\(|\[)\s*['\"][A-Z0-9_]*(TOKEN|SECRET|API_KEY|PASSWORD|PASSWD|CREDENTIAL)|\bos\.getenv\(\s*['\"][A-Z0-9_]*(TOKEN|SECRET|API_KEY|PASSWORD)|\bprocess\.env\.[A-Z0-9_]*(TOKEN|SECRET|API_KEY|PASSWORD)|\$\{?[A-Z0-9_]*(TOKEN|SECRET|API_KEY|PASSWORD)\b"), "ours"),

    # --- права харнесса ---
    ("bypass-perms", "permissions", "BLOCK", "WARN", R(r"bypassPermissions|--dangerously-skip-permissions|--permission-mode\s+bypass", I), "ours"),
    ("broad-allow", "permissions", "WARN", "INFO", R(r"\"allow\"\s*:\s*\[[^\]]*\"Bash\"|\bBash\(\s*\*\s*\)|\bBash\(\s*(ba|z)?sh\s*:\s*\*\s*\)"), "ours"),

    # --- социальная инженерия ---
    ("zip-password", "social-engineering", "BLOCK", "BLOCK", R(r"\.(zip|7z|rar)\b[^\n]{0,200}\b(pass(word)?|пароль|парол\w+)\b\s*[:=`'\"«]", I), "ours"),
    ("download-run", "social-engineering", "WARN", "WARN", R(r"\b(download|скачай|скачайте|завантаж\w*)\b[^\n]{0,120}\.(exe|dmg|pkg|msi|scr|bat|apk)\b", I), "ours"),
    ("paste-terminal", "social-engineering", "WARN", "WARN", R(r"\b(copy|paste|скопируй|вставь|скопіюй|встав)\w*\b[^\n]{0,80}\b(terminal|терминал\w*|термінал\w*)", I), "ours"),

    # --- цепочка поставки, телеметрия (справочно) ---
    ("unpinned", "supply-chain", "INFO", "INFO", R(r"@latest\b|\bnpx\s+(-y|--yes)\b|\bpip3?\s+install\s+(?![^\n]*(==|-r\s|-e\s|\.\s*$))[A-Za-z]|--break-system-packages|\bgit\s+clone\b(?![^\n]*(--branch\s+v?\d|@[0-9a-f]{7,}|&&\s*git\s+checkout))"), "ours"),
    ("telemetry", "telemetry", "INFO", "INFO", R(r"\b(posthog|sentry_sdk|@sentry/|mixpanel|segment\.(io|com)|amplitude|analytics\.track)\b", I), "ours"),
]

BARE_IP_URL = R(r"\bhttps?://(\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?")
URL = R(r"https?://[^\s\"'<>)\]`|\\]+")

# Скрытые символы. Tag-символы U+E0000-E007F (кроме флагов-эмодзи U+1F3F4 +
# теги), bidi-управление, zero-width. ZWJ/ZWNJ считаем скрытыми только между
# ASCII (как в janitor), BOM в начале файла — норма.
TAG_RUN = R("[\U000E0000-\U000E007F]+")
BIDI = R("[‪-‮⁦-⁩]")
ZERO_WIDTH = R("[​‎‏⁠-⁤﻿]")
ZWJ_ASCII = R("[\x20-\x7e][‌‍]+[\x20-\x7e]")

B64_BLOB = R(r"(?<![A-Za-z0-9+/_-])[A-Za-z0-9+/]{40,}={0,2}(?![A-Za-z0-9+/_-])")
HEX_BLOB = R(r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}){40,}(?![0-9A-Fa-f])")
CODE_TOKENS = R(r"\b(import|exec|eval|system|subprocess|curl|wget|bash|powershell|require|socket|http|base64|chmod|ssh|token|password)\b", I)
HTML_COMMENT = R(r"<!--(.*?)-->", S)
HTML_IMPERATIVE = R(r"\b(curl|wget|send\s+to|upload|post\s+to|do\s+not\s+(tell|mention|inform)|ignore\s+(all|previous|prior)|delete\s+(all|the\s+user)|игнориру|ігнору|не\s+(говори|сообщай|кажи|повідомляй)|отправ|надішли|запусти|выполни|виконай)", I)

# Контекст, в котором опасное только перечислено (урок darwin-skill).
FORBID = R(r"(никаких|никогда|нельзя|запрещ\w*|не\s+(запускай|выполняй|используй|делай|пиши|ставь)|жодн\w*|ніколи|заборон\w*|не\s+(запускай|виконуй|використовуй|роби|пиши|став)|\bnever\b|\bavoid\b|\bdo\s+not\b|\bdon't\b|\bmust\s+not\b|\bforbid\w*|\bno\s+`)", I)
DOC_VOCAB = R(r"(?<![\w./-])(пример\w*|приклад\w*|шаблон\w*|паттерн\w*|ловит|ловить|ловят|признак\w*|ознак\w*|атак\w*|инъекц\w*|ін.єкц\w*|injection\w*|example\w*|patterns?|detects?|catch(es)?|attack\w*|red\s+flags?|красн\w+\s+флаг\w*|правил[оа]|regex\w*|регуляр\w*|класс\w*\s+наход|сигнатур\w*|вредонос\w*|шкідлив\w*|malicious|phrases?|фраз\w*)(?![\w.-])", I)
NEGATED_CONFIRM = R(r"\b(no|never|not|nothing|don't|do\s+not)\b[^\n]{0,60}\bwithout\b|(^|[\s(«\"*])(не|нічого|ничего|ніколи|никогда)\s[^\n]{0,60}\sбез\s", I)
NEG_AFTER = R(r"^[\s,;:—-]*(\S+\s+){0,2}?(не|ні|not|never|нельзя|нікол\w*|никогда)\b", I)
QUOTED = R("«[^»\n]*»|“[^”\n]*”|„[^“”\n]*[“”]|\"[^\"\n]*\"|`[^`\n]*`")
PATTERN_LITERAL = R(r"re\.compile|\bR\(r?[\"']|\br[\"']|RegExp\(|new\s+RegExp|\bgrep\s+(-\w*[EP]|-e)|\brg\s|PATTERN|RULES|\(\?[imsx]+\)|\\b|\\s[+*]")
COMMENT_LINE = R(r"^\s*(#|//|--|;|\*|/\*|<!--|REM\s)", I)
REF_FILE = R(r"(^|/)(references?|docs?|knowledge|guides?)/|(checklist|patterns?|rules|threats?|attacks?|security|red-?flags|injection)[\w-]*\.(md|txt)$", I)

# Сеть и запись в коде (для хуков и «заявления против поведения»)
NET_CODE = R(r"\b(curl|wget|ncat|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b|\bnc\s+-|/dev/tcp/|\b(requests|httpx|aiohttp|urllib3?|http\.client|socket|ftplib|smtplib|paramiko)\b\s*[.(]|\burllib\.request\b|\burlopen\s*\(|\bfetch\s*\(|\baxios\b|\bXMLHttpRequest\b|\bWebSocket\s*\(|\bgh\s+api\b|\bgit\s+(push|fetch|clone|pull)\b|\bhttps?://(?!localhost|127\.0\.0\.1)", I)
WRITE_CODE = R(r"\bopen\s*\([^)\n]*,\s*['\"][wax]b?\+?['\"]|\.write_(text|bytes)\s*\(|\bshutil\.(rmtree|move|copy\w*)\s*\(|\bos\.(remove|unlink|rename|replace|makedirs|mkdir|rmdir)\s*\(|\.(mkdir|unlink|rmdir|touch)\s*\(|\bfs\.(writeFile\w*|appendFile\w*|unlink\w*|rm\w*|mkdir\w*)\s*\(|\bgit\s+(commit|push|add|reset|checkout\s+--)\b|\b(rm|mv|cp|tee|touch|mkdir)\s+-?\w|\bsed\s+-i\b")
SHELL_REDIRECT = R(r"(?<![0-9&<>=-])>>?\s*(?!&|/dev/null)[\"']?(\$\{?\w+|~/|/|\./|[\w-]+(\.\w+|/))")
STRIP_QUOTED = R(r"\"[^\"\n]*\"|'[^'\n]*'")
CLAIM_READONLY = R(r"read[- ]only|только\s+(чтени\w*|чита\w*)|лише\s+(читанн\w*|чита\w*)|тільки\s+(читанн\w*|чита\w*)|ничего\s+не\s+(меняет|изменяет|пишет|записывает)|нічого\s+не\s+(змінює|пише|записує)|does\s+not\s+(modify|write|change)|never\s+(modifies|writes)|no\s+writes|без\s+записи|без\s+запису|код\s+не\s+меняет|код\s+не\s+змінює", I)
CLAIM_NONET = R(r"\bno\s+network\b|without\s+(network|internet)|\boffline\b|does\s+not\s+(make|send|use)\s+(any\s+)?(network|http|internet)|без\s+сети|без\s+мережі|без\s+інтернету|без\s+интернета|в\s+сеть\s+не\s+ходит|не\s+ходит\s+в\s+сеть|у?\s*мережу\s+не\s+ходить|не\s+ходить\s+у\s+мережу|no\s+external\s+(calls|requests)", I)

# Frontmatter и lint
NAME_OK = R(r"^[a-z0-9][a-z0-9-]{0,63}$")
XML_TAG = R(r"<\s*/?\s*[A-Za-z][\w:-]*(\s[^<>]*)?/?\s*>")
NEGATIVE_BOUNDARY = R(r"\bНЕ\s|\bне\s+(для|використов\w*|используй|запускай|підходить|подходит|застосов\w*)|\bnot\s+for\b|\bdo\s+not\s+use\b|\bdon't\s+use\b|\bnot\s+(when|to\s+be\s+used)\b", I)
BROAD_DESC = R(r"\b(always\s+use|use\s+(this\s+)?(for\s+)?(any|every|all)\s+(task|request|session)|proactively|in\s+all\s+cases|всегда\s+используй|в\s+любой\s+(задаче|сессии)|для\s+любой\s+задачи|завжди\s+використовуй|у\s+будь-якій\s+(задачі|сесії)|для\s+будь-якої\s+задачі)", I)
BROAD_TOOLS = R(r"^(Bash|Bash\(\s*\*?\s*\)|Bash\(\s*((ba|z)?sh|python[23]?|node|bash\s+-c|eval|curl|wget)\s*:?\s*\*?\s*\)|\*)$", I)

# Дубли триггеров: Unicode-слова, стем 6 букв (замер catalog/skills-janitor/measure.py)
STOP = set("""use when the user wants to or and a an this skill also that for with in on of is are it be as at by from not
any into your you can will should only use used using via e.g. etc
і й та або в у на з із до для що як це не коли щойно якщо чи по за від при його її їх ще вже лише тільки також цей ця ці
и или с из для что как это не когда если по при его ее их уже только также этот эта эти""".split())
STOP_STEMS = {"скіл", "скил", "тригер", "тригерн", "запуск", "викори", "исполь", "резуль", "фраза", "фрази", "фразы",
              "trigge", "phrase", "result", "запуск", "робить", "делает", "потріб", "нужно", "файл", "file",
              "напиши", "зроби", "сделай", "наприк", "наприм", "наприклад", "результ"}
QUOTE_PHRASE = R(r"«([^»]{4,80})»|“([^”]{4,80})”|\"([^\"]{4,80})\"")


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------
def is_private_ip(ip: str) -> bool:
    try:
        a, b, *_ = (int(x) for x in ip.split("."))
    except ValueError:
        return True
    return (a in (0, 10, 127) or (a == 169 and b == 254) or (a == 172 and 16 <= b <= 31)
            or (a == 192 and b == 168) or a >= 224)


def in_quotes(line: str, start: int, end: int) -> bool:
    return any(q.start() <= start and end <= q.end() for q in QUOTED.finditer(line))


def file_kind(rel: str, text: str) -> str:
    p = Path(rel)
    ext = p.suffix.lower()
    if ext in INSTR_EXT:
        return "instr"
    if ext in CODE_EXT or text.startswith("#!"):
        return "code"
    return "config"


def parse_frontmatter(text: str):
    """Минимальный YAML-разбор frontmatter: строки, кавычки, блочные скаляры
    (|, >, |-, >-, |2), простые списки. CRLF допускается. Возвращает
    (dict | None, номер строки конца frontmatter)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return None, 0
    data: dict = {}
    i = 1
    while i < end:
        ln = lines[i]
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).rstrip()
        i += 1
        if re.match(r"^[|>][+-]?\d*\s*(#.*)?$", val):
            folded = val.startswith(">")
            block = []
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            while block and not block[-1]:
                block.pop()
            data[key] = (" ".join(b for b in block if b) if folded else "\n".join(block))
        elif val == "":
            items, cont = [], []
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                s = lines[i].strip()
                if s.startswith("- "):
                    items.append(s[2:].strip().strip("'\""))
                elif s:
                    cont.append(s)
                i += 1
            data[key] = items if items else " ".join(cont)
        else:
            if val[:1] in "\"'":
                q = val[0]
                buf = val
                while (len(buf) < 2 or not buf.rstrip().endswith(q) or buf.rstrip().endswith("\\" + q) and q == '"') and i < end:
                    buf += " " + lines[i].strip()
                    i += 1
                buf = buf.strip()
                inner = buf[1:-1] if buf.endswith(q) and len(buf) >= 2 else buf[1:]
                data[key] = inner.replace("''", "'") if q == "'" else inner.replace('\\"', '"')
            elif val.startswith("["):
                data[key] = [x.strip().strip("'\"") for x in val.strip("[]").split(",") if x.strip()]
            else:
                cont = [val]
                while i < end and lines[i].startswith((" ", "\t")) and not re.match(r"^\s*[\w-]+\s*:", lines[i]):
                    cont.append(lines[i].strip())
                    i += 1
                data[key] = " ".join(cont)
    return data, end + 1


def tools_list(v) -> list[str]:
    if isinstance(v, list):
        return [x.strip() for x in v if x.strip()]
    if not isinstance(v, str):
        return []
    out, depth, cur = [], 0, ""
    for ch in v:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and ch in ", ":
            if cur.strip():
                out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def keywords(desc: str) -> set[str]:
    out = set()
    for w in re.findall(r"[^\W\d_]+", desc.lower().replace("ʼ", "").replace("'", "")):
        if w in STOP or len(w) <= 2:
            continue
        st = w[:6]
        if st in STOP_STEMS or w in STOP_STEMS:
            continue
        out.add(st)
    return out


def phrases(desc: str) -> set[str]:
    out = set()
    for m in QUOTE_PHRASE.finditer(desc):
        p = next(g for g in m.groups() if g)
        p = re.sub(r"\s*\[[^\]]*\]\s*", " ", p.lower().replace("ʼ", "'"))
        p = re.sub(r"\s+", " ", p).strip(" .,;:!?")
        if len(p.split()) >= 2:
            out.add(p)
    return out


# ---------------------------------------------------------------------------
# Сканер
# ---------------------------------------------------------------------------
class Scanner:
    def __init__(self, excludes: set[str]):
        self.excludes = excludes | {".git"}
        self.findings: list[Finding] = []
        self.surfaces: list[tuple[str, str]] = []
        self.hosts: dict[str, str] = {}
        self.unread: list[str] = []
        self.skills: list[dict] = []
        self.files = 0
        self.texts: dict[str, str] = {}      # rel -> text (для хуков и заявлений)
        self.root_of: dict[str, Path] = {}

    # -- общий учёт --
    def add(self, level, cls, rule, rel, line, text, note=""):
        self.findings.append(Finding(level, cls, rule, rel, line, text.strip()[:180], note))

    def walk(self, root: Path):
        for cur, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in self.excludes)
            for name in sorted(files):
                yield Path(cur, name)

    # -- по строкам --
    def adjust(self, level, kind, rel, line, m, ctx):
        """Понижение уровня там, где опасное только перечислено или запрещено."""
        if level == "INFO":
            return level, ""
        start, end = m.start(), m.end()
        if kind == "instr":
            if "\\|" in m.group(0):
                return "INFO", "перечисление в таблице (экранированный |)"
            forbid = FORBID.search(line[:start])
            quoted = in_quotes(line, start, end)
            doc = DOC_VOCAB.search(line) or DOC_VOCAB.search(ctx)
            if forbid and quoted:
                return "INFO", "упомянуто как запрещённое"
            if forbid or (quoted and doc):
                return ("WARN" if level == "BLOCK" else "INFO"), "запрет/перечисление рядом"
            if quoted or doc:
                level, note = DOWN[level] if level == "BLOCK" else level, "в кавычках или в описании шаблонов"
                if REF_FILE.search(rel) and level == "BLOCK":
                    level = "WARN"
                return level, note
            if REF_FILE.search(rel) and level == "BLOCK":
                return "WARN", "справочный файл"
            return level, ""
        # код и конфиги
        if PATTERN_LITERAL.search(line) and (in_quotes(line, start, end) or "r\"" in line or "r'" in line):
            return "INFO", "шаблон внутри строки/регулярки (похоже на сканер)"
        if COMMENT_LINE.search(line):
            if FORBID.search(line[:start]):
                return "INFO", "комментарий-запрет"
            return DOWN[level] if level == "BLOCK" else level, "в комментарии"
        return level, ""

    def scan_lines(self, rel, text, kind, origin="", base_line=0):
        lines = text.splitlines()
        hits = []
        for i, line in enumerate(lines, 1):
            lineno = base_line or i
            if len(line) > 5000:
                line = line[:5000]
            ctx = " ".join(lines[max(0, i - 4):i - 1])
            for rule, cls, lv_code, lv_instr, rx, src in LINE_RULES:
                level = lv_instr if kind == "instr" else lv_code
                if level is None:
                    continue
                m = rx.search(line)
                if not m:
                    continue
                if cls == "injection" and rule.startswith("inj-noconfirm") and NEGATED_CONFIRM.search(line):
                    continue
                if cls == "injection" and rule.startswith(("inj-secrecy", "inj-noconfirm")) and NEG_AFTER.search(line[m.end():m.end() + 30]):
                    continue    # «без ведома пользователя не коммить» — защита
                level, note = self.adjust(level, kind, rel, line, m, ctx)
                if origin:
                    level, note = (lv_code or level), "внутри закодированного блока"
                hits.append((cls, level))
                self.add(level, cls, rule + (f" [{src}]" if src == "janitor" else ""), rel, lineno, origin + line, note)
            for m in BARE_IP_URL.finditer(line):
                if not is_private_ip(m.group(1)):
                    level, note = self.adjust("BLOCK", kind, rel, line, m, ctx)
                    hits.append(("unresolved-target", level))
                    self.add(level, "unresolved-target", "bare-ip-url", rel, lineno, origin + line, note)
            self.hidden_chars(rel, lineno, line, kind, first=(i == 1))
            if not origin:
                self.encoded(rel, lineno, line, kind, text)
        return hits

    def hidden_chars(self, rel, lineno, line, kind, first=False):
        for m in TAG_RUN.finditer(line):
            pre = line[max(0, m.start() - 2):m.start()]
            if "\U0001F3F4" in pre:           # флаг-эмодзи региона
                continue
            hidden = "".join(chr(ord(c) - 0xE0000) for c in m.group(0) if 0x20 <= ord(c) - 0xE0000 < 0x7F)
            self.add("BLOCK", "hidden-text", "unicode-tags", rel, lineno,
                     f"tag-символы U+E00xx, скрытый текст: {hidden[:120]!r}")
            if hidden:
                self.scan_lines(rel, hidden, "instr", origin="[из tag-символов] ", base_line=lineno)
        if BIDI.search(line):
            self.add("BLOCK" if kind == "code" else "WARN", "hidden-text", "unicode-bidi", rel, lineno,
                     "bidi-управление (Trojan Source): " + repr(line.strip()[:80]))
        zw = ZERO_WIDTH.search(line)
        if zw and not (first and zw.start() == 0 and zw.group(0) == "﻿"):
            self.add("WARN", "hidden-text", "unicode-zero-width [janitor+]", rel, lineno, "zero-width: " + repr(line.strip()[:80]))
        elif ZWJ_ASCII.search(line):
            self.add("WARN", "hidden-text", "unicode-zwj-ascii [janitor]", rel, lineno, "ZWJ/ZWNJ между ASCII: " + repr(line.strip()[:80]))

    def encoded(self, rel, lineno, line, kind, text):
        cands = [("base64", b) for b in B64_BLOB.findall(line)] + [("hex", h) for h in HEX_BLOB.findall(line)]
        for enc, blob in cands:
            if enc == "base64" and (len(blob) < (40 if kind == "code" else 80) or re.fullmatch(r"[A-Za-z]+|[0-9a-fA-F]+|[A-Za-z0-9]*/[A-Za-z0-9/]*", blob) and "/" in blob and blob.count("/") > 3):
                continue
            try:
                raw = (base64.b64decode(blob + "=" * (-len(blob) % 4), validate=True) if enc == "base64" else bytes.fromhex(blob))
                dec = raw.decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError):
                continue
            if sum(ch.isprintable() or ch in "\n\t\r" for ch in dec) / max(1, len(dec)) < 0.9:
                continue
            if not CODE_TOKENS.search(dec):
                self.add("INFO", "encoded-code", f"{enc}-text", rel, lineno, f"{enc} → {dec[:100]}")
                continue
            m = re.search(r"\b([A-Za-z_]\w*)\s*[:=]\s*[bru]?[\"']" + re.escape(blob[:20]), line)
            dead = bool(m) and len(re.findall(r"\b" + re.escape(m.group(1)) + r"\b", text)) == 1
            self.add("WARN", "encoded-code", f"{enc}-code", rel, lineno,
                     f"{enc} → {dec[:120]}", "не используется в файле (мёртвый код)" if dead else "")
            self.scan_lines(rel, dec, "code", origin=f"[из {enc}] ", base_line=lineno)

    # -- файл целиком --
    def scan_file(self, root: Path, path: Path):
        rel = path.relative_to(root).as_posix()
        label = (root.name + "/" + rel) if self.multi else rel
        self.files += 1
        parts = set(rel.split("/")[:-1])
        if parts & SKIPPED_ELSEWHERE:
            self.add("INFO", "inventory", "skipped-dir", label, 0, "папка, которую многие сканеры пропускают: прочитано")
        if path.is_symlink():
            tgt = os.path.realpath(path)
            inside = tgt.startswith(str(root.resolve()) + os.sep)
            self.add("INFO" if inside else "WARN", "inventory", "symlink", label, 0, f"симлинк → {tgt}")
            return
        ext = path.suffix.lower()
        if ext in BINARY_EXT:
            self.add("WARN", "opaque-binary", "binary", label, 0, "бинарь/архив: прочитать нельзя; сверить с исходниками или не ставить")
            return
        if ext in MEDIA_EXT or ext in OFFICE_EXT:
            return
        try:
            data = path.read_bytes()
        except OSError as exc:
            self.unread.append(f"{label}: {exc}")
            return
        if len(data) > MAX_BYTES or b"\0" in data[:4096]:
            self.unread.append(f"{label}: двоичный или больше {MAX_BYTES} байт")
            return
        text = data.decode("utf-8", errors="replace")
        kind = file_kind(rel, text)
        self.texts[label] = text
        self.root_of[label] = root
        if os.access(path, os.X_OK) and not ext and not text.startswith("#!"):
            self.add("INFO", "inventory", "exec-no-ext", label, 0, "исполняемый файл без расширения")
        self.surface(label, rel)
        hits = self.scan_lines(label, text, kind)
        self.exfil(label, kind, hits)
        if kind == "instr":
            for m in HTML_COMMENT.finditer(text):
                body = m.group(1).strip()
                if len(body) > 20 and HTML_IMPERATIVE.search(body):
                    self.add("WARN", "hidden-text", "md-htmlcomment [janitor+]", label,
                             text.count("\n", 0, m.start()) + 1, "HTML-комментарий с указанием: " + body[:140])
        if path.name == "package.json":
            self.package_json(label, text)
        for url in URL.findall(text):
            host = url.split("/")[2].lower().split("@")[-1].split(":")[0]
            self.hosts.setdefault(host, label)
        if path.name == "SKILL.md":
            self.skill(root, path, label, text)
        elif kind == "instr" and ("/agents/" in "/" + rel or "/commands/" in "/" + rel):
            fm, _ = parse_frontmatter(text)
            if fm:
                self.tools_check(label, fm.get("allowed-tools") or fm.get("tools"))

    def surface(self, label, rel):
        checks = [
            (r"(^|/)hooks/[^/]*\.json$|(^|/)\.claude/settings(\.local)?\.json$|(^|/)settings(\.local)?\.json$", "hooks/settings: исполняется харнессом без вызова скилла"),
            (r"(^|/)\.mcp\.json$", "MCP: процесс или сеть при старте сессии"),
            (r"(^|/)\.claude-plugin/(plugin|marketplace)\.json$", "манифест: hooks, mcpServers, источники"),
            (r"(^|/)package\.json$", "package.json: (pre|post)install при установке"),
            (r"(^|/)(setup\.py|pyproject\.toml|Makefile|install\.sh|setup\.sh|postinstall\.\w+)$", "установщик/сборка"),
            (r"(^|/)(statusline|status-line)[^/]*$", "statusline: исполняется харнессом"),
        ]
        for rx, why in checks:
            if re.search(rx, rel):
                self.surfaces.append((label, why))

    def exfil(self, label, kind, hits):
        eff = {(c) for c, lv in hits if lv in ("BLOCK", "WARN") or c == "secret-access" and lv == "INFO" and kind == "code"}
        secret = "secret-access" in eff
        channel = eff & {"outbound-data", "exfil-channel", "unresolved-target"}
        if secret and channel:
            self.add("BLOCK", "exfiltration", "secret+channel", label, 0,
                     "в одном файле чтение секрета и канал наружу: " + ", ".join(sorted(channel)))

    def package_json(self, label, text):
        try:
            scripts = json.loads(text).get("scripts", {}) or {}
        except (ValueError, AttributeError):
            return
        for k, v in scripts.items():
            if k in ("preinstall", "install", "postinstall", "prepare", "prepublish"):
                lv = "BLOCK" if NET_CODE.search(str(v)) else "WARN"
                self.add(lv, "install-hook", "npm-" + k, label, 0, f"{k}: {v}")

    # -- скиллы: lint, права, заявления --
    def skill(self, root, path, label, text):
        fm, body_start = parse_frontmatter(text)
        d = path.parent
        rec = {"label": label, "dir": str(d.resolve()), "root": str(root), "plugin": plugin_name(root, d),
               "name": d.name, "description": "", "file": label}
        if fm is None:
            self.add("WARN", "lint", "no-frontmatter", label, 1, "нет frontmatter --- … ---")
            self.skills.append(rec)
            return
        name = str(fm.get("name") or "")
        desc = fm.get("description") or ""
        desc = desc if isinstance(desc, str) else " ".join(desc)
        wtu = fm.get("when_to_use") or ""
        wtu = wtu if isinstance(wtu, str) else " ".join(wtu)
        rec.update(name=name or d.name, description=(desc + " " + wtu).strip())
        self.skills.append(rec)
        if not name:
            self.add("WARN", "lint", "no-name", label, 1, "нет name")
        else:
            if not NAME_OK.match(name):
                self.add("WARN", "lint", "name-format", label, 1, f"name «{name}»: нужны a-z, 0-9, дефис, до 64")
            if name != d.name:
                self.add("WARN", "lint", "name-dir", label, 1, f"name «{name}» ≠ папка «{d.name}»")
            if re.search(r"anthropic|claude", name, I):
                self.add("WARN", "lint", "name-reserved", label, 1, f"в name зарезервированное слово: {name}")
        if not desc.strip():
            self.add("WARN", "lint", "no-description", label, 1, "нет description")
        else:
            total = len(desc) + len(wtu)
            if total > DESC_LIMIT:
                self.add("WARN", "lint", "desc-length", label, 1, f"description+when_to_use = {total} > {DESC_LIMIT}: обрежется в листинге")
            elif len(desc) > SPEC_DESC_LIMIT:
                self.add("INFO", "lint", "desc-spec-length", label, 1, f"description = {len(desc)} > {SPEC_DESC_LIMIT} (лимит открытой спецификации Agent Skills)")
            t = XML_TAG.search(desc + " " + wtu)
            if t:
                self.add("WARN", "lint", "desc-xml", label, 1, f"XML-тег в description: {t.group(0)} (claude.ai предупреждает при синке)")
            if not NEGATIVE_BOUNDARY.search(desc + " " + wtu):
                self.add("INFO", "lint", "no-negative-boundary", label, 1, "нет границы «НЕ для…» / «Not for…»")
            b = BROAD_DESC.search(desc)
            if b:
                self.add("WARN", "broad-trigger", "broad-description", label, 1, "широкий триггер: " + b.group(0))
        self.tools_check(label, fm.get("allowed-tools"))
        claims_text = text + "\n" + read_text(d / "README.md")
        self.claims(d, label, claims_text, tools_list(fm.get("allowed-tools")))

    def tools_check(self, label, value):
        tools = tools_list(value)
        if not tools:
            return
        broad = [t for t in tools if BROAD_TOOLS.match(t)]
        if broad:
            self.add("WARN", "permissions", "allowed-tools-broad", label, 1, "allowed-tools без сужения: " + ", ".join(broad))
        else:
            self.add("INFO", "permissions", "allowed-tools", label, 1, "allowed-tools: " + ", ".join(tools))

    def claims(self, scope: Path, label, claims_text, tools):
        ro = CLAIM_READONLY.search(claims_text)
        nonet = CLAIM_NONET.search(claims_text)
        if not (ro or nonet):
            return
        scope_s = str(scope.resolve()) + os.sep
        for other, txt in self.pending_code(scope_s):
            if set(Path(other).parts[:-1]) & TEST_DIRS:
                continue    # тесты и фикстуры — не поведение плагина
            kind = file_kind(other, txt)
            if kind != "code":
                continue
            shell = Path(other).suffix.lower() in SHELL_EXT or txt.startswith("#!/bin/") or txt.startswith("#!/usr/bin/env bash")
            code_lines = [ln for ln in txt.splitlines() if not COMMENT_LINE.search(ln)]
            joined = "\n".join(code_lines)
            if nonet:
                m = NET_CODE.search(joined)
                if m:
                    self.add("BLOCK", "claim-vs-behavior", "claims-no-network", label, 0,
                             f"заявлено «{nonet.group(0)}», а в {other} сеть: {m.group(0)}")
            if ro:
                m = WRITE_CODE.search(joined) or (SHELL_REDIRECT.search(STRIP_QUOTED.sub('""', joined)) if shell else None)
                if m:
                    self.add("WARN", "claim-vs-behavior", "claims-read-only", label, 0,
                             f"заявлено «{ro.group(0)}», а в {other} запись: {m.group(0).strip()}")
        if ro and any(t.split("(")[0] in ("Write", "Edit", "NotebookEdit", "MultiEdit") for t in tools):
            self.add("WARN", "claim-vs-behavior", "claims-read-only-tools", label, 1, f"заявлено «{ro.group(0)}», а allowed-tools дают запись")
        if nonet and any(t.split("(")[0] in ("WebFetch", "WebSearch") for t in tools):
            self.add("WARN", "claim-vs-behavior", "claims-no-network-tools", label, 1, f"заявлено «{nonet.group(0)}», а allowed-tools дают сеть")

    def plugin_claims(self, root: Path):
        """Заявления плагина: description в plugin.json и README вне таблиц.
        Строка таблицы README вида «| `скилл` | … |» относится к этому скиллу."""
        pj = root / ".claude-plugin" / "plugin.json"
        if not pj.exists():
            return
        label = (root.name + "/README.md") if self.multi else "README.md"
        try:
            general = str(json.loads(read_text(pj)).get("description", ""))
        except ValueError:
            general = ""
        for ln in read_text(root / "README.md").splitlines():
            m = re.match(r"^\|\s*`([a-z0-9-]+)`\s*\|", ln)
            if m:
                for d in (root / "skills" / m.group(1), root / m.group(1)):
                    if (d / "SKILL.md").exists():
                        self.claims(d, label, ln, [])
                        break
            elif not ln.lstrip().startswith("|"):
                general += "\n" + ln
        self.claims(root, label, general, [])

    def pending_code(self, scope_s):
        """Код в папке скилла; читается с диска (скилл сканируется раньше
        своих scripts/ из-за порядка обхода)."""
        for cur, dirs, files in os.walk(scope_s, followlinks=False):
            dirs[:] = sorted(x for x in dirs if x not in self.excludes)
            for f in sorted(files):
                p = Path(cur, f)
                if p.suffix.lower() in BINARY_EXT | MEDIA_EXT | OFFICE_EXT or p.is_symlink():
                    continue
                txt = read_text(p)
                if txt:
                    yield os.path.relpath(p, scope_s), txt

    # -- хуки и MCP --
    def configs(self, root: Path):
        for label, text in list(self.texts.items()):
            if self.root_of.get(label) != root:
                continue
            rel = label.split("/", 1)[1] if self.multi else label
            base = Path(rel).name
            if not base.endswith(".json"):
                continue
            try:
                data = json.loads(text)
            except ValueError:
                if re.search(r"(^|/)(hooks/[^/]*|\.mcp|plugin|settings(\.local)?)\.json$", rel):
                    self.add("WARN", "inventory", "bad-json", label, 0, "JSON не разбирается: харнесс может прочитать иначе")
                continue
            if not isinstance(data, dict):
                continue
            plugin_dir = root / Path(rel).parent
            if Path(rel).parent.name in (".claude-plugin", "hooks", ".claude"):
                plugin_dir = plugin_dir.parent
            if "hooks" in data and (base in ("hooks.json", "plugin.json") or base.startswith("settings")):
                h = data["hooks"]
                if isinstance(h, str):
                    hp = (plugin_dir / h).resolve()
                    self.add("INFO", "hooks", "hooks-path", label, 0, f"hooks → {h}")
                    try:
                        h = json.loads(hp.read_text(encoding="utf-8")).get("hooks", {})
                    except (OSError, ValueError, AttributeError):
                        h = {}
                self.hooks(label, h, plugin_dir)
            if base == ".mcp.json" or "mcpServers" in data:
                servers = data.get("mcpServers", data if base == ".mcp.json" else {})
                if isinstance(servers, str):
                    self.add("INFO", "mcp", "mcp-path", label, 0, f"mcpServers → {servers}")
                    try:
                        servers = json.loads((plugin_dir / servers).read_text(encoding="utf-8"))
                        servers = servers.get("mcpServers", servers)
                    except (OSError, ValueError, AttributeError):
                        servers = {}
                self.mcp(label, servers)
            if base == "plugin.json":
                for k in ("commands", "agents", "skills", "outputStyles", "lspServers"):
                    if k in data:
                        self.add("INFO", "inventory", "manifest-" + k, label, 0, f"{k}: {json.dumps(data[k], ensure_ascii=False)[:120]}")

    def hooks(self, label, hooks, plugin_dir: Path):
        if not isinstance(hooks, dict):
            return
        for event, groups in hooks.items():
            for g in groups if isinstance(groups, list) else []:
                if not isinstance(g, dict):
                    continue
                matcher = g.get("matcher", "")
                for h in g.get("hooks", []) if isinstance(g.get("hooks"), list) else []:
                    if not isinstance(h, dict):
                        continue
                    typ = h.get("type", "command")
                    cmd = str(h.get("command") or h.get("url") or h.get("prompt") or "")
                    self.add("INFO", "hooks", "hook", label, 0, f"{event}[{matcher or '*'}] {typ}: {cmd[:120]}")
                    if typ == "http" or h.get("url"):
                        self.add("BLOCK", "hooks", "hook-network", label, 0, f"{event}: HTTP-хук → {cmd[:100]}")
                        continue
                    if typ != "command":
                        continue
                    m = NET_CODE.search(cmd)
                    if m:
                        self.add("BLOCK", "hooks", "hook-network", label, 0, f"{event}: сеть в команде хука: {m.group(0)}")
                    for ref in re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([^\s\"']+)|(?<![\w/$])((?:\./)?[\w.-]+/[\w./-]+\.(?:sh|py|js|mjs|ts|rb|pl|ps1))", cmd):
                        rp = next(x for x in ref if x)
                        sp = (plugin_dir / rp).resolve()
                        txt = read_text(sp)
                        if not sp.exists():
                            self.add("WARN", "hooks", "hook-missing-script", label, 0, f"{event}: скрипт не найден: {rp}")
                            continue
                        code = "\n".join(ln for ln in txt.splitlines() if not COMMENT_LINE.search(ln))
                        m = NET_CODE.search(code)
                        if m:
                            self.add("BLOCK", "hooks", "hook-network", label, 0, f"{event}: сеть в скрипте хука {rp}: {m.group(0)}")
                    if event in ("UserPromptSubmit", "PreToolUse", "PostToolUse", "SessionStart") and not matcher:
                        self.add("INFO", "hooks", "hook-every", label, 0, f"{event} без matcher: срабатывает на каждое событие")

    def mcp(self, label, servers):
        if not isinstance(servers, dict):
            return
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            cmd = " ".join([str(cfg.get("command", ""))] + [str(a) for a in cfg.get("args", []) or []]).strip()
            url = str(cfg.get("url", ""))
            self.add("INFO", "mcp", "mcp-server", label, 0, f"{name}: {cmd or url} ({cfg.get('type', 'stdio')})")
            if re.search(r"@latest\b|\bnpx\s+(-y|--yes)\s+(?!\S+@\d)\S+|\buvx\s+(?!\S+[@=]=?\d)\S+|\bpip3?\s+install\b(?![^\n]*==)|docker\s+run\b(?![^\n]*@sha256)", cmd):
                self.add("WARN", "mcp", "mcp-unpinned", label, 0, f"{name}: версия не закреплена: {cmd[:120]}")
            if url and not re.match(r"https?://(localhost|127\.0\.0\.1)", url):
                self.add("WARN", "mcp", "mcp-remote", label, 0, f"{name}: удалённый сервер {url[:100]}: данные уходят наружу")
            env = cfg.get("env") or {}
            if isinstance(env, dict) and any(re.search(r"TOKEN|SECRET|KEY|PASSWORD", k) for k in env):
                self.add("INFO", "mcp", "mcp-secret-env", label, 0, f"{name}: передаёт секреты в env: {', '.join(env)}")

    # -- запуск --
    def run(self, roots: list[Path]):
        self.multi = len(roots) > 1
        for root in roots:
            for path in self.walk(root):
                self.scan_file(root, path)
            self.configs(root)
            self.plugin_claims(root)
        self.dedupe()

    def dedupe(self):
        best: dict[tuple, Finding] = {}
        for f in self.findings:
            key = (f.cls, f.file, f.line, f.text) if f.line else (f.cls, f.rule, f.file, f.text)
            if key not in best or RANK[f.level] < RANK[best[key].level]:
                best[key] = f
        # одна строка — одна находка класса (берём самый высокий уровень)
        seen: dict[tuple, Finding] = {}
        for f in best.values():
            key = (f.cls, f.file, f.line) if f.line else (f.cls, f.rule, f.file, f.text)
            if key not in seen or RANK[f.level] < RANK[seen[key].level]:
                seen[key] = f
        self.findings = sorted(seen.values(), key=lambda f: (RANK[f.level], f.cls, f.file, f.line))


def read_text(p: Path) -> str:
    try:
        if p.is_file() and p.stat().st_size <= MAX_BYTES:
            return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass
    return ""


def plugin_name(root: Path, d: Path) -> str:
    cur = d
    while True:
        pj = cur / ".claude-plugin" / "plugin.json"
        if pj.exists():
            try:
                return json.loads(pj.read_text(encoding="utf-8")).get("name") or cur.name
            except ValueError:
                return cur.name
        if cur.resolve() == root.resolve() or cur.parent == cur:
            return root.name
        cur = cur.parent


def collect_skills(root: Path, excludes: set[str]) -> list[dict]:
    out = []
    for cur, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(x for x in dirs if x not in excludes | {".git"})
        if "SKILL.md" in files:
            p = Path(cur, "SKILL.md")
            fm, _ = parse_frontmatter(read_text(p))
            fm = fm or {}
            desc = fm.get("description") or ""
            desc = desc if isinstance(desc, str) else " ".join(desc)
            wtu = fm.get("when_to_use") or ""
            out.append({"label": str(p), "dir": str(Path(cur).resolve()), "root": str(root),
                        "plugin": plugin_name(root, Path(cur)), "name": str(fm.get("name") or Path(cur).name),
                        "description": (desc + " " + (wtu if isinstance(wtu, str) else "")).strip(), "file": str(p)})
    return out


def duplicates(skills: list[dict], threshold: float) -> list[Finding]:
    out: list[Finding] = []
    uniq: dict[str, dict] = {}
    for s in skills:
        uniq.setdefault(s["dir"], s)
    items = list(uniq.values())
    by_name: dict[str, list[dict]] = {}
    for s in items:
        by_name.setdefault(s["name"], []).append(s)
    for name, group in sorted(by_name.items()):
        if len(group) > 1:
            where = "; ".join(f"{g['plugin']}:{g['name']} ({g['file']})" for g in group)
            out.append(Finding("WARN", "duplicates", "dup-name", group[0]["file"], 0,
                               f"одно имя «{name}» у {len(group)} скиллов: {where}"))
    kws = {s["dir"]: keywords(s["description"]) for s in items}
    phr = {s["dir"]: phrases(s["description"]) for s in items}
    for a, b in itertools.combinations(items, 2):
        ka, kb = kws[a["dir"]], kws[b["dir"]]
        j = len(ka & kb) / len(ka | kb) if ka | kb else 0.0
        common = phr[a["dir"]] & phr[b["dir"]]
        pair = f"{a['plugin']}:{a['name']} ↔ {b['plugin']}:{b['name']}"
        if j >= threshold:
            out.append(Finding("WARN", "duplicates", "dup-trigger", a["file"], 0,
                               f"близкие description, Jaccard {j:.2f}: {pair}", "общие: " + ", ".join(sorted(ka & kb))[:160]))
        elif common:
            out.append(Finding("WARN", "duplicates", "dup-phrase", a["file"], 0,
                               f"одинаковые тригерные фразы: {pair}", "; ".join(sorted(common))[:160]))
        elif j >= threshold * 0.66:
            out.append(Finding("INFO", "duplicates", "near-trigger", a["file"], 0, f"Jaccard {j:.2f}: {pair}"))
    return out


def load_tsv(path: Path) -> list[dict]:
    out = []
    for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "\t" not in ln or ln.startswith("#"):
            continue
        name, desc = ln.split("\t", 1)
        plugin, _, short = name.rpartition(":")
        out.append({"label": f"{path.name}:{i}", "dir": f"tsv:{path.name}:{name}", "root": str(path),
                    "plugin": plugin or path.stem, "name": short, "description": desc, "file": f"{path.name}:{i}"})
    return out


# ---------------------------------------------------------------------------
# Вывод
# ---------------------------------------------------------------------------
def render(sc: Scanner, findings: list[Finding], roots, dup_only: bool, verbose: bool) -> str:
    cnt = {lv: sum(1 for f in findings if f.level == lv) for lv in RANK}
    verdict = "BLOCK" if cnt["BLOCK"] else "WARN" if cnt["WARN"] else "PASS"
    out = [f"# skill-prescan {VERSION}: {', '.join(str(r) for r in roots)}", "",
           f"Итог: **{verdict}** · BLOCK {cnt['BLOCK']} · WARN {cnt['WARN']} · INFO {cnt['INFO']} · файлов {sc.files} · скиллов {len(sc.skills)}",
           "", "Эвристика, не доказательство: BLOCK — стоп и ручной разбор, WARN — прочитать и закрыть, INFO — справочно.", ""]
    if not dup_only:
        out += ["## Поверхности исполнения без вызова скилла", ""]
        out += [f"- `{r}` — {w}" for r, w in sc.surfaces] or ["- нет"]
        out.append("")

    def table(rows):
        res = ["| Уровень | Класс | Правило | Файл:строка | Фрагмент | Пометка |", "|---|---|---|---|---|---|"]
        for f in rows:
            frag = f.text.replace("|", "\\|").replace("`", "'")
            note = f.note.replace("|", "\\|")
            res.append(f"| {f.level} | {f.cls} | {f.rule} | `{f.file}:{f.line}` | `{frag}` | {note} |")
        return res

    main_rows = [f for f in findings if f.level != "INFO" or verbose]
    out += ["## Находки", ""] + (table(main_rows) if main_rows else ["Нет."]) + [""]
    if not verbose:
        info: dict[str, int] = {}
        for f in findings:
            if f.level == "INFO":
                info[f.cls + "/" + f.rule] = info.get(f.cls + "/" + f.rule, 0) + 1
        if info:
            out += ["INFO по правилам (подробно: `--verbose`): " + ", ".join(f"{k} ×{v}" for k, v in sorted(info.items())), ""]
    if not dup_only:
        out += ["## Внешние хосты", "", ", ".join(f"`{h}`" for h in sorted(sc.hosts)) or "нет", "",
                "## Не прочитано", ""] + ([f"- {u}" for u in sc.unread] or ["- всё текстовое прочитано (медиа и .docx пропущены)"])
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="skill-prescan.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--roots", nargs="+", type=Path, default=[])
    ap.add_argument("--descriptions", type=Path, action="append", default=[])
    ap.add_argument("--exclude", nargs="+", default=[])
    ap.add_argument("--dup-threshold", type=float, default=0.30)
    ap.add_argument("--fail-on", choices=["block", "warn"], default="block")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--version", action="version", version=VERSION)
    a = ap.parse_args(argv)
    if not a.paths and not a.roots:
        ap.print_help()
        return 2
    for p in a.paths + a.roots + a.descriptions:
        if not p.exists():
            print(f"нет пути: {p}", file=sys.stderr)
            return 2
    excludes = set(a.exclude)
    sc = Scanner(excludes)
    roots = [p.resolve() for p in a.paths]
    sc.run(roots)
    all_skills = list(sc.skills)
    for r in a.roots:
        all_skills += collect_skills(r.resolve(), excludes)
    for t in a.descriptions:
        all_skills += load_tsv(t)
    findings = sc.findings + duplicates(all_skills, a.dup_threshold)
    findings.sort(key=lambda f: (RANK[f.level], f.cls, f.file, f.line))
    shown = roots + [r.resolve() for r in a.roots]
    if a.json:
        print(json.dumps({"version": VERSION, "roots": [str(r) for r in shown], "files": sc.files,
                          "skills": len(all_skills), "findings": [asdict(f) for f in findings],
                          "exec_surfaces": sc.surfaces, "hosts": sorted(sc.hosts), "unread": sc.unread},
                         ensure_ascii=False, indent=1))
    else:
        sys.stdout.write(render(sc, findings, shown, not a.paths, a.verbose))
    worst = min((RANK[f.level] for f in findings), default=9)
    limit = RANK["WARN"] if a.fail_on == "warn" else RANK["BLOCK"]
    return 1 if worst <= limit else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

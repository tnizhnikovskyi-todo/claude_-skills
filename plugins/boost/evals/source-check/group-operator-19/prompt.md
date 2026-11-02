---
name: source-check/group-operator-19
description: Odoo 19 — group_operator устарел с 18, правильно aggregator. Нужна цитата с URL
tags: [source-check, positive]
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

Пишу модуль под Odoo 19: `margin_pct = fields.Float(group_operator='avg')`. Это правильный параметр для 19-й версии? Подтверди по источнику.

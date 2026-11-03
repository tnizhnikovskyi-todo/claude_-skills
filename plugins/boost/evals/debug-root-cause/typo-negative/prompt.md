---
name: debug-root-cause/typo-negative
description: Очевидная опечатка — скилл не должен срабатывать, ответ короткий
tags: [debug-root-cause, negative]
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Поле в Odoo 19 не становится обязательным в форме: `name = fields.Char(requird=True)`. Что не так? Ответь одной-двумя строками.

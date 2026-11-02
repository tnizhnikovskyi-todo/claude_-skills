---
skill: lean-change
date: 2026-10-20
status: actioned
kind: violation
fix: text
rule: "тест на рискованную логику"
repeat_of: null
siblings_checked: ["repo-audit: ok"]
source: "сессия пользователя 2026-10-20"
summary: lean-change не добавил тест на сумму заказа в Odoo-задаче
resolution: "в SKILL.md добавлена фраза про TransactionCase"
---
**Ожидали:** тест `TransactionCase` на сумму заказа.
**Получили:** дифф без тестов.
**Предложение:** явно потребовать тест на деньги.
**Принцип:** —

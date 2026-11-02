---
name: general/bug-hunt
description: Поиск бага по симптому (округление долей рассрочки)
tags: [general, bug]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Пользователи жалуются: иногда сумма платежей по рассрочке не равна сумме счёта
(расходится на копейку). Вот код. Найди причину и дай исправление.

```python
def split_installments(total, n):
    """Делит сумму счёта total на n равных платежей (до копеек)."""
    part = round(total / n, 2)
    return [part] * n


def schedule(invoice):
    parts = split_installments(invoice["amount"], invoice["months"])
    return [{"month": i + 1, "amount": p} for i, p in enumerate(parts)]
```

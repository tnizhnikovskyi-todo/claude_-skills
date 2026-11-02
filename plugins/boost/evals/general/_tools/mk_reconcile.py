"""Генерирует данные кейса reconcile-payments и печатает правильный ответ.
Детерминированно (seed). Расхождения заложены явно, см. PLANTED."""
import random
random.seed(19)
partners = ["ТОВ Альфа", "ТОВ Бета", "ФОП Гончар", "ТОВ Дельта", "ПП Енергія",
            "ТОВ Злагода", "ФОП Іваненко", "ТОВ Каштан", "ТОВ Лан", "ПП Мрія"]
inv = []
for i in range(101, 161):
    amt = round(random.randint(4000, 250000) / 100 * 5, 2)
    inv.append((f"INV/2026/{i:04d}", random.choice(partners), amt))
pay = []
day = 1
for num, partner, amt in inv:
    if num == "INV/2026/0126":          # нет оплаты
        continue
    a = amt
    if num == "INV/2026/0107":          # перестановка цифр
        s = f"{amt:.2f}"; a = float(s[:-5] + s[-4] + s[-5] + s[-3:])
    if num == "INV/2026/0144":          # недоплата 0.10
        a = round(amt - 0.10, 2)
    ref = num
    if num == "INV/2026/0131":          # другой формат ссылки, сумма верная (приманка)
        ref = "INV-2026-0131"
    pay.append((f"2026-10-{(day % 28) + 1:02d}", ref, partner, a))
    if num == "INV/2026/0119":          # оплачено дважды
        pay.append((f"2026-10-{((day + 3) % 28) + 1:02d}", ref, partner, a))
    day += 1
pay.append(("2026-10-29", "INV/2026/0171", "ТОВ Лан", 18350.00))  # оплата без счёта
random.shuffle(pay)
def fmt(x): return f"{x:,.2f}".replace(",", " ")
print("### Счета (выставлено)\n\n| Номер | Контрагент | Сумма |\n|---|---|---:|")
for n, p, a in inv: print(f"| {n} | {p} | {fmt(a)} |")
print("\n### Оплаты (банк)\n\n| Дата | Назначение (номер счёта) | Плательщик | Сумма |\n|---|---|---|---:|")
for d, r, p, a in pay: print(f"| {d} | {r} | {p} | {fmt(a)} |")
import sys
amap = {n: a for n, _, a in inv}
s = f"{amap['INV/2026/0107']:.2f}"
print(f"\n<!-- ANSWER 0107 inv={amap['INV/2026/0107']} paid={float(s[:-5]+s[-4]+s[-5]+s[-3:])}; 0119 x2 {amap['INV/2026/0119']}; 0126 none {amap['INV/2026/0126']}; 0144 inv={amap['INV/2026/0144']} paid={round(amap['INV/2026/0144']-0.1,2)}; 0171 stray 18350; 0131 ok -->", file=sys.stderr)

"""Свой замер (не код skills-janitor): длина описаний и перекрытие триггеров.
Повторяет ИДЕЮ janitor (Jaccard по словам описания, 1.3 токена/слово),
чтобы показать её поведение на кириллице, и сравнивает с Unicode-вариантом."""
import re, sys, os, glob, itertools

def frontmatter_desc(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    if not lines or lines[0].strip() != "---":
        return ""
    out, block = [], False
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        if not block and ln.startswith("description:"):
            v = ln[len("description:"):].strip()
            if v in (">", "|", ">-", "|-", ""):
                block = True
                continue
            return v.strip('"')
        elif block:
            if ln.startswith((" ", "\t")):
                out.append(ln.strip())
            else:
                break
    return " ".join(out)

items = []
repo, tsv = sys.argv[1], sys.argv[2]
for p in sorted(glob.glob(os.path.join(repo, "plugins/boost/skills/*/SKILL.md"))):
    items.append(("boost:" + p.split("/")[-2], frontmatter_desc(p)))
for ln in open(tsv, encoding="utf-8"):
    if "\t" in ln:
        n, d = ln.rstrip("\n").split("\t", 1)
        items.append(("org:" + n, d))

STOP = set("use when the user wants to or and a an this skill also that for with in on of is are it be as at by from not".split())
STOP |= set("і й та або в у на з із до для що як це не коли щойно якщо чи по за від при його її їх и или с из для что как это не когда если по".split())

def kw_ascii(d):  # как у janitor: [a-z]+
    return {w for w in re.findall(r"[a-z]+", d.lower()) if w not in STOP and len(w) > 2}

def kw_uni(d):
    return {w[:6] for w in re.findall(r"[^\W\d_]+", d.lower()) if w not in STOP and len(w) > 2}

print(f"{'skill':34} {'chars':>5} {'words':>5} {'jan~tok':>7} {'cyr%':>4} {'ascii_kw':>8} {'uni_kw':>6}")
tc = tw = 0
for n, d in items:
    w = len(d.split()); c = len(d)
    cyr = sum(1 for ch in d if "Ѐ" <= ch <= "ӿ")
    tc += c; tw += w
    print(f"{n:34} {c:5} {w:5} {round(w*1.3):7} {round(100*cyr/max(1,c)):4} {len(kw_ascii(d)):8} {len(kw_uni(d)):6}")
print(f"{'TOTAL':34} {tc:5} {tw:5} {round(tw*1.3):7}")

def jac(a, b):
    return len(a & b) / len(a | b) if a | b else 0

print("\nПары с Jaccard > 0.30 (janitor-порог). ascii = как у janitor, uni = Unicode-слова, стем 6 букв")
rows = []
for (n1, d1), (n2, d2) in itertools.combinations(items, 2):
    ja, ju = jac(kw_ascii(d1), kw_ascii(d2)), jac(kw_uni(d1), kw_uni(d2))
    rows.append((ju, ja, n1, n2))
rows.sort(reverse=True)
for ju, ja, n1, n2 in rows[:8]:
    print(f"  uni={ju:.2f} ascii={ja:.2f}  {n1} <-> {n2}")
print("  пар выше 0.30: ascii =", sum(1 for r in rows if r[1] > .3), " uni =", sum(1 for r in rows if r[0] > .3))
print("\nascii > 0.30:")
for ju, ja, n1, n2 in sorted(rows, key=lambda r: -r[1]):
    if ja > .3:
        d1 = dict(items)[n1]; d2 = dict(items)[n2]
        print(f"  {ja:.2f} {n1} <-> {n2}: {sorted(kw_ascii(d1) & kw_ascii(d2))} | union={len(kw_ascii(d1)|kw_ascii(d2))}")

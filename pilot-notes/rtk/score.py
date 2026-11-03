"""Оценка прогонов: score.py <out_dir> [--cmds]
Читает <id>.jsonl (stream-json): ключи из tasks.json в финальном ответе,
usage, стоимость, ходы, команды Bash и байты их вывода (tool_result)."""
import json, sys, os
here = os.path.dirname(os.path.abspath(__file__))
tasks = json.load(open(os.path.join(here, 'tasks.json')))
out = sys.argv[1]; show = '--cmds' in sys.argv
tot = dict(cost=0, inp=0, bash=0, hits=0, keys=0)
print("| задача | ключи | ходы | вход (вкл. кэш) | выход | байт вывода Bash | $ |\n|---|---|---|---|---|---|---|")
for t in tasks:
    p = os.path.join(out, t['id'] + '.jsonl')
    if not os.path.exists(p): continue
    res = None; cmds = []; bb = 0
    for line in open(p):
        try: e = json.loads(line)
        except ValueError: continue
        if e.get('type') == 'result': res = e
        m = e.get('message') or {}
        for c in m.get('content') or [] if isinstance(m.get('content'), list) else []:
            if c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                cmds.append(c['input'].get('command', ''))
            if c.get('type') == 'tool_result':
                cc = c.get('content'); bb += len(json.dumps(cc, ensure_ascii=False) if not isinstance(cc, str) else cc)
    if not res: print(f"| {t['id']} | нет результата |"); continue
    r = res.get('result') or ''; u = res['usage']
    hit = sum(k in r for k in t['keys'])
    inp = u['input_tokens'] + u['cache_creation_input_tokens'] + u['cache_read_input_tokens']
    tot['cost'] += res['total_cost_usd']; tot['inp'] += inp; tot['bash'] += bb; tot['hits'] += hit; tot['keys'] += len(t['keys'])
    print(f"| {t['id']} | {hit}/{len(t['keys'])} | {res['num_turns']} | {inp} | {u['output_tokens']} | {bb} | {res['total_cost_usd']:.4f} |")
    if show:
        for c in cmds: print(f"|   | `{c[:150]}` |")
print(f"| **итого** | {tot['hits']}/{tot['keys']} | | {tot['inp']} | | {tot['bash']} | {tot['cost']:.4f} |")

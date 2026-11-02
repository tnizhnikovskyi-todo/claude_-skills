#!/usr/bin/env python3
"""Карта аддонов Odoo: модели, наследование, связи, вью, права, правила.

Только stdlib, ничего не устанавливает, ничего не импортирует из
анализируемого кода (Python разбирается через ast, XML через ElementTree).

    python3 -I odoo_map.py ADDONS_PATH [...]                  # вся карта
    python3 -I odoo_map.py ADDONS_PATH --model td.vehicle     # всё о модели
    python3 -I odoo_map.py ADDONS_PATH --model td.vehicle --field odometer

Видит только переданные пути. Ядро Odoo и другие репозитории не
сканирует: всё, что определено вне них, помечено «вне скана».
"""
import argparse
import ast
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'static'}
RELATIONAL = {'Many2one', 'One2many', 'Many2many'}


def rel(path, root):
    return os.path.relpath(path, root)


def find_modules(paths):
    mods = {}
    for base in paths:
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            if '__manifest__.py' in filenames:
                mods[os.path.basename(dirpath)] = dirpath
    return mods


def read_manifest(path):
    try:
        with open(os.path.join(path, '__manifest__.py'), encoding='utf-8') as f:
            data = ast.literal_eval(f.read())
        return data if isinstance(data, dict) else {}
    except (ValueError, SyntaxError, OSError):
        return {}


def literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError, TypeError):
        return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [v for v in value if isinstance(v, str)]


def call_name(node):
    """'fields.Many2one' -> 'Many2one', 'api.depends' -> 'depends'."""
    func = node.func if isinstance(node, ast.Call) else node
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ''


def scan_python(path, module, root, out):
    try:
        with open(path, encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=path)
    except (SyntaxError, OSError, UnicodeDecodeError) as exc:
        out['skipped'].append(f'{rel(path, root)}: {exc.__class__.__name__}')
        return
    where = rel(path, root)
    for node in ast.walk(tree):
        # env['model'] / env["model"]
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute)
                and node.value.attr == 'env'):
            name = literal(node.slice)
            if isinstance(name, str):
                out['env'].append({'model': name, 'module': module,
                                   'where': f'{where}:{node.lineno}'})
        if not isinstance(node, ast.ClassDef):
            continue
        attrs, fields, decos = {}, [], []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                    and isinstance(stmt.targets[0], ast.Name):
                target, value = stmt.targets[0].id, stmt.value
                if target in ('_name', '_inherit', '_inherits'):
                    attrs[target] = literal(value)
                elif isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                        and isinstance(value.func.value, ast.Name) \
                        and value.func.value.id == 'fields':
                    kw = {k.arg: literal(k.value) for k in value.keywords if k.arg}
                    ftype = value.func.attr
                    comodel = kw.get('comodel_name')
                    if comodel is None and ftype in RELATIONAL and value.args:
                        comodel = literal(value.args[0])
                    fields.append({'name': target, 'type': ftype, 'line': stmt.lineno,
                                   'comodel': comodel, 'related': kw.get('related'),
                                   'compute': kw.get('compute')})
            elif isinstance(stmt, ast.FunctionDef):
                for d in stmt.decorator_list:
                    if isinstance(d, ast.Call) and call_name(d) in (
                            'depends', 'constrains', 'onchange'):
                        args = [a for a in (literal(x) for x in d.args) if isinstance(a, str)]
                        decos.append({'kind': call_name(d), 'args': args,
                                      'method': stmt.name, 'line': stmt.lineno})
        if not attrs:
            continue
        name = attrs.get('_name')
        inherit = as_list(attrs.get('_inherit'))
        inherits = attrs.get('_inherits') or {}
        if not isinstance(name, str):
            name = inherit[0] if len(inherit) == 1 else None
        if not name:
            continue
        if '_name' not in attrs or name in inherit:
            role = 'расширяет'
        else:
            role = 'определяет'
        bases = [call_name(b) for b in node.bases]
        out['classes'].append({
            'model': name, 'role': role, 'module': module, 'class': node.name,
            'where': f'{where}:{node.lineno}', 'mixins': [i for i in inherit if i != name],
            'inherits': inherits if isinstance(inherits, dict) else {},
            'transient': 'TransientModel' in bases, 'fields': fields, 'decos': decos,
            'file': where})


def line_of(text, xml_id):
    m = re.search(r'id=["\']%s["\']' % re.escape(xml_id), text)
    return text.count('\n', 0, m.start()) + 1 if m else 0


def model_from_ref(ref, known):
    ref = ref.split('.', 1)[-1]
    if not ref.startswith('model_'):
        return ref
    key = ref[len('model_'):]
    for model in known:
        if model.replace('.', '_') == key:
            return model
    return key.replace('_', '.') + ' (?)'


def scan_xml(path, module, root, out):
    where = rel(path, root)
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        tree = ET.fromstring(text.encode('utf-8'))
    except (ET.ParseError, OSError, UnicodeDecodeError) as exc:
        out['skipped'].append(f'{where}: {exc.__class__.__name__}')
        return
    for rec in tree.iter('record'):
        model, xml_id = rec.get('model', ''), rec.get('id', '')
        flds = {f.get('name'): f for f in rec.findall('field')}
        loc = f'{where}:{line_of(text, xml_id)}'
        if model == 'ir.ui.view':
            arch = flds.get('arch')
            root_tag = arch[0].tag if arch is not None and len(arch) else '?'
            inh = flds.get('inherit_id')
            out['views'].append({
                'id': f'{module}.{xml_id}', 'module': module, 'where': loc,
                'model': (flds['model'].text or '').strip() if 'model' in flds else '',
                'type': root_tag if inh is None else 'наследует',
                'inherit': qualify(inh.get('ref'), module) if inh is not None else ''})
        elif model == 'ir.rule':
            mref = flds['model_id'].get('ref', '') if 'model_id' in flds else ''
            groups = flds['groups'].get('eval', '') if 'groups' in flds else ''
            out['rules'].append({
                'id': f'{module}.{xml_id}', 'module': module, 'where': loc, 'model_ref': mref,
                'groups': ', '.join(re.findall(r"ref\(['\"]([^'\"]+)", groups)) or 'глобальное',
                'domain': ' '.join((flds['domain_force'].text or '').split())
                if 'domain_force' in flds else ''})
        elif model.startswith('ir.actions'):
            if 'res_model' in flds:
                out['actions'].append({'id': f'{module}.{xml_id}', 'where': loc,
                                       'model': (flds['res_model'].text or '').strip()})
        elif model:
            out['records'].append({'model': model, 'module': module, 'where': loc})
    for tpl in tree.iter('template'):
        if tpl.get('inherit_id'):
            out['views'].append({'id': f"{module}.{tpl.get('id', '')}", 'module': module,
                                 'where': f"{where}:{line_of(text, tpl.get('id', ''))}",
                                 'model': '(qweb)', 'type': 'наследует',
                                 'inherit': qualify(tpl.get('inherit_id'), module)})


def qualify(ref, module):
    return ref if '.' in ref else f'{module}.{ref}'


def scan_acl(path, module, root, out):
    where = rel(path, root)
    with open(path, encoding='utf-8', newline='') as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            perms = ''.join(c if row.get(f'perm_{p}', '0').strip() == '1' else '-'
                            for p, c in (('read', 'r'), ('write', 'w'),
                                         ('create', 'c'), ('unlink', 'd')))
            out['acl'].append({'id': row.get('id', ''), 'module': module,
                               'model_ref': row.get('model_id:id', ''),
                               'group': row.get('group_id:id', '') or 'все (без группы)',
                               'perms': perms, 'where': f'{where}:{i}'})


def scan(paths):
    root = os.path.commonpath([os.path.abspath(p) for p in paths])
    if os.path.isfile(root):
        root = os.path.dirname(root)
    out = {k: [] for k in ('classes', 'env', 'views', 'rules', 'actions', 'records',
                           'acl', 'skipped')}
    out['modules'] = {}
    for module, mpath in sorted(find_modules(paths).items()):
        man = read_manifest(mpath)
        out['modules'][module] = {'depends': man.get('depends', []),
                                  'data': man.get('data', []), 'path': rel(mpath, root)}
        for dirpath, dirnames, filenames in os.walk(mpath):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                if fn.endswith('.py') and fn != '__manifest__.py':
                    scan_python(full, module, root, out)
                elif fn.endswith('.xml'):
                    scan_xml(full, module, root, out)
                elif fn == 'ir.model.access.csv':
                    scan_acl(full, module, root, out)
    known = {c['model'] for c in out['classes']}
    for item in out['rules'] + out['acl']:
        item['model'] = model_from_ref(item['model_ref'], known)
    out['root'] = root
    return out


def table(head, rows):
    if not rows:
        return '_нет_\n'
    lines = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    lines += ['| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |' for r in rows]
    return '\n'.join(lines) + '\n'


def touches(cls, model):
    return cls['model'] == model or model in cls['inherits'] or model in cls['mixins']


def render(out, model=None, field=None):
    p = []
    defined = {c['model'] for c in out['classes'] if c['role'] == 'определяет'}
    classes = [c for c in out['classes'] if not model or touches(c, model)]
    p.append(f"# Карта Odoo: {model or 'все модели'}\n\nКорень скана: `{out['root']}`\n")

    p.append('## Модули (__manifest__.py)\n')
    p.append(table(['модуль', 'depends', 'data'], [
        (m, ', '.join(v['depends']) or '—', len(v['data']))
        for m, v in out['modules'].items()]))

    p.append('\n## Модели и наследование\n')
    rows = []
    for c in classes:
        role = c['role'] if c['model'] == model or not model else (
            'делегирует (_inherits)' if model in c['inherits'] else 'миксин/прототип')
        extra = []
        if c['mixins']:
            extra.append('_inherit: ' + ', '.join(c['mixins']))
        if c['inherits']:
            extra.append('_inherits: ' + ', '.join(f'{k} → {v}' for k, v in c['inherits'].items()))
        if c['transient']:
            extra.append('TransientModel')
        rows.append((c['model'], role, c['module'], c['class'], c['where'], '; '.join(extra)))
    p.append(table(['модель', 'роль', 'модуль', 'класс', 'где', 'ещё'], rows))
    outside = sorted({c['model'] for c in classes if c['model'] not in defined}
                     | {m for c in classes for m in list(c['inherits']) + c['mixins']
                        if m not in defined})
    if outside:
        p.append('\nОпределены вне скана (ядро/другие репо): ' +
                 ', '.join(f'`{m}`' for m in outside) + '\n')

    p.append('\n## Поля-связи (comodel / related / compute)\n')
    rows = []
    for c in out['classes']:
        for f in c['fields']:
            hit = (not model or c['model'] == model or f['comodel'] == model)
            if hit and (f['comodel'] or f['related'] or f['compute']):
                rows.append((c['model'], f['name'], f['type'], f['comodel'] or '',
                             f['related'] or '', f['compute'] or '',
                             f"{c['file']}:{f['line']}"))
    p.append(table(['модель', 'поле', 'тип', 'comodel', 'related', 'compute', 'где'], rows))

    paths = [r for r in through_paths(out, model)] if model else []
    if paths:
        p.append(f'\n## Пути через `{model}` из других моделей (related / depends / домены правил)\n')
        p.append(table(['модель', 'что', 'путь', 'где'], paths))

    rows = [(c['model'], d['kind'], ', '.join(d['args']), d['method'],
             f"{c['file']}:{d['line']}")
            for c in out['classes'] if not model or c['model'] == model for d in c['decos']]
    p.append('\n## @api.depends / constrains / onchange\n')
    p.append(table(['модель', 'декоратор', 'пути', 'метод', 'где'], rows))

    rows = [(e['model'], e['module'], e['where']) for e in out['env']
            if not model or e['model'] == model]
    p.append("\n## env['…']\n")
    p.append(table(['модель', 'модуль', 'где'], rows))

    deleg = {c['model'] for c in out['classes'] if model and model in c['inherits']}
    views = [v for v in out['views'] if not model or v['model'] == model or v['model'] in deleg]
    p.append('\n## Вью\n')
    if deleg:
        p.append('Включены вью моделей с `_inherits` на неё (там видны её поля): ' +
                 ', '.join(f'`{m}`' for m in sorted(deleg)) + '\n\n')
    p.append(table(['xml id', 'модель', 'тип', 'inherit_id', 'где'], [
        (v['id'], v['model'], v['type'], v['inherit'] or '', v['where']) for v in views]))
    ids = {v['id'] for v in out['views']}
    tree = view_tree(views)
    if tree:
        p.append('\nДерево наследования вью:\n```\n' + tree + '```\n')
    ext = sorted({v['inherit'] for v in views if v['inherit'] and v['inherit'] not in ids})
    if ext:
        p.append('Родительские вью вне скана: ' + ', '.join(f'`{e}`' for e in ext) + '\n')
    acts = [(a['id'], a['model'], a['where']) for a in out['actions']
            if not model or a['model'] == model]
    if acts:
        p.append('\nДействия (res_model):\n' + table(['xml id', 'модель', 'где'], acts))

    p.append('\n## Права (ir.model.access.csv)\n')
    p.append(table(['модель', 'группа', 'rwcd', 'id', 'где'], [
        (a['model'], a['group'], a['perms'], a['id'], a['where'])
        for a in out['acl'] if not model or a['model'] == model]))
    with_acl = {a['model'] for a in out['acl']}
    missing = sorted(m for m in defined if m not in with_acl and (not model or m == model))
    if missing:
        p.append('\n**Без строк доступа:** ' + ', '.join(f'`{m}`' for m in missing) + '\n')

    p.append('\n## Правила записей (ir.rule)\n')
    p.append(table(['модель', 'группы', 'домен', 'id', 'где'], [
        (r['model'], r['groups'], f"`{r['domain']}`", r['id'], r['where'])
        for r in out['rules'] if not model or r['model'] == model]))

    recs = {}
    for r in out['records']:
        if not model or r['model'] == model:
            recs.setdefault((r['model'], r['module']), []).append(r['where'])
    if recs:
        p.append('\n## Прочие <record> по моделям\n')
        p.append(table(['модель', 'модуль', 'записей', 'первая'], [
            (m, mod, len(w), w[0]) for (m, mod), w in sorted(recs.items())]))

    if model and field:
        p.append(field_hits(out, field))

    p.append('\n## Не охвачено\n')
    p.append('- Только пути скана. Ядро Odoo, enterprise, другие репо не сканировались.\n'
             '- Данные в БД (ir.filters, серверные действия, Studio, автоматизации) не видны.\n'
             '- JS/OWL, QWeb-отчёты по тексту не разбираются; ищи grep по имени.\n')
    if out['skipped']:
        p.append('- Не разобраны: ' + '; '.join(out['skipped']) + '\n')
    return '\n'.join(p)


def comodels(out):
    """model -> {field: comodel} по всем классам (с учётом _inherit и _inherits)."""
    res = {}
    for c in out['classes']:
        res.setdefault(c['model'], {}).update(
            {f['name']: f['comodel'] for f in c['fields'] if f['comodel']})
    for c in out['classes']:
        for parent in c['inherits']:
            for k, v in res.get(parent, {}).items():
                res.setdefault(c['model'], {}).setdefault(k, v)
    return res


def walk_path(cmap, start, path):
    """Модели, через которые проходит путь 'a.b.c' (без стартовой)."""
    seen, cur = [], start
    for part in path.split('.')[:-1]:
        cur = cmap.get(cur, {}).get(part)
        if not cur:
            break
        seen.append(cur)
    return seen


def through_paths(out, model):
    cmap = comodels(out)
    for c in out['classes']:
        for f in c['fields']:
            if f['related'] and model in walk_path(cmap, c['model'], f['related']):
                yield (c['model'], f"related поля {f['name']}", f['related'],
                       f"{c['file']}:{f['line']}")
        for d in c['decos']:
            for a in d['args']:
                if model in walk_path(cmap, c['model'], a):
                    yield (c['model'], f"{d['kind']} {d['method']}", a,
                           f"{c['file']}:{d['line']}")
    for r in out['rules']:
        for a in re.findall(r"\(\s*['\"]([\w.]+)['\"]", r['domain']):
            if model in walk_path(cmap, r['model'], a):
                yield (r['model'], f"ir.rule {r['id']}", a, r['where'])


def view_tree(views):
    by_id = {v['id']: v for v in views}
    children = {}
    for v in views:
        children.setdefault(v['inherit'], []).append(v)
    lines = []

    def walk(v, depth):
        lines.append('  ' * depth + f"{v['id']} ({v['type']}, {v['where']})\n")
        for ch in children.get(v['id'], []):
            walk(ch, depth + 1)
    for v in views:
        if not v['inherit'] or v['inherit'] not in by_id:
            if v['inherit']:
                lines.append(f"{v['inherit']} (вне скана)\n")
                walk(v, 1)
            else:
                walk(v, 0)
    return ''.join(lines) if any(v['inherit'] for v in views) else ''


def field_hits(out, field):
    f = re.escape(field)
    # 'odometer', vehicle_id.odometer — да; odometer_at, td.odometer.export — нет
    pat = re.compile(r'(?<![\w.])%s(?![\w])|(?<=\.)%s(?![\w.])' % (f, f))
    rows = []
    for module, info in out['modules'].items():
        mpath = os.path.join(out['root'], info['path'])
        for dirpath, dirnames, filenames in os.walk(mpath):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                if not fn.endswith(('.py', '.xml', '.csv', '.js')):
                    continue
                full = os.path.join(dirpath, fn)
                try:
                    with open(full, encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if pat.search(line):
                                rows.append((f'{rel(full, out["root"])}:{i}',
                                             line.strip()[:110]))
                except (OSError, UnicodeDecodeError):
                    continue
    return (f'\n## Упоминания `{field}` (по имени, все модели)\n\n'
            'Разбери каждую строку: это поле нужной модели (через _inherit, _inherits, '
            'related, путь в depends/домене) или одноимённое поле другой модели?\n\n'
            + table(['где', 'строка'], rows))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='каталоги аддонов или модулей')
    ap.add_argument('--model', help='показать только то, что касается модели')
    ap.add_argument('--field', help='с --model: все упоминания поля по имени')
    args = ap.parse_args(argv)
    sys.stdout.write(render(scan(args.paths), args.model, args.field))
    return 0


if __name__ == '__main__':
    sys.exit(main())

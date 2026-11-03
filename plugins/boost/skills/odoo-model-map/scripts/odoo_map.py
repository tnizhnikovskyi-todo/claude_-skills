#!/usr/bin/env python3
"""Карта аддонов Odoo: модели, наследование, связи, вью, права, правила.

Только stdlib, ничего не устанавливает, ничего не импортирует из
анализируемого кода (Python разбирается через ast, XML через ElementTree).

    python3 -I odoo_map.py ADDONS_PATH [...]                  # вся карта
    python3 -I odoo_map.py ADDONS_PATH --model td.vehicle     # всё о модели
    python3 -I odoo_map.py ADDONS_PATH --model td.vehicle --field odometer
    python3 -I odoo_map.py ADDONS_PATH --model td.vehicle --trace action_reset_odometer

Имя модели класса без `_name` зависит от серии Odoo (из `version` в
__manifest__.py, либо `--odoo`): в 19 `_inherit` списком без `_name` даёт
НОВУЮ модель с именем из класса, в 18 список из одного элемента был
расширением.

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


def series_of(version):
    """'19.0.1.0.0' -> 19, '18.0.2.1' -> 18, '1.0' / '' -> None (серия не указана)."""
    parts = str(version or '').split('.')
    if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0])
    return None


def class_to_model(cls_name):
    """Имя модели из имени класса по правилу Odoo 19: MileageArchive -> mileage.archive."""
    return re.sub(r'(?<=[^_])([A-Z])', r'.\1', cls_name).lower()


def resolve_name(attrs, cls_name, series):
    """(_name, роль, пометка) для класса модели; (None, None, '') если это не модель."""
    name, raw = attrs.get('_name'), attrs.get('_inherit')
    inherit = as_list(raw)
    if isinstance(name, str) and name:
        return name, 'расширяет' if name in inherit else 'определяет', ''
    if isinstance(raw, str) and raw:
        return raw, 'расширяет', ''          # строкой: расширение в любой серии
    if not inherit:
        return None, None, ''
    parents = ', '.join(inherit)
    if series is not None and series <= 18:
        if len(inherit) == 1:
            return inherit[0], 'расширяет', (
                f'_inherit списком без _name: в {series}.0 расширение; '
                f'в 19.0 стало бы новой моделью `{class_to_model(cls_name)}`')
        return cls_name, 'определяет', f'_inherit списком без _name: модель `{cls_name}` из имени класса'
    new = class_to_model(cls_name)
    note = (f'_inherit списком без _name: в 19.0 НОВАЯ модель `{new}` (имя из класса, '
            f'предупреждение в логе), наследует {parents}, а не расширяет')
    if len(inherit) == 1:
        note += f'; в 18.0 было бы расширение `{inherit[0]}`'
    if series is None:
        note += '; серия Odoo в version манифеста не указана — применено правило 19'
    return new, 'определяет', note


def method_info(fn):
    """super() того же метода, вызовы методов, ключи write/create/update({...})."""
    sup, calls, writes = False, set(), {}
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        attr, obj = n.func.attr, n.func.value
        if isinstance(obj, ast.Call) and call_name(obj) == 'super':
            sup = sup or attr == fn.name
            continue
        calls.add(attr)
        if attr in ('write', 'create', 'update') and n.args and isinstance(n.args[0], ast.Dict):
            keys = {k for k in (literal(x) for x in n.args[0].keys) if isinstance(k, str)}
            # self.write → 'self'; self.vehicle_id.write → 'vehicle_id'; иное → выражение
            tgt = ast.unparse(obj)
            tgt = 'self' if tgt == 'self' else tgt[5:] if tgt.startswith('self.') else tgt
            writes.setdefault(tgt, set()).update(keys)
    return {'line': fn.lineno, 'super': sup, 'calls': calls, 'writes': writes}


def scan_python(path, module, root, out, series=None):
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
        attrs, fields, decos, methods = {}, [], [], {}
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
                methods[stmt.name] = method_info(stmt)
                for d in stmt.decorator_list:
                    if isinstance(d, ast.Call) and call_name(d) in (
                            'depends', 'constrains', 'onchange'):
                        args = [a for a in (literal(x) for x in d.args) if isinstance(a, str)]
                        decos.append({'kind': call_name(d), 'args': args,
                                      'method': stmt.name, 'line': stmt.lineno})
        if not attrs:
            continue
        inherit = as_list(attrs.get('_inherit'))
        inherits = attrs.get('_inherits') or {}
        name, role, note = resolve_name(attrs, node.name, series)
        if not name:
            continue
        bases = [call_name(b) for b in node.bases]
        out['classes'].append({
            'model': name, 'role': role, 'module': module, 'class': node.name,
            'where': f'{where}:{node.lineno}', 'mixins': [i for i in inherit if i != name],
            'inherits': inherits if isinstance(inherits, dict) else {},
            'transient': 'TransientModel' in bases, 'fields': fields, 'decos': decos,
            'methods': methods, 'note': note, 'series': series, 'file': where})


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
            vmodel = (flds['model'].text or '').strip() if 'model' in flds else ''
            for b in (arch.iter('button') if arch is not None else ()):
                if b.get('type') == 'object' and b.get('name'):
                    out['buttons'].append({'method': b.get('name'), 'view': f'{module}.{xml_id}',
                                           'model': vmodel, 'where': loc})
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
            # act_window: res_model; report: model; server: model_id ref
            target = flds.get('res_model') if 'res_model' in flds else flds.get('model')
            name = (target.text or '').strip() if target is not None else ''
            if not name and 'model_id' in flds:
                name = '@' + flds['model_id'].get('ref', '')
            if name:
                out['actions'].append({'id': f'{module}.{xml_id}', 'where': loc,
                                       'model': name, 'kind': model})
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


def scan(paths, odoo=None):
    root = os.path.commonpath([os.path.abspath(p) for p in paths])
    if os.path.isfile(root):
        root = os.path.dirname(root)
    out = {k: [] for k in ('classes', 'env', 'views', 'rules', 'actions', 'records',
                           'acl', 'buttons', 'skipped')}
    out['modules'] = {}
    for module, mpath in sorted(find_modules(paths).items()):
        man = read_manifest(mpath)
        series = odoo or series_of(man.get('version'))
        out['modules'][module] = {'version': man.get('version', ''), 'series': series,
                                  'depends': man.get('depends', []),
                                  'data': man.get('data', []), 'demo': man.get('demo', []),
                                  'path': rel(mpath, root)}
        for dirpath, dirnames, filenames in os.walk(mpath):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                if fn.endswith('.py') and fn != '__manifest__.py':
                    scan_python(full, module, root, out, series)
                elif fn.endswith('.xml'):
                    scan_xml(full, module, root, out)
                elif fn == 'ir.model.access.csv':
                    scan_acl(full, module, root, out)
    known = {c['model'] for c in out['classes']}
    for item in out['rules'] + out['acl']:
        item['model'] = model_from_ref(item['model_ref'], known)
    for a in out['actions']:
        if a['model'].startswith('@'):
            a['model'] = model_from_ref(a['model'][1:], known)
    vmap = {v['id']: v for v in out['views']}
    for b in out['buttons']:
        v, seen = vmap.get(b['view']), set()
        while not b['model'] and v and v['id'] not in seen:   # модель у наследника вью — от родителя
            seen.add(v['id'])
            b['model'], v = v['model'], vmap.get(v['inherit'])
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


def render(out, model=None, field=None, trace_method=None):
    p = []
    defined = {c['model'] for c in out['classes'] if c['role'] == 'определяет'}
    classes = [c for c in out['classes'] if not model or touches(c, model)]
    p.append(f"# Карта Odoo: {model or 'все модели'}\n\nКорень скана: `{out['root']}`\n")

    p.append('## Модули (__manifest__.py)\n')
    p.append(table(['модуль', 'version', 'серия', 'depends', 'data', 'demo'], [
        (m, v['version'] or '—', v['series'] or '? (правило 19)',
         ', '.join(v['depends']) or '—', len(v['data']), len(v['demo']))
        for m, v in out['modules'].items()]))

    p.append('\n## Модели и наследование\n')
    rows = []
    for c in classes:
        role = c['role'] if c['model'] == model or not model else (
            'делегирует (_inherits)' if model in c['inherits'] else
            'новая модель по прототипу (НЕ расширение)' if c['note'] else 'миксин/прототип')
        extra = [c['note']] if c['note'] else []
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
    notes = [c for c in classes if c['note']]
    if notes:
        p.append('\n**Внимание, имя модели зависит от серии Odoo:**\n' + ''.join(
            f"- `{c['class']}` ({c['where']}): {c['note']}\n" for c in notes))

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
    acts = [(a['id'], a['kind'], a['model'], a['where']) for a in out['actions']
            if not model or a['model'] == model]
    if acts:
        p.append('\nДействия и отчёты:\n' + table(['xml id', 'тип', 'модель', 'где'], acts))

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
    if model and trace_method:
        p.append(trace(out, model, trace_method))

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


def load_order(modules):
    """Модули скана в порядке загрузки по depends (между независимыми — по имени)."""
    order, done = [], set()

    def visit(m, stack=()):
        if m in done or m not in modules or m in stack:
            return
        for d in sorted(modules[m]['depends']):
            visit(d, stack + (m,))
        done.add(m)
        order.append(m)
    for m in sorted(modules):
        visit(m)
    return order


def trace(out, model, method):
    """Трасса от точки входа: переопределения по MRO, вызовы, записи и их триггеры."""
    order = load_order(out['modules'])
    chain = sorted((c for c in out['classes'] if c['model'] == model and method in c['methods']),
                   key=lambda c: order.index(c['module']), reverse=True)
    p = [f'\n## Трасса `{model}.{method}()`\n']
    entry = [(b['view'], b['where']) for b in out['buttons']
             if b['method'] == method and b['model'] == model]
    p.append('Точки входа (кнопки type="object"): ' +
             (', '.join(f'`{v}` ({w})' for v, w in entry) or '_в XML скана нет_') + '\n\n')
    p.append('Порядок вызова (MRO: модуль, загруженный последним, первым):\n\n')
    broken = False
    for i, c in enumerate(chain, 1):
        m = c['methods'][method]
        mark = ('super() → дальше' if m['super'] else 'базовая реализация'
                if c['role'] == 'определяет' else 'без super(): ниже не идёт')
        p.append(f"{i}. {c['module']} · `{c['class']}` · {c['file']}:{m['line']} · "
                 f"{'(не вызывается) ' if broken else ''}{mark}\n")
        broken = broken or not m['super']
    base = any(c['role'] == 'определяет' for c in chain)
    if not chain:
        p.append('_переопределений в скане нет_\n')
    if not broken and not base:
        p.append('- далее: реализация вне скана (ядро/ORM/миксин)\n')
    known = {}
    for c in out['classes']:
        for name, m in c['methods'].items():
            known.setdefault(name, []).append(f"{c['model']} {c['file']}:{m['line']}")
    calls = sorted({x for c in chain for x in c['methods'][method]['calls']
                    if x in known and x != method})
    p.append('\nВызывает методы из скана: ' + ('; '.join(
        f"`{x}` ({', '.join(known[x])})" for x in calls) or '_нет_') + '\n')
    cmap, targets = comodels(out), {}
    for c in chain:
        for tgt, keys in c['methods'][method]['writes'].items():
            env = re.fullmatch(r"env\[['\"]([\w.]+)['\"]\]", tgt)
            tmodel = model if tgt == 'self' else env.group(1) if env else \
                cmap.get(model, {}).get(tgt, f'? ({tgt})')
            targets.setdefault(tmodel, set()).update(keys)
    for tmodel, keys in sorted(targets.items()):
        p.append(write_triggers(out, tmodel, sorted(keys)))
    p.append('\nНе доказано: порядок модулей без связи через depends; переопределения в '
             'ядре и вне скана; вызовы через переменные, getattr, серверные действия, '
             'cron и JS; присваивания rec.field = … (не write) и их триггеры.\n')
    return ''.join(p)


def write_triggers(out, model, writes):
    """Что сработает при записи полей writes модели model: depends/constrains/onchange, related."""
    rows, cmap = [], comodels(out)
    for c in out['classes']:
        for d in c['decos']:
            for a in d['args']:
                hit = (c['model'] == model and a.split('.')[0] in writes) or (
                    a.split('.')[-1] in writes and model in walk_path(cmap, c['model'], a))
                if hit:
                    rows.append((c['model'], d['kind'], d['method'], a, f"{c['file']}:{d['line']}"))
    rows += [(r[0], 'related', r[1], r[2], r[3]) for r in through_paths(out, model)
             if r[1].startswith('related') and r[2].split('.')[-1] in writes]
    return (f"\nПишет в `{model}` поля {', '.join(f'`{w}`' for w in writes)} → неявные триггеры:\n\n"
            + table(['модель', 'что', 'метод/поле', 'путь', 'где'], rows))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='каталоги аддонов или модулей')
    ap.add_argument('--model', help='показать только то, что касается модели')
    ap.add_argument('--field', help='с --model: все упоминания поля по имени')
    ap.add_argument('--trace', metavar='METHOD',
                    help='с --model: трасса метода (переопределения, вызовы, триггеры)')
    ap.add_argument('--odoo', type=int, metavar='SERIES',
                    help='серия Odoo (18, 19…) вместо version из __manifest__.py')
    args = ap.parse_args(argv)
    sys.stdout.write(render(scan(args.paths, args.odoo), args.model, args.field, args.trace))
    return 0


if __name__ == '__main__':
    sys.exit(main())

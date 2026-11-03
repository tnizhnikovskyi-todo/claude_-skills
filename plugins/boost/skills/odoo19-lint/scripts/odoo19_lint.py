#!/usr/bin/env python3
"""odoo19-lint: ловушки Odoo 19 в файлах модуля (Python, XML, CSV, манифест).

Только stdlib. Анализируемый код не импортируется и не исполняется:
Python разбирается через ast/tokenize, XML через expat, манифест через
ast.literal_eval, CSV через csv.

    python3 -I odoo19_lint.py PATH [PATH ...]      # файлы или каталоги
    python3 -I odoo19_lint.py PATH --json          # машинный вывод
    python3 -I odoo19_lint.py --rules              # список правил с источниками

Код выхода: 1 — есть находки уровня ERROR, 0 — нет (WARN не валит).
Подавить находку на строке: комментарий `odoo19-lint: ignore`.

Каждое правило сверено с исходниками odoo/odoo ветки 19.0
(коммит e0b25b7, 2026-11-03); источник печатается в каждой находке.
"""
import argparse
import ast
import csv
import io
import json
import os
import re
import sys
from xml.parsers import expat

SRC = 'odoo/odoo@19.0:'
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'static'}
IGNORE_MARK = 'odoo19-lint: ignore'

# id: (уровень, что не так, как исправить, источник)
RULES = {
    'view-tree': (
        'ERROR', 'тег <tree> (или xpath на tree): в 19.0 тип вью называется list',
        '<tree> → <list>, xpath "//tree" → "//list"',
        SRC + 'odoo/addons/base/models/ir_ui_view.py:149-156 (type: list, без tree), :610-617 (Invalid view type)'),
    'view-mode-tree': (
        'ERROR', "режим 'tree' в view_mode/views действия: вида tree в 19.0 нет",
        "view_mode 'tree,form' → 'list,form'; (False, 'tree') → (False, 'list')",
        SRC + 'odoo/addons/base/models/ir_actions.py:318 (default list,form), :401-408 (VIEW_TYPES); '
              'odoo/addons/base/models/ir_ui_view.py:3054-3058 (No default view of type)'),
    'tree-view-ref': (
        'WARN', 'ключ контекста tree_view_ref больше не читается (ищется list_view_ref), вью молча не та',
        'tree_view_ref → list_view_ref',
        SRC + 'odoo/addons/base/models/ir_ui_view.py:3024-3026 (view_ref_key = view_type + "_view_ref")'),
    'view-attrs-states': (
        'ERROR', 'атрибут attrs=/states= во вью: с 17.0 вью с ними не проходит проверку',
        'attrs="{\'invisible\': [...]}" → invisible="выражение"; states="draft" → invisible="state != \'draft\'"',
        SRC + 'odoo/addons/base/models/ir_ui_view.py:495-499'),
    'route-type-json': (
        'WARN', "@route(type='json') — устаревший алиас в 19.0 (DeprecationWarning)",
        "type='json' → type='jsonrpc'",
        SRC + 'odoo/http.py:812-818'),
    'sql-constraints': (
        'ERROR', '_sql_constraints в 19.0 игнорируется целиком (только warning в логе): ограничения в БД не будет',
        "_name_uniq = models.Constraint('UNIQUE(name)', 'сообщение') (атрибут класса); индексы — models.Index",
        SRC + 'odoo/orm/model_classes.py:159-164'),
    'partner-mobile-title': (
        'ERROR', 'у res.partner в 19.0 нет полей mobile и title: related/depends/вью с ними не установятся',
        'mobile → phone (или своё поле); title → убрать или своё поле; не ссылаться на partner.mobile/title',
        SRC + 'odoo/addons/base/models/res_partner.py:184-313 (поля ResPartner: phone :276, mobile/title нет; '
              'ни один addons/*/models/*.py 19.0 их не добавляет)'),
    'groups-fields': (
        'ERROR', 'поля прав, переименованные в 19.0: res.groups.users/category_id, *.groups_id',
        'res.groups: users → user_ids, category_id → privilege_id (запись res.groups.privilege с category_id); '
        'res.users / ir.ui.menu / ir.actions.* / ir.ui.view: groups_id → group_ids',
        SRC + 'odoo/addons/base/models/res_groups.py:17,36; res_groups_privilege.py:13; res_users.py:257; '
              'ir_ui_menu.py:29; ir_actions.py:329,661; ir_actions_report.py:183; ir_ui_view.py:175'),
    'inherit-list-no-name': (
        'ERROR', '_inherit списком без _name: в 19.0 это НОВАЯ модель с именем из имени класса, а не расширение',
        "расширение: _inherit = 'x' строкой, или явно _name = 'x' + _inherit = ['x', 'mail.thread']",
        SRC + 'odoo/orm/models.py:241-249'),
    'inherit-list-implicit-name': (
        'WARN', '_inherit списком без _name: имя модели выводится из имени класса (совпало, но с warning)',
        "добавить явный _name = '<модель>' или _inherit = '<модель>' строкой",
        SRC + 'odoo/orm/models.py:241-249'),
    'cron-numbercall': (
        'ERROR', 'у ir.cron в 19.0 нет numbercall/doall: запись крона не загрузится',
        'убрать numbercall/doall; крон бессрочный, пока active; разовый — деактивировать в коде',
        SRC + 'odoo/addons/base/models/ir_cron.py:99-122 (поля IrCron, _inherits ir.actions.server); numbercall/doall в odoo/ 19.0 нет'),
    'name-get': (
        'ERROR', 'name_get в 19.0 не существует: переопределение не вызывается, вызов падает AttributeError',
        'переопределить _compute_display_name (+ @api.depends), читать record.display_name',
        SRC + 'odoo/orm/models.py:1438 (_compute_display_name); name_get в odoo/ 19.0 не определён'),
    'read-group': (
        'WARN', 'read_group() устарел в 19.0',
        '_read_group(domain, groupby, aggregates) в бэкенде или formatted_read_group для UI',
        SRC + 'odoo/orm/models.py:2754-2755'),
    'private-env': (
        'WARN', 'self._context / self._cr / self._uid устарели в 19.0',
        'self.env.context / self.env.cr / self.env.uid',
        SRC + 'odoo/orm/models.py:5930-5943'),
    'toggle-active': (
        'WARN', 'toggle_active() устарел в 19.0',
        'action_archive() / action_unarchive()',
        SRC + 'odoo/orm/models.py:5807-5813'),
    'notify-progress': (
        'WARN', 'ir.cron._notify_progress() устарел в 19.0',
        'self.env["ir.cron"]._commit_progress(processed=..., remaining=...)',
        SRC + 'odoo/addons/base/models/ir_cron.py:823-824, :846 (_commit_progress)'),
    'api-returns': (
        'ERROR', 'декоратора @api.returns в 19.0 нет: AttributeError при импорте модуля',
        'убрать @api.returns',
        SRC + 'odoo/api/__init__.py:5-17 (экспортируемые декораторы, returns нет)'),
    'user-has-groups': (
        'ERROR', 'user_has_groups() в 19.0 нет: AttributeError',
        "self.env.user.has_group('module.group') или has_groups('a,!b')",
        SRC + 'odoo/addons/base/models/res_users.py:1034,1066; user_has_groups в 19.0 не определён'),
    'group-operator': (
        'WARN', "параметр поля group_operator устарел (с 18.0)",
        "group_operator='sum' → aggregator='sum'",
        SRC + 'odoo/orm/fields.py:485-487'),
    'product-type': (
        'ERROR', "detailed_type и type='product' в 19.0 нет: товар с учётом остатков задаётся иначе",
        "type='consu' + is_storable=True (поле из stock)",
        SRC + 'addons/product/models/product_template.py:58-65 (type: consu/service/combo); '
              'addons/stock/models/product.py:834 (is_storable)'),
    'uom-fields': (
        'ERROR', 'у uom.uom в 19.0 нет category_id / uom_type / factor_inv: категории единиц удалены',
        'relative_factor + relative_uom_id (например 6 × uom.product_uom_unit)',
        SRC + 'addons/uom/models/uom_uom.py:34-44 (поля UomUom)'),
    'line-product-uom': (
        'ERROR', 'у sale.order.line / purchase.order.line в 19.0 поле единицы называется product_uom_id',
        'product_uom → product_uom_id (у stock.move по-прежнему product_uom)',
        SRC + 'addons/sale/models/sale_order_line.py:132; addons/purchase/models/purchase_order_line.py:43; '
              'addons/stock/models/stock_move.py:67'),
    'manifest-hook-path': (
        'ERROR', 'хук в манифесте задан путём с точкой: загрузчик ищет getattr(модуль, имя) — AttributeError',
        "'pre_init_hook': 'my_module.hooks.pre_init' → 'pre_init' (функция импортирована в __init__.py)",
        SRC + 'odoo/modules/loading.py:182-185'),
}

# Поля, которых нет у модели в 19.0: (модель, поле) -> правило.
BAD_FIELDS = {
    ('res.partner', 'mobile'): 'partner-mobile-title',
    ('res.partner', 'title'): 'partner-mobile-title',
    ('res.groups', 'users'): 'groups-fields',
    ('res.groups', 'category_id'): 'groups-fields',
    ('res.groups', 'groups_id'): 'groups-fields',
    ('res.users', 'groups_id'): 'groups-fields',
    ('ir.ui.menu', 'groups_id'): 'groups-fields',
    ('ir.ui.view', 'groups_id'): 'groups-fields',
    ('ir.actions.act_window', 'groups_id'): 'groups-fields',
    ('ir.actions.server', 'groups_id'): 'groups-fields',
    ('ir.actions.report', 'groups_id'): 'groups-fields',
    ('ir.actions.client', 'groups_id'): 'groups-fields',
    ('ir.actions.act_url', 'groups_id'): 'groups-fields',
    ('ir.cron', 'numbercall'): 'cron-numbercall',
    ('ir.cron', 'doall'): 'cron-numbercall',
    ('product.template', 'detailed_type'): 'product-type',
    ('product.product', 'detailed_type'): 'product-type',
    ('uom.uom', 'category_id'): 'uom-fields',
    ('uom.uom', 'uom_type'): 'uom-fields',
    ('uom.uom', 'factor_inv'): 'uom-fields',
    ('sale.order.line', 'product_uom'): 'line-product-uom',
    ('purchase.order.line', 'product_uom'): 'line-product-uom',
}
LINE_MODELS = {'sale.order.line', 'purchase.order.line'}
ORDER_MODELS = {'sale.order', 'purchase.order'} | LINE_MODELS
PARTNER_RE = re.compile(r'(?<!\w)(\w+)\.(mobile|title)\b(?!\s*\()')


class Linter:
    def __init__(self):
        self.findings = []
        self.files = 0
        self.skipped = []
        # поля, которые сам сканируемый код добавляет моделям: подавляет ложные срабатывания
        self.defined = set()
        # имена полей Many2one('res.partner') в сканируемом коде (driver_id, customer_id…)
        self.partner_fields = set()

    def add(self, path, line, rule, detail='', lines=None):
        if lines is not None and 0 < line <= len(lines) and IGNORE_MARK in lines[line - 1]:
            return
        self.findings.append({'file': path, 'line': line, 'rule': rule,
                              'severity': RULES[rule][0], 'detail': detail})

    def is_partner(self, name):
        return 'partner' in name.lower() or name in self.partner_fields

    def partner_hits(self, text):
        return [m for m in PARTNER_RE.finditer(text)
                if self.is_partner(m.group(1)) and self.field_missing('res.partner', m.group(2))]

    def field_missing(self, model, field):
        rule = BAD_FIELDS.get((model, field))
        if rule and (model, field) not in self.defined:
            return rule
        return None


# ---------------------------------------------------------------- Python

def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    elif isinstance(node, ast.Call):
        parts.append('()')
    return '.'.join(reversed(parts))


def const_str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def class_models(cls):
    """(_name, [_inherit], имеет_ли _name) из тела класса."""
    name, inherit, inherit_is_list = None, [], False
    for stmt in cls.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            key = stmt.targets[0].id
            try:
                val = ast.literal_eval(stmt.value)
            except (ValueError, SyntaxError, TypeError):
                continue
            if key == '_name' and isinstance(val, str):
                name = val
            elif key == '_inherit':
                if isinstance(val, str):
                    inherit = [val]
                elif isinstance(val, (list, tuple)):
                    inherit = [v for v in val if isinstance(v, str)]
                    inherit_is_list = True
    return name, inherit, inherit_is_list


def is_model_class(cls):
    for base in cls.bases:
        if dotted(base).split('.')[-1] in ('Model', 'AbstractModel', 'TransientModel'):
            return True
    return False


def implicit_name(class_name):
    return re.sub(r'(?<=[^_])([A-Z])', r'.\1', class_name).lower()


def env_model(node):
    """Имя модели из env['x'] где-то в цепочке вызова: self.env['x'].create -> 'x'."""
    while isinstance(node, (ast.Attribute, ast.Call, ast.Subscript)):
        if isinstance(node, ast.Subscript):
            model = const_str(node.slice)
            if model and dotted(node.value).endswith('env'):
                return model
            node = node.value
        elif isinstance(node, ast.Attribute):
            node = node.value
        else:
            node = node.func
    return None


def collect_defined(tree, linter):
    for cls in ast.walk(tree):
        if not (isinstance(cls, ast.ClassDef) and is_model_class(cls)):
            continue
        name, inherit, _ = class_models(cls)
        models = {name} if name else set(inherit)
        for stmt in cls.body:
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name) and isinstance(stmt.value, ast.Call)
                    and dotted(stmt.value.func).startswith('fields.')):
                for m in models:
                    linter.defined.add((m, stmt.targets[0].id))
                call = stmt.value
                comodel = const_str(call.args[0]) if call.args else None
                for kw in call.keywords:
                    if kw.arg == 'comodel_name':
                        comodel = const_str(kw.value)
                if dotted(call.func).endswith('Many2one') and comodel == 'res.partner':
                    linter.partner_fields.add(stmt.targets[0].id)


def docstring_lines(tree):
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and const_str(body[0].value) is not None:
                lines.update(range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1))
    return lines


def check_python(path, text, linter):
    lines = text.splitlines()
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        linter.skipped.append(f'{path}: SyntaxError {exc.lineno}')
        return
    doc = docstring_lines(tree)
    called = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}

    # классы: _inherit, _sql_constraints, name_get, поля линий заказа
    line_classes = []
    for cls in ast.walk(tree):
        if not (isinstance(cls, ast.ClassDef) and is_model_class(cls)):
            continue
        name, inherit, inherit_is_list = class_models(cls)
        if inherit_is_list and not name and inherit:
            derived = implicit_name(cls.name)
            if derived in inherit:
                linter.add(path, cls.lineno, 'inherit-list-implicit-name',
                           f'класс {cls.name} → модель {derived!r}', lines)
            else:
                linter.add(path, cls.lineno, 'inherit-list-no-name',
                           f'класс {cls.name} создаст новую модель {derived!r}, а не расширит {inherit}', lines)
        if (name or (inherit[0] if inherit else None)) in LINE_MODELS or set(inherit) & LINE_MODELS:
            line_classes.append(cls)
        for stmt in cls.body:
            if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_sql_constraints'
                                                    for t in stmt.targets):
                linter.add(path, stmt.lineno, 'sql-constraints', '', lines)
            if isinstance(stmt, ast.FunctionDef) and stmt.name == 'name_get':
                linter.add(path, stmt.lineno, 'name-get', 'переопределение name_get никогда не вызовется', lines)

    for cls in line_classes:
        for node in ast.walk(cls):
            if isinstance(node, ast.Attribute) and node.attr == 'product_uom' and \
                    ('sale.order.line', 'product_uom') not in linter.defined and is_line_ref(node.value):
                linter.add(path, node.lineno, 'line-product-uom', dotted(node), lines)
        # строки 'product_uom' в @api.depends/@api.onchange и related= (не ключи vals для stock.move)
        for fn in cls.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            for dec in fn.decorator_list:
                if isinstance(dec, ast.Call) and dotted(dec.func).split('.')[-1] in ('depends', 'onchange'):
                    for a in dec.args:
                        s = const_str(a)
                        if s and s.split('.')[-1] == 'product_uom' and not s.startswith('move'):
                            linter.add(path, a.lineno, 'line-product-uom', repr(s), lines)

    for node in ast.walk(tree):
        # декораторы
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                dn = dotted(target)
                if dn in ('api.returns', 'returns'):
                    linter.add(path, dec.lineno, 'api-returns', '', lines)
                if isinstance(dec, ast.Call) and dn.split('.')[-1] == 'route':
                    for kw in dec.keywords:
                        if kw.arg == 'type' and const_str(kw.value) == 'json':
                            linter.add(path, dec.lineno, 'route-type-json', '', lines)

        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                attr = func.attr
                if attr == 'read_group':
                    linter.add(path, node.lineno, 'read-group', dotted(func), lines)
                elif attr == 'toggle_active':
                    linter.add(path, node.lineno, 'toggle-active', dotted(func), lines)
                elif attr == '_notify_progress':
                    linter.add(path, node.lineno, 'notify-progress', dotted(func), lines)
                elif attr == 'name_get':
                    linter.add(path, node.lineno, 'name-get', dotted(func) + '()', lines)
                elif attr == 'user_has_groups':
                    linter.add(path, node.lineno, 'user-has-groups', dotted(func), lines)
                elif attr in ('create', 'write', 'search', 'search_read', 'read', 'mapped', 'filtered_domain'):
                    model = env_model(func.value)
                    if model:
                        check_call_fields(path, node, model, linter, lines)
            if dotted(func).startswith('fields.'):
                for kw in node.keywords:
                    if kw.arg == 'group_operator':
                        linter.add(path, node.lineno, 'group-operator', '', lines)

        elif isinstance(node, ast.Attribute) and id(node) not in called:
            if node.attr in ('_context', '_cr', '_uid') and isinstance(node.value, ast.Name):
                linter.add(path, node.lineno, 'private-env', f'{node.value.id}.{node.attr}', lines)
            base = dotted(node.value)
            last = base.split('.')[-1] if base else ''
            if node.attr in ('mobile', 'title') and linter.is_partner(last):
                if linter.field_missing('res.partner', node.attr):
                    linter.add(path, node.lineno, 'partner-mobile-title', f'{base}.{node.attr}', lines)
            elif node.attr == 'groups_id' and ('res.users', 'groups_id') not in linter.defined \
                    and not any(f == 'groups_id' for _, f in linter.defined):
                linter.add(path, node.lineno, 'groups-fields', f'{base}.groups_id → group_ids', lines)
            elif node.attr == 'users' and ('group' in last.lower() or base.endswith('ref.()')):
                linter.add(path, node.lineno, 'groups-fields', f'{base}.users → user_ids', lines)
            elif node.attr == 'category_id' and 'group' in last.lower() and not last.lower().endswith('privilege'):
                linter.add(path, node.lineno, 'groups-fields', f'{base}.category_id → privilege_id.category_id', lines)
            elif node.attr == 'category_id' and 'uom' in last.lower():
                linter.add(path, node.lineno, 'uom-fields', f'{base}.category_id', lines)
            elif node.attr in ('factor_inv', 'uom_type') and ('uom.uom', node.attr) not in linter.defined:
                linter.add(path, node.lineno, 'uom-fields', f'{base}.{node.attr}', lines)
            elif node.attr == 'detailed_type' and ('product.template', 'detailed_type') not in linter.defined:
                linter.add(path, node.lineno, 'product-type', f'{base}.detailed_type', lines)

        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                key = const_str(k) if k is not None else None
                val = const_str(v)
                if key == 'view_mode' and val and 'tree' in val.split(','):
                    linter.add(path, k.lineno, 'view-mode-tree', repr(val), lines)
                elif key in ('numbercall', 'doall'):
                    linter.add(path, k.lineno, 'cron-numbercall', repr(key), lines)
                elif key == 'detailed_type' and ('product.template', 'detailed_type') not in linter.defined:
                    linter.add(path, k.lineno, 'product-type', repr(key), lines)
                elif key == 'tree_view_ref':
                    linter.add(path, k.lineno, 'tree-view-ref', '', lines)
                elif key == 'views' and isinstance(v, (ast.List, ast.Tuple)):
                    for elt in v.elts:
                        if isinstance(elt, ast.Tuple) and len(elt.elts) == 2 and const_str(elt.elts[1]) == 'tree':
                            linter.add(path, elt.lineno, 'view-mode-tree', "(…, 'tree')", lines)

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.lineno in doc:
                continue
            s = node.value
            for m in linter.partner_hits(s):
                linter.add(path, node.lineno, 'partner-mobile-title', repr(m.group(0)), lines)
            if 'tree_view_ref' in s and not s.strip() == 'tree_view_ref':
                linter.add(path, node.lineno, 'tree-view-ref', '', lines)
            if re.search(r'//tree\b|<tree[\s>/]', s):
                linter.add(path, node.lineno, 'view-tree', repr(s[:60]), lines)


def is_line_ref(node):
    """self.product_uom / line.product_uom — да; move.product_uom (stock.move) — нет."""
    last = dotted(node).split('.')[-1].lower()
    if 'move' in last:
        return False
    return last in ('self', 'rec', 'record', 'sol', 'pol') or last.endswith(('line', 'lines', 'line_id', 'line_ids'))


def check_call_fields(path, call, model, linter, lines):
    """self.env['res.groups'].create({'users': ...}) и т.п."""
    for arg in list(call.args) + [kw.value for kw in call.keywords]:
        for sub in ast.walk(arg):
            names = []
            if isinstance(sub, ast.Dict):
                names = [(const_str(k), k) for k in sub.keys if k is not None]
            elif isinstance(sub, ast.Tuple) and sub.elts:
                names = [(const_str(sub.elts[0]), sub.elts[0])]
            elif isinstance(sub, ast.Constant):
                names = [(const_str(sub), sub)]
            for fname, n in names:
                if not fname:
                    continue
                rule = linter.field_missing(model, fname.split('.')[0])
                if rule:
                    linter.add(path, n.lineno, rule, f"{model}.{fname}", lines)


# ---------------------------------------------------------------- XML

class Node:
    __slots__ = ('tag', 'attrib', 'line', 'children', 'text', 'parent')

    def __init__(self, tag, attrib, line, parent):
        self.tag, self.attrib, self.line, self.parent = tag, attrib, line, parent
        self.children, self.text = [], ''

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()


def parse_xml(data):
    parser = expat.ParserCreate()
    root = Node('#doc', {}, 0, None)
    stack = [root]
    comments = []

    def start(tag, attrib):
        node = Node(tag, attrib, parser.CurrentLineNumber, stack[-1])
        stack[-1].children.append(node)
        stack.append(node)

    def end(_tag):
        stack.pop()

    def chars(text):
        stack[-1].text += text

    def comment(text):
        comments.append((parser.CurrentLineNumber, text))

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = chars
    parser.CommentHandler = comment
    parser.Parse(data, True)
    return root


def record_fields(rec):
    return [c for c in rec.children if c.tag == 'field' and 'name' in c.attrib]


def field_value(f):
    return (f.attrib.get('eval') or f.attrib.get('ref') or f.text or '').strip()


def check_xml(path, data, linter):
    lines = data.decode('utf-8', 'replace').splitlines()
    try:
        root = parse_xml(data)
    except expat.ExpatError as exc:
        linter.skipped.append(f'{path}: XML {exc}')
        return
    for node in root.iter():
        if node.tag == 'record':
            check_record(path, node, linter, lines)
        elif node.tag in ('template',):
            pass
        for key, val in node.attrib.items():
            if key == 'context' and 'tree_view_ref' in val:
                linter.add(path, node.line, 'tree-view-ref', '', lines)


def check_record(path, rec, linter, lines):
    model = rec.attrib.get('model', '')
    fields = record_fields(rec)
    byname = {f.attrib['name']: f for f in fields}
    for f in fields:
        rule = linter.field_missing(model, f.attrib['name'])
        if rule:
            linter.add(path, f.line, rule, f"{model}: <field name=\"{f.attrib['name']}\">", lines)
    if model in ('product.template', 'product.product') and 'type' in byname:
        val = field_value(byname['type']).strip('\'"')
        if val == 'product':
            linter.add(path, byname['type'].line, 'product-type', "type='product'", lines)
    if model in ('ir.actions.act_window', 'ir.actions.act_window.view') and 'view_mode' in byname:
        modes = field_value(byname['view_mode']).strip('\'"')
        if 'tree' in [m.strip() for m in modes.split(',')]:
            linter.add(path, byname['view_mode'].line, 'view-mode-tree', repr(modes), lines)
    if model in ('ir.actions.act_window',) and 'context' in byname and 'tree_view_ref' in field_value(byname['context']):
        linter.add(path, byname['context'].line, 'tree-view-ref', '', lines)
    if model == 'ir.ui.view' and 'arch' in byname:
        view_model = field_value(byname['model']) if 'model' in byname else ''
        inherit = field_value(byname['inherit_id']) if 'inherit_id' in byname else ''
        if not view_model and inherit.startswith('base.view_partner'):
            view_model = 'res.partner'
        check_arch(path, byname['arch'], view_model, linter, lines)


def check_arch(path, arch, view_model, linter, lines):
    for node in arch.iter():
        if node is arch:
            continue
        if node.tag == 'tree':
            linter.add(path, node.line, 'view-tree', '<tree>', lines)
        for key in ('attrs', 'states'):
            if key in node.attrib:
                linter.add(path, node.line, 'view-attrs-states', f'{key}="{node.attrib[key][:40]}"', lines)
        if node.tag == 'attribute' and node.attrib.get('name') in ('attrs', 'states'):
            linter.add(path, node.line, 'view-attrs-states', f'<attribute name="{node.attrib["name"]}">', lines)
        expr = node.attrib.get('expr', '')
        if re.search(r'(^|/)tree\b', expr):
            linter.add(path, node.line, 'view-tree', f'xpath {expr!r}', lines)
        if expr and view_model in ORDER_MODELS and re.search(r"@name=['\"]product_uom['\"]", expr):
            linter.add(path, node.line, 'line-product-uom', f'xpath {expr!r}', lines)
        if expr and view_model == 'res.partner' and re.search(r"field\[@name=['\"](mobile|title)['\"]", expr):
            linter.add(path, node.line, 'partner-mobile-title', f'xpath {expr!r}', lines)
        if node.tag == 'field' and 'name' in node.attrib:
            fname = node.attrib['name']
            if view_model == 'res.partner' and fname in ('mobile', 'title') and \
                    linter.field_missing('res.partner', fname) and not inside_subview(node, arch):
                linter.add(path, node.line, 'partner-mobile-title', f'<field name="{fname}"> во вью res.partner', lines)
            if fname == 'product_uom' and view_model in ORDER_MODELS and \
                    ('sale.order.line', 'product_uom') not in linter.defined:
                linter.add(path, node.line, 'line-product-uom', f'<field name="product_uom"> во вью {view_model}', lines)
            if linter.partner_hits(fname):
                linter.add(path, node.line, 'partner-mobile-title', f'<field name="{fname}">', lines)
        ctx = node.attrib.get('context', '')
        if 'tree_view_ref' in ctx:
            linter.add(path, node.line, 'tree-view-ref', '', lines)


def inside_subview(node, arch):
    """Поле внутри вложенного вью One2many (child_ids) относится к другой модели — не судим."""
    p = node.parent
    while p is not None and p is not arch:
        if p.tag == 'field':
            return True
        p = p.parent
    return False


# ---------------------------------------------------------------- CSV и манифест

def check_csv(path, text, linter):
    model = os.path.splitext(os.path.basename(path))[0]
    try:
        header = next(csv.reader(io.StringIO(text)), [])
    except csv.Error:
        return
    lines = text.splitlines()
    for col in header:
        fname = col.strip().split(':')[0].split('/')[0]
        rule = linter.field_missing(model, fname)
        if rule:
            linter.add(path, 1, rule, f'{model}.csv: колонка {col!r}', lines)


def check_manifest(path, text, linter):
    lines = text.splitlines()
    try:
        data = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        linter.skipped.append(f'{path}: манифест не литерал')
        return
    if not isinstance(data, dict):
        return
    for key in ('pre_init_hook', 'post_init_hook', 'uninstall_hook', 'post_load'):
        val = data.get(key)
        if isinstance(val, str) and '.' in val:
            line = next((i + 1 for i, l in enumerate(lines) if key in l), 1)
            linter.add(path, line, 'manifest-hook-path', f'{key}: {val!r}', lines)


# ---------------------------------------------------------------- обход

def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                if fn.endswith(('.py', '.xml', '.csv')):
                    yield os.path.join(dirpath, fn)


def lint(paths):
    linter = Linter()
    files = list(iter_files(paths))
    texts = {}
    for f in files:
        try:
            with open(f, 'rb') as fh:
                texts[f] = fh.read()
        except OSError as exc:
            linter.skipped.append(f'{f}: {exc}')
    # 1-й проход: какие поля добавляет сам сканируемый код
    for f, data in texts.items():
        if f.endswith('.py') and not f.endswith('__manifest__.py'):
            try:
                collect_defined(ast.parse(data), linter)
            except SyntaxError:
                pass
    for f, data in texts.items():
        linter.files += 1
        if f.endswith('__manifest__.py'):
            check_manifest(f, data.decode('utf-8', 'replace'), linter)
        elif f.endswith('.py'):
            check_python(f, data.decode('utf-8', 'replace'), linter)
        elif f.endswith('.xml'):
            check_xml(f, data, linter)
        elif f.endswith('.csv'):
            check_csv(f, data.decode('utf-8', 'replace'), linter)
    # дубли (одна строка, одно правило) убираем
    seen, uniq = set(), []
    for x in linter.findings:
        key = (x['file'], x['line'], x['rule'])
        if key not in seen:
            seen.add(key)
            uniq.append(x)
    linter.findings = sorted(uniq, key=lambda x: (x['severity'] != 'ERROR', x['file'], x['line']))
    return linter


def print_text(linter, out=None):
    out = out or sys.stdout
    errors = sum(1 for x in linter.findings if x['severity'] == 'ERROR')
    warns = len(linter.findings) - errors
    print(f'odoo19-lint: {errors} ERROR, {warns} WARN; файлов просмотрено: {linter.files}', file=out)
    for x in linter.findings:
        sev, what, fix, src = RULES[x['rule']]
        detail = f' — {x["detail"]}' if x['detail'] else ''
        print(f'\n{sev} [{x["rule"]}] {x["file"]}:{x["line"]}{detail}', file=out)
        print(f'  что: {what}', file=out)
        print(f'  исправить: {fix}', file=out)
        print(f'  источник: {src}', file=out)
    if linter.skipped:
        print('\nНе разобрано: ' + '; '.join(linter.skipped), file=out)
    print('\nНе проверяет: поля и модели вне переданных путей (ядро, enterprise, другие аддоны), '
          'код, собранный динамически, JS/OWL. Отсутствие находок ≠ модуль установится.', file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Ловушки Odoo 19 в файлах модуля (stdlib, код не исполняется).')
    ap.add_argument('paths', nargs='*', help='файлы или каталоги модуля/аддонов')
    ap.add_argument('--json', action='store_true', help='вывод JSON')
    ap.add_argument('--rules', action='store_true', help='список правил с источниками')
    args = ap.parse_args(argv)
    if args.rules:
        for rid, (sev, what, fix, src) in RULES.items():
            print(f'{rid} [{sev}]\n  что: {what}\n  исправить: {fix}\n  источник: {src}\n')
        return 0
    if not args.paths:
        ap.error('нужен путь к модулю или каталогу аддонов')
    linter = lint(args.paths)
    if args.json:
        print(json.dumps({'findings': [dict(x, what=RULES[x['rule']][1], fix=RULES[x['rule']][2],
                                            source=RULES[x['rule']][3]) for x in linter.findings],
                          'files': linter.files, 'skipped': linter.skipped}, ensure_ascii=False, indent=1))
    else:
        print_text(linter)
    return 1 if any(x['severity'] == 'ERROR' for x in linter.findings) else 0


if __name__ == '__main__':
    sys.exit(main())

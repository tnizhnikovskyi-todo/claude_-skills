"""Тест скрипта odoo19_lint.py на фикстурах tests/bad и tests/good.

    python3 -I -m unittest discover -s plugins/boost/evals/odoo19-lint -p 'test_*.py'

bad/  — по позитивному примеру на каждое правило;
good/ — тот же модуль, написанный правильно для Odoo 19: ни одной находки.
"""
import contextlib
import importlib.util
import io
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BAD = os.path.join(HERE, 'tests', 'bad')
GOOD = os.path.join(HERE, 'tests', 'good')
PILOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'pilot', 'addons'))
SCRIPT = os.path.join(HERE, '..', '..', 'skills', 'odoo19-lint', 'scripts', 'odoo19_lint.py')

spec = importlib.util.spec_from_file_location('odoo19_lint', SCRIPT)
lint_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_mod)

# правило -> (файл относительно td_lint/, строка) позитивного примера в bad/
EXPECTED = {
    'view-tree': [('views/views.xml', 7), ('views/views.xml', 32)],
    'view-mode-tree': [('views/views.xml', 56), ('models/models.py', 49)],
    'tree-view-ref': [('views/views.xml', 57), ('models/models.py', 50)],
    'view-attrs-states': [('views/views.xml', 18), ('views/views.xml', 20), ('views/views.xml', 36)],
    'route-type-json': [('controllers/main.py', 5)],
    'sql-constraints': [('models/models.py', 7)],
    'partner-mobile-title': [('models/models.py', 12), ('models/models.py', 13), ('models/models.py', 31),
                             ('views/views.xml', 30), ('views/views.xml', 49), ('models/models.py', 82)],
    'groups-fields': [('models/models.py', 25), ('models/models.py', 28), ('security/security.xml', 8),
                      ('security/security.xml', 14), ('security/security.xml', 17), ('views/views.xml', 58),
                      ('security/res.groups.csv', 1)],
    'inherit-list-no-name': [('models/models.py', 54)],
    'inherit-list-implicit-name': [('models/models.py', 71)],
    'cron-numbercall': [('data/data.xml', 10), ('data/data.xml', 11)],
    'name-get': [('models/models.py', 16)],
    'read-group': [('models/models.py', 35)],
    'private-env': [('models/models.py', 34)],
    'toggle-active': [('models/models.py', 38)],
    'notify-progress': [('models/models.py', 41)],
    'api-returns': [('models/models.py', 19)],
    'user-has-groups': [('models/models.py', 44)],
    'group-operator': [('models/models.py', 14)],
    'product-type': [('data/data.xml', 21), ('data/data.xml', 22)],
    'uom-fields': [('data/data.xml', 15), ('data/data.xml', 16), ('data/data.xml', 17)],
    'line-product-uom': [('models/models.py', 65), ('models/models.py', 68), ('views/views.xml', 45)],
    'manifest-hook-path': [('__manifest__.py', 4)],
    # второй круг
    'manifest-version': [('__manifest__.py', 5)],
    'removed-module': [('__manifest__.py', 6)],
    'old-constraints': [('models/round2.py', 9)],
    'digits-uom': [('models/round2.py', 12)],
    'fields-date-alias': [('models/round2.py', 13)],
    'api-model-create': [('models/round2.py', 15)],
    'default-get-kwarg': [('models/round2.py', 22)],
    'models-newid': [('models/round2.py', 28)],
    'odoo-registry': [('models/round2.py', 31)],
    'default-user': [('models/round2.py', 34), ('views/round2.xml', 39)],
    'login-classmethod': [('models/round2.py', 41)],
    'line-tax-ids': [('models/round2.py', 49), ('models/round2.py', 56), ('views/round2.xml', 32)],
    'js-use-service': [('static/src/js/widget.js', 7), ('static/src/js/widget.js', 8)],
    'savepoint-case': [('tests/test_ticket.py', 1)],
    'search-group-attrs': [('views/round2.xml', 9)],
    'oe-chatter': [('views/round2.xml', 21)],
    'osv-expression': [('models/round2.py', 3)],
}


def found(linter, root):
    out = set()
    for x in linter.findings:
        rel = os.path.relpath(x['file'], os.path.join(root, 'td_lint')).replace(os.sep, '/')
        out.add((x['rule'], rel, x['line']))
    return out


class BadFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.linter = lint_mod.lint([BAD])
        cls.found = found(cls.linter, BAD)

    def test_every_rule_has_positive_example(self):
        self.assertEqual(set(EXPECTED), set(lint_mod.RULES))

    def test_expected_findings(self):
        for rule, places in EXPECTED.items():
            for rel, line in places:
                with self.subTest(rule=rule, at=f'{rel}:{line}'):
                    self.assertIn((rule, rel, line), self.found)

    def test_no_unexpected_findings(self):
        expected = {(r, rel, line) for r, places in EXPECTED.items() for rel, line in places}
        self.assertEqual(self.found - expected, set())

    def test_severity_and_source(self):
        for rid, (sev, what, fix, src) in lint_mod.RULES.items():
            with self.subTest(rule=rid):
                self.assertIn(sev, ('ERROR', 'WARN'))
                self.assertTrue(src.startswith('odoo/odoo@19.0:'), src)
                self.assertRegex(src, r':\d+')
                self.assertTrue(what and fix)

    def test_exit_code_and_text(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = lint_mod.main([BAD])
        self.assertEqual(code, 1)
        text = buf.getvalue()
        self.assertIn('исправить:', text)
        self.assertIn('источник: odoo/odoo@19.0:', text)
        self.assertIn('Не проверяет:', text)


class GoodFixture(unittest.TestCase):
    def test_correct_odoo19_code_is_clean(self):
        linter = lint_mod.lint([GOOD])
        self.assertEqual(linter.findings, [])
        self.assertEqual(linter.skipped, [])

    def test_exit_code_zero(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lint_mod.main([GOOD]), 0)


class Suppression(unittest.TestCase):
    def test_ignore_comment(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'm.py')
            with open(p, 'w', encoding='utf-8') as f:
                f.write("from odoo import fields, models\n\n\nclass A(models.Model):\n"
                        "    _name = 'a'\n"
                        "    x = fields.Char(related='partner_id.mobile')  # odoo19-lint: ignore\n"
                        "    y = fields.Char(related='partner_id.mobile')\n")
            lines = [x['line'] for x in lint_mod.lint([p], all_files=True).findings]
            self.assertEqual(lines, [7])

    def test_module_defines_mobile(self):
        """Если модуль сам добавляет res.partner.mobile, related на него не ошибка."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'm.py')
            with open(p, 'w', encoding='utf-8') as f:
                f.write("from odoo import fields, models\n\n\nclass P(models.Model):\n"
                        "    _inherit = 'res.partner'\n    mobile = fields.Char()\n\n\n"
                        "class A(models.Model):\n    _name = 'a'\n"
                        "    m = fields.Char(related='partner_id.mobile')\n")
            self.assertEqual(lint_mod.lint([p], all_files=True).findings, [])


@unittest.skipUnless(os.path.isdir(PILOT), 'pilot/addons нет рядом')
class Pilot(unittest.TestCase):
    def test_k9_only(self):
        """pilot-notes/KEYS.md: K9 — related='partner_id.mobile'; <list>, invisible=, models.Constraint верны."""
        linter = lint_mod.lint([PILOT])
        got = [(x['rule'], os.path.basename(x['file']), x['line']) for x in linter.findings]
        self.assertEqual(got, [('partner-mobile-title', 'workshop_order.py', 17)])


class EvalFixture(unittest.TestCase):
    """Ключ кейса review-module: ровно эти находки в _fixture/addons/td_rental."""

    def test_review_module_key(self):
        root = os.path.join(HERE, '_fixture', 'addons')
        got = sorted((x['rule'], os.path.relpath(x['file'], root).replace(os.sep, '/'), x['line'])
                     for x in lint_mod.lint([root]).findings)
        self.assertEqual(got, sorted([
            ('cron-numbercall', 'td_rental/data/ir_cron.xml', 10),
            ('inherit-list-no-name', 'td_rental/models/rental_kpi.py', 4),
            ('sql-constraints', 'td_rental/models/rental_order.py', 10),
            ('partner-mobile-title', 'td_rental/models/rental_order.py', 18),
            ('name-get', 'td_rental/models/rental_order.py', 41),
            ('groups-fields', 'td_rental/security/security.xml', 10),
            ('groups-fields', 'td_rental/security/security.xml', 16),
            ('groups-fields', 'td_rental/security/security.xml', 18),
            ('view-mode-tree', 'td_rental/views/rental_views.xml', 55),
            ('read-group', 'td_rental/models/rental_kpi.py', 10),
            ('private-env', 'td_rental/models/rental_order.py', 54),
            ('api-model-create', 'td_rental/models/rental_order.py', 59),
            ('search-group-attrs', 'td_rental/views/rental_views.xml', 66),
        ]))


class ReferenceFiles(unittest.TestCase):
    """Урок darwin-skill: барьер не срабатывает на справочниках, где запрещённое перечислено."""

    SKILLS = os.path.join(HERE, '..', '..', 'skills')

    def test_skills_and_references_are_clean(self):
        linter = lint_mod.lint([self.SKILLS])
        self.assertEqual(linter.findings, [])
        self.assertTrue(linter.outside)  # скрипты скиллов вне модулей Odoo — пропущены

    def test_markdown_is_never_read(self):
        files = list(lint_mod.iter_files([self.SKILLS]))
        self.assertFalse([f for f in files if f.endswith('.md')])
        rules_md = os.path.join(self.SKILLS, 'odoo19-lint', 'references', 'rules.md')
        self.assertTrue(os.path.isfile(rules_md))

    def test_all_files_flag_sees_own_script(self):
        """Без ограничения скрипт видит свои же строки-сообщения: поэтому по умолчанию только модули."""
        linter = lint_mod.lint([os.path.join(self.SKILLS, 'odoo19-lint', 'scripts')], all_files=True)
        self.assertTrue(linter.findings)


if __name__ == '__main__':
    unittest.main()

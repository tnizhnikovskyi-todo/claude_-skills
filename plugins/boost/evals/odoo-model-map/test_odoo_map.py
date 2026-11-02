"""Тест скрипта odoo_map.py на фикстуре _fixture/addons.

    python3 -I -m unittest discover -s plugins/boost/evals/odoo-model-map -p 'test_*.py'
"""
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.join(HERE, '_fixture', 'addons')
SCRIPT = os.path.join(HERE, '..', '..', 'skills', 'odoo-model-map', 'scripts', 'odoo_map.py')

spec = importlib.util.spec_from_file_location('odoo_map', SCRIPT)
odoo_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(odoo_map)


class OdooMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = odoo_map.scan([ADDONS])

    def test_manifest_depends(self):
        mods = self.out['modules']
        self.assertEqual(set(mods), {'td_fleet', 'td_fleet_service', 'td_fleet_report'})
        self.assertEqual(mods['td_fleet_report']['depends'], ['td_fleet_service'])

    def test_string_inheritance_found(self):
        ext = {(c['module'], c['class']) for c in self.out['classes']
               if c['model'] == 'td.vehicle' and c['role'] == 'расширяет'}
        # _inherit = "td.vehicle" (двойные кавычки) и _inherit = ['td.vehicle'] (список)
        self.assertEqual(ext, {('td_fleet_service', 'FleetMaintenance'),
                               ('td_fleet_report', 'MileageKpi')})

    def test_inherits_delegation(self):
        card = [c for c in self.out['classes'] if c['model'] == 'td.service.card'][0]
        self.assertEqual(card['inherits'], {'td.vehicle': 'vehicle_id'})
        self.assertEqual(card['role'], 'определяет')

    def test_multiline_comodel(self):
        f = {(c['model'], x['name']): x['comodel'] for c in self.out['classes']
             for x in c['fields']}
        self.assertEqual(f[('td.vehicle.service', 'vehicle_id')], 'td.vehicle')
        self.assertEqual(f[('td.odometer.export', 'vehicle_ids')], 'td.vehicle')

    def test_env_refs(self):
        refs = {(e['model'], e['module']) for e in self.out['env']}
        self.assertIn(('td.vehicle', 'td_fleet_report'), refs)
        self.assertIn(('td.vehicle.tag', 'td_fleet_service'), refs)

    def test_view_inheritance_chain(self):
        views = {v['id']: v['inherit'] for v in self.out['views']}
        self.assertEqual(views['td_fleet_service.td_vehicle_view_form_service'],
                         'td_fleet.td_vehicle_view_form')
        self.assertEqual(views['td_fleet_report.td_vehicle_view_form_kpi'],
                         'td_fleet_service.td_vehicle_view_form_service')
        tree = odoo_map.view_tree([v for v in self.out['views'] if v['model'] == 'td.vehicle'])
        self.assertIn('    td_fleet_report.td_vehicle_view_form_kpi', tree)

    def test_acl_and_missing(self):
        acl = {(a['model'], a['group']) for a in self.out['acl']}
        self.assertIn(('td.service.card', 'td_fleet.group_fleet_manager'), acl)
        text = odoo_map.render(self.out)
        self.assertIn('**Без строк доступа:** `td.odometer.export`', text)

    def test_rules(self):
        rules = {r['id']: (r['model'], r['groups']) for r in self.out['rules']}
        self.assertEqual(rules['td_fleet.td_vehicle_company_rule'], ('td.vehicle', 'глобальное'))
        self.assertEqual(rules['td_fleet_service.td_vehicle_service_own_rule'],
                         ('td.vehicle.service', 'base.group_user'))

    def test_paths_through_model(self):
        rows = list(odoo_map.through_paths(self.out, 'td.vehicle'))
        paths = {(r[0], r[2]) for r in rows}
        self.assertIn(('td.vehicle.service', 'vehicle_id.odometer'), paths)
        self.assertIn(('td.vehicle.service', 'vehicle_id.company_id'), paths)
        # многострочный @api.depends(...) через Many2one
        self.assertIn(('td.vehicle.service', 'vehicle_id.odometer'),
                      {(r[0], r[2]) for r in rows if r[1].startswith('depends')})

    def test_actions_bound_to_model(self):
        acts = {a['id']: a['model'] for a in self.out['actions']}
        self.assertEqual(acts['td_fleet_report.td_vehicle_report_action'], 'td.vehicle')
        self.assertEqual(acts['td_fleet_service.action_mark_service_due'], 'td.vehicle')

    def test_field_hits(self):
        text = odoo_map.field_hits(self.out, 'odometer')
        for where in ('td_fleet_service/views/td_vehicle_views.xml:8',      # xpath
                      'td_fleet_service/views/td_vehicle_service_views.xml:29',  # _inherits
                      'td_fleet_report/models/kpi.py:20',                    # related
                      'td_fleet_report/wizard/odometer_export.py:22',        # домен
                      'td_fleet/views/td_vehicle_views.xml:49',              # фильтр
                      'td_fleet_service/data/td_vehicle_service_actions.xml:9',  # код
                      'td_fleet_report/report/td_vehicle_report.xml:18'):    # QWeb
            self.assertIn(where, text)
        self.assertNotIn("_name = 'td.odometer.export'", text)
        self.assertNotIn('odometer_at = ', text)

    def test_model_filter_renders(self):
        text = odoo_map.render(self.out, 'td.vehicle', 'odometer')
        self.assertIn('делегирует (_inherits)', text)
        self.assertIn('## Не охвачено', text)
        self.assertIn('td_fleet_service.td_service_card_view_form', text)  # вью _inherits-модели
        self.assertNotIn('td.vehicle.tag | определяет', text)


if __name__ == '__main__':
    unittest.main()

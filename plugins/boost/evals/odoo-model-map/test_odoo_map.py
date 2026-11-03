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
        # _inherit = "td.vehicle" и _inherit = 'td.vehicle' строкой; список НЕ расширение (19)
        self.assertEqual(ext, {('td_fleet_service', 'FleetMaintenance'),
                               ('td_fleet_report', 'MileageKpi')})

    def test_list_inherit_without_name_is_new_model_in_19(self):
        # odoo/orm/models.py@19.0:240-249: _name из _inherit только для строки,
        # иначе из имени класса (MileageArchive -> mileage.archive)
        arch = [c for c in self.out['classes'] if c['class'] == 'MileageArchive'][0]
        self.assertEqual(arch['model'], 'mileage.archive')
        self.assertEqual(arch['role'], 'определяет')
        self.assertEqual(arch['series'], 19)
        self.assertIn('в 18.0 было бы расширение', arch['note'])
        self.assertIn('td.vehicle', arch['mixins'])
        text = odoo_map.render(self.out, 'td.vehicle')
        self.assertIn('| mileage.archive | новая модель по прототипу (НЕ расширение)', text)
        self.assertNotIn('| td.vehicle | расширяет | td_fleet_report | MileageArchive', text)
        # новой модели нужны свои права
        self.assertIn('`mileage.archive`', odoo_map.render(self.out).split('**Без строк доступа:**')[1])

    def test_list_inherit_in_18_is_extension(self):
        # odoo/models.py@18.0:245-250: список из одного элемента без _name -> расширение
        out18 = odoo_map.scan([ADDONS], odoo=18)
        arch = [c for c in out18['classes'] if c['class'] == 'MileageArchive'][0]
        self.assertEqual((arch['model'], arch['role']), ('td.vehicle', 'расширяет'))
        self.assertIn('в 19.0 стало бы новой моделью `mileage.archive`', arch['note'])

    def test_resolve_name_rules(self):
        r = odoo_map.resolve_name
        self.assertEqual(r({'_inherit': 'x.y'}, 'Foo', 19)[:2], ('x.y', 'расширяет'))
        self.assertEqual(r({'_inherit': ['x.y'], '_name': 'x.y'}, 'Foo', 19)[:2],
                         ('x.y', 'расширяет'))
        self.assertEqual(r({'_inherit': ['x.y']}, 'FooBar', 19)[:2], ('foo.bar', 'определяет'))
        self.assertEqual(r({'_inherit': ['a', 'b']}, 'FooBar', 18)[:2], ('FooBar', 'определяет'))
        name, role, note = r({'_inherit': ['x.y']}, 'Foo', None)   # серия не указана
        self.assertEqual((name, role), ('foo', 'определяет'))
        self.assertIn('серия Odoo в version манифеста не указана', note)
        self.assertEqual(odoo_map.series_of('19.0.1.0.0'), 19)
        self.assertIsNone(odoo_map.series_of('1.0'))
        self.assertEqual(odoo_map.class_to_model('Res_PartnerX'), 'res_partner.x')

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
        missing = text.split('**Без строк доступа:**')[1].split('\n')[0]
        self.assertIn('`td.odometer.export`', missing)
        self.assertNotIn('`td.vehicle`', missing)

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

    def test_trace_entry_point(self):
        text = odoo_map.trace(self.out, 'td.vehicle', 'action_reset_odometer')
        self.assertIn('`td_fleet.td_vehicle_view_form`', text)          # кнопка
        first = text.index('FleetMaintenance')
        self.assertLess(first, text.index('`Vehicle`'))                  # MRO: последний модуль первым
        self.assertIn('maintenance.py:18 · super() → дальше', text)
        self.assertIn('vehicle.py:35 · базовая реализация', text)
        for hit in ('_check_odometer', '_compute_next_service_km', '_compute_km_per_service',
                    '_compute_km_since_service', 'related поля vehicle_odometer'):
            self.assertIn(hit, text)                                     # триггеры write odometer
        self.assertIn('Пишет в `td.vehicle.service` поля `note`', text)  # self.service_ids.write
        self.assertIn('Не доказано', text)

    def test_trace_resolves_targets(self):
        text = odoo_map.trace(self.out, 'td.vehicle.service', 'action_tag_as_repair')
        self.assertIn('Пишет в `td.vehicle` поля `state`, `tag_ids`', text)
        self.assertIn('Пишет в `td.vehicle.tag` поля `name`', text)
        self.assertIn('td_vehicle_service_view_list', text)

    def test_model_filter_renders(self):
        text = odoo_map.render(self.out, 'td.vehicle', 'odometer')
        self.assertIn('делегирует (_inherits)', text)
        self.assertIn('## Не охвачено', text)
        self.assertIn('td_fleet_service.td_service_card_view_form', text)  # вью _inherits-модели
        self.assertNotIn('td.vehicle.tag | определяет', text)


if __name__ == '__main__':
    unittest.main()

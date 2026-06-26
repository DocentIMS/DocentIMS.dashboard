from DocentIMS.dashboard.api.services.docent_config.get import (
    collect_dashboard_config,
)
from DocentIMS.dashboard.testing import (  # noqa
    DOCENTIMS_DASHBOARD_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


REG = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.%s'


class DocentConfigIntegrationTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _set(self, name, value):
        api.portal.set_registry_record(REG % name, value)

    def test_empty_config_returns_all_keys(self):
        cfg = collect_dashboard_config()
        self.assertEqual(
            set(cfg),
            {'member_roles', 'company_roles', 'meeting_locations',
             'meeting_types', 'companies'},
        )
        for value in cfg.values():
            self.assertEqual(value, [])

    def test_roles_and_locations_flatten_to_names(self):
        self._set('vokabularies', [
            {'vocabulary_entry': 'Project Manager'},
            {'vocabulary_entry': 'Architect'},
            {'vocabulary_entry': ''},  # blank rows are dropped
        ])
        self._set('vokabularies3', [{'vocabulary_entry': 'Owner'}])
        self._set('location_names', [{'location_name': 'Site Office'}])

        cfg = collect_dashboard_config()
        self.assertEqual(cfg['member_roles'], ['Project Manager', 'Architect'])
        self.assertEqual(cfg['company_roles'], ['Owner'])
        self.assertEqual(cfg['meeting_locations'], ['Site Office'])

    def test_meeting_types_and_companies_keep_record_shape(self):
        self._set('meeting_types', [{
            'meeting_type': 'PTM',
            'meeting_title': 'Project Team Meeting',
            'meeting_summary': 'Weekly',
        }])
        self._set('companies', [{
            'full_company_name': 'Acme Inc',
            'short_company_name': 'Acme',
            'company_letter_kode': 'ACM',
            'company_full_street_address': '1 Main St',
            'company_other_address': '',
            'company_city': 'Boston',
            'company_zip': '02101',
            'company_state': 'MA',
        }])

        cfg = collect_dashboard_config()
        self.assertEqual(len(cfg['meeting_types']), 1)
        self.assertEqual(cfg['meeting_types'][0]['meeting_title'],
                         'Project Team Meeting')
        self.assertEqual(len(cfg['companies']), 1)
        self.assertEqual(cfg['companies'][0]['company_letter_kode'], 'ACM')
        self.assertEqual(cfg['companies'][0]['company_city'], 'Boston')

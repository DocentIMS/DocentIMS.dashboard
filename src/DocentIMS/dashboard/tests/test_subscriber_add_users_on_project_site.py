# -*- coding: utf-8 -*-
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class SubscriberIntegrationTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_handler_importable(self):
        # The add-users subscriber exposes a `handler` callable.
        from DocentIMS.dashboard.subscribers import add_users_on_project_site
        self.assertTrue(callable(add_users_on_project_site.handler))

    def test_build_message_leaves_unknown_placeholders(self):
        # Sanity check the shared interpolation helper used by the subscriber.
        from DocentIMS.dashboard.mailing import build_message
        result = build_message(
            'Hello {first_name}, {unknown}', self.portal,
            {'first_name': 'Wayne'})
        self.assertIn('Wayne', result)
        self.assertIn('{unknown}', result)


class SubscriberFunctionalTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portal_available(self):
        self.assertTrue(self.portal is not None)

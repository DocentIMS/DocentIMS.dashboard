# -*- coding: utf-8 -*-
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletType
from zope.component import getUtility

import unittest


class PortletIntegrationTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.app.REQUEST
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_infoportlet_is_registered(self):
        portlet = getUtility(
            IPortletType,
            name='DocentIMS.dashboard.portlets.Infoportlet',
        )
        self.assertEqual(portlet.addview, 'DocentIMS.dashboard.portlets.Infoportlet')


class PortletFunctionalTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

# -*- coding: utf-8 -*-
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING
from DocentIMS.dashboard.testing import DOCENTIMS_DASHBOARD_INTEGRATION_TESTING
from DocentIMS.dashboard.views.email_pre_view import IEmailPreView
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Document', 'front-page')

    def test_email_pre_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='email-pre-view'
        )
        self.assertTrue(IEmailPreView.providedBy(view))

    def test_email_pre_view_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal['front-page'], self.portal.REQUEST),
                name='email-pre-view'
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = IEmailPreView.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):

    layer = DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

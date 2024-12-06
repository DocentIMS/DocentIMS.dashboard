# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE
    PloneSandboxLayer,
)
from plone.testing import z2

import DocentIMS.dashboard


class DocentimsDashboardLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=DocentIMS.dashboard)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'DocentIMS.dashboard:default')


DOCENTIMS_DASHBOARD_FIXTURE = DocentimsDashboardLayer()


DOCENTIMS_DASHBOARD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DOCENTIMS_DASHBOARD_FIXTURE,),
    name='DocentimsDashboardLayer:IntegrationTesting',
)


DOCENTIMS_DASHBOARD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DOCENTIMS_DASHBOARD_FIXTURE,),
    name='DocentimsDashboardLayer:FunctionalTesting',
)


DOCENTIMS_DASHBOARD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        DOCENTIMS_DASHBOARD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='DocentimsDashboardLayer:AcceptanceTesting',
)

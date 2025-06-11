# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone import api

@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "DocentIMS.dashboard:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["DocentIMS.dashboard.upgrades"]


def post_install(context):
    """Post install script"""
    portal =  api.portal.get()
    
    #portal.default_page='app-view'
    portal.layout = 'app-view'
    # api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_buttons', 
    #                                      [{'location_name': 'https://team.chelseamallproject.com'}, 
    #                                       {'location_name': 'https://team.reverebeachproject.com'}
    #                                      ])
    
    
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

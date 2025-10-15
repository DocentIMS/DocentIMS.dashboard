# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
import plone.api

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
    portal =  plone.api.portal.get()
    
    #portal.default_page='app-view'
    portal.layout = 'app-view'
    
    # Button has been moved to 'Project' content type
    # api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_buttons', 
    #                                      [{'location_name': 'https://team.chelseamallproject.com'}, 
    #                                       {'location_name': 'https://team.reverebeachproject.com'}
    #  
    # ])
    plone.api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names', 
                                         [{'location_name': 'Teams'}, 
                                          {'location_name': 'Zoom'},
                                          {'location_name': 'Client Office'},
                                          {'location_name': 'Client Office and Teams'},
                                          {'location_name': 'Client Office and Zoom'}
                                         ])
    
    #Is member roles
    plone.api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies',
                                        [   {'vocabulary_entry': 'Project Manager'},
                                            {'vocabulary_entry': 'Quality Manager'},
                                            {'vocabulary_entry': 'Client'},
                                            {'vocabulary_entry': 'Electrical'},                                              
                                        ])  
    
    #Is company roles
    plone.api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3',
                                        [   {'vocabulary_entry': 'Prime'},
                                            {'vocabulary_entry': 'Architect'},
                                            {'vocabulary_entry': 'Geotechnical'},
                                            {'vocabulary_entry': 'Outreach'},                                              
                                        ])  
    
    plone.api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types',
      [ {'meeting_type': 'Project Team Meeting', 
         'meeting_title': 'Project Team Meeting', 
         'meeting_summary': 'Project Meeting' 
         },
        {'meeting_type': 'Community Meeting', 
         'meeting_title': 'Community Outreach Meeting', 
         'meeting_summary': 'Community Outreach Meeting' 
         },
        {'meeting_type': 'Executive Team Meeting', 
         'meeting_title': 'Executive Team Meeting', 
         'meeting_summary': 'Executive Meeting' 
        },
      ])
    
    # Do something at the end of the installation of this package.
    # add user vbauser
    portal = plone.api.portal.get()
    try:
        plone.api.user.create(email='vbauser@docentims.com', username='vbauser@docentims.com', password=None, roles=('Member', 'Manager',), properties={'fullname': "VBA User", 'first_name': 'VBA', 'last_name': 'User'})
    except ValueError: 
        pass


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

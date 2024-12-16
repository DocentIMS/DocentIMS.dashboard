# -*- coding: utf-8 -*-

# from DocentIMS.ActionItems import _
from Products.Five.browser import BrowserView
from zope.interface import Interface
import requests
from plone import api

# from AccessControl.SecurityManagement import getSecurityManager

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IAppInjectView(Interface):
    """ Marker Interface for IAppInjectView"""


class AppInjectView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('app_inject_view.pt')

    # def __init__(self, context, request):
    #     self.request = request
        
        
    def __call__(self):
        # Implement your own actions:
        return self.index()
    
    def get_current(self):
        current = api.user.get_current()
        return current.getProperty('email')
    
    
    def get_dashboard_info(self):
        # TO DO: dont use admin 
        siteurl = self.request.get('siteurl', 'https://mymeadows.org')
        # app_password =  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_password')
        # app_user = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_user')
        
        response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
 
        if response:
                body = response.json()
                return body
            
        return None
     
 
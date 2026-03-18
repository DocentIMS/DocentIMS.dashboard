# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.interface import Interface
import requests
from plone import api
from  ..interfaces import IDocentimsSettings
from plone.memoize import ram
import time 

# from AccessControl.SecurityManagement import getSecurityManager
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


# 15 minutes in seconds
CACHE_TIMEOUT = 15 * 60

def cache_key_subbuttons(method, self): 
    user = self.get_current()
    t = int(time.time() / CACHE_TIMEOUT)

    refresh = self.request.get('refresh', None)
    if refresh:
        # unique key every time → bypass cache
        return f"inject-{user}-refresh"
    
    return f"inject-{user}-{t}"


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
        self.dashboard_info = self.get_dashboard_info()
        self.portlet_data = self.get_portlet_data()
        return self.index()
    
    
    def get_current(self):
        current = api.user.get_current()
        return current.getUserName()
        # return current.getProperty('email')
    
    @ram.cache(cache_key_subbuttons)
    def get_dashboard_info(self):
        # TO DO: dont use admin 
        # print('getting dashboard info')
        #Should happen every 15 minutes or on reload ?
        # print('getting stuff')
        
        siteurl = self.request.get('siteurl', 'http://mymeadows.org')
        # app_password =  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_password')
        # app_user = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_user')
        basik =  api.portal.get_registry_record('dashboard', interface=IDocentimsSettings) or ''
        response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', timeout=3,  headers={'Authorization': f'Basic {basik}','Accept': 'application/json', 'Content-Type': 'application/json'} )
 
        if response:
                body = response.json()
                return body
            
        return None
    
    def portlet_data(self):
        return self.get_portlet_data()
    
    @ram.cache(cache_key_subbuttons)   
    def get_portlet_data(self):
        #Should happen every 15 minutes or on reload ?
        siteurl = self.request.get('siteurl', 'http://mymeadows.org')        
        result = []    
        try:                
            response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', timeout=3,
                                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            if response.status_code == 200:
                body = response.json()
                if body['dashboard-list'] != None:
                    result.append({
                                        'name': body['dashboard-list']['short_name'], 
                                        'url': siteurl, 
                                        'short_name':  body['dashboard-list']['short_name'],
                                        'project_color': body['dashboard-list']['project_color'],
                                        'portlet_content': body['dashboard-list']['portlet_content'],
                            })                
        except requests.exceptions.ConnectionError:
                    print("Failed to connect to the server. Please check your network or URL.")
        except requests.exceptions.Timeout:
                    print("The request timed out. Try again later.")
        except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
            
        return result
     
 
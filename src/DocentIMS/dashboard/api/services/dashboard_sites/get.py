# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
import requests
from AccessControl import getSecurityManager
from plone.restapi.services import Service
from zExceptions import Unauthorized
            

@implementer(IExpandableElement)
@adapter(Interface, Interface)
class DashboardSites(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        if api.user.is_anonymous():
            raise Unauthorized
        
        user = api.user.get_current()
        usermail = self.request.get('email', None)        
        
        if user.id  != 'admin':
            usermail = user.getProperty('email')
        # some_secret = self.request.get('some_secret', None)
        result = {
            'dashboard_sites': {
                '@id': '{}/@dashboard_sites'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        # === Return list of sites ===    
        sites = None
        projects = api.content.find(portal_type='Project')

        # 2) Create a list of URLs
        if projects:
            sites = [brain.project_url for brain in projects]
        buttons = []
        
        # if some_secret = something;        
        if usermail and sites:           
            for siteurl in sites:
                try:                
                    response = requests.get(f'{siteurl}/@item_count?user={usermail}', 
                                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
                    if response.status_code == 200:
                        body = response.json()
                        if body['dashboard-list'] != None:
                            buttons.append({
                                'name': body['dashboard-list']['short_name'], 
                                'url': siteurl, 
                                'project_color': body['dashboard-list']['project_color'],
                                'last_login_time': body['dashboard-list']['last_login_time'], 
                            })
                
                except requests.exceptions.ConnectionError:
                    print("Failed to connect to the server. Please check your network or URL.")
                except requests.exceptions.Timeout:
                    print("The request timed out. Try again later.")
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")

            
        result = {
                'dashboard_sites': {
                    'sites': sites, 
                    'buttons': buttons,   
                },
            } 
                   
        return result
    
        
class DashboardSitesGet(Service):
        def reply(self):
            # if api.user.is_anonymous():
            #    return None
            service_factory = DashboardSites(self.context, self.request)
            return service_factory(expand=True)['dashboard_sites']

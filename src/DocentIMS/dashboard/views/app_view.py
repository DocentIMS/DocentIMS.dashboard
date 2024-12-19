# -*- coding: utf-8 -*-

# from DocentIMS.ActionItems import _
from Products.Five.browser import BrowserView
from zope.interface import Interface
import requests
from plone import api
from DocentIMS.ActionItems.interfaces import IDocentimsSettings
from datetime import datetime






class IAppView(Interface):
    """ Marker Interface for IAppView"""


class AppView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('app_view.pt')

    def __call__(self):
        # Implement your own actions:
        # colors=self.get_colors()
        return self.index()    

    def get_current_time(self):
        # Get the current local time
        now =  datetime.now()
        # return now.strftime('%A, %d %B %Y, %I:%M %p')
        return now.strftime('%d %b %I:%M %p')


    def get_buttons(self):
        
        urls = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_buttons')
        buttons = []
        
        
        if urls:
            for siteurl in urls:
                try:                
                    response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', 
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
            
        return buttons
    
    def get_current(self):
        current = api.user.get_current()
        #return current.getId()
        return current.getProperty('email')
    
    def get_fullname(self):
        current = api.user.get_current()
        #return current.getId()
        return current.getProperty('fullname')
    
    def get_colors(self):
        color1=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color1')
        color2=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color2')
        color3=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color3')
        color4=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color4')
        color5=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color5')
        return[color1, color2, color3, color4, color5]
    
    # def get_if_login(self):
    #     current = api.user.get_current()
    #     last_login_time =  current.getProperty('last_login_time', None)
    #     return last_login_time.year() == 2000 
        
  
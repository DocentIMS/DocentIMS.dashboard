# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.interface import Interface
import requests
from plone import api
from plone.memoize import ram
import time
from datetime import datetime
import socket
 

# 15 minutes in seconds
CACHE_TIMEOUT = 15 * 60

def cache_key_buttons(method, self):
    user = self.get_current()
    t = int(time.time() / CACHE_TIMEOUT)

    refresh = self.request.get('refresh', None)
    if refresh:
        return f"buttons-{user}-refresh"
    
    
    return f"buttons-{user}-{t}"



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

    # def buttons(self):
    #     return self.get_buttons()
    
    @ram.cache(cache_key_buttons)
    def get_buttons(self):
        
        # print('getting buttons')
        # Should happen every 30 minutes
        
        #urls = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_buttons')
        # 1) Find all 'Project' items
        urls = None
        projects = api.content.find(portal_type='Project')

        # 2) Create a list of URLs
        if projects:
            # urls = [brain.project_url for brain in projects]
            urls = [(brain.project_url, brain.getURL()) for brain in projects]
        
        buttons = []        
        
        if urls:
            for siteurl, absolute_url in urls:
                try:                
                    response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', timeout=3,
                                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
                    if response.status_code == 200:
                        body = response.json()
                        if body['dashboard-list'] != None:
                            buttons.append({
                                        'name': body['dashboard-list']['short_name'], 
                                        'url': siteurl, 
                                        'edit_url': absolute_url,
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
        return current.getUserName()
        # return current.getProperty('email')
    
    def check_editperm(self):
        user = api.user.get_current()
        if 'Manager' in user.getRoles():
            return True
        if 'Site Administrator' in user.getRoles():
            return True
        if 'Dashboard Manager' in user.getRoles():
            return True
        if 'Project Manager' in user.getRoles():
            return True
        return False
    
    def get_fullname(self):
        current = api.user.get_current()
        #return current.getId()
        return current.getProperty('fullname')
    
    @ram.cache(cache_key_buttons)
    def get_colors(self):
        color1=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color1')
        color2=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color2')
        color3=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color3')
        color4=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color4')
        color5=  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.color5')
        return[color1, color2, color3, color4, color5]
    
    
    def get_meeting_types(self):
        meeting_types = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types')
        return [
            meeting.get('meeting_type')
            for meeting in meeting_types
            if meeting.get('meeting_type')
        ]                     
                                                        
    @ram.cache(cache_key_buttons)
    def get_server_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception as e:
            return f"Error: {e}"
    
    @ram.cache(cache_key_buttons)
    def get_served_domain(self):
        """Retrieve the domain dynamically from the request"""
        return self.request.get("HTTP_HOST") or "0.0.0.0"
        
        
    @ram.cache(cache_key_buttons)  
    def get_served_domain_ip(self):
        """Get the public IP of the domain serving the Plone site"""
        try:
            # domain = self.request.get("https://www.medialog.no", "unknown")
            domain = self.get_served_domain()
            if domain and ':' in domain:
                domain = domain.split(':')[0]
            
            return socket.gethostbyname(domain)
        except Exception as e:
            return f"Error resolving domain IP: {e}"
    
 
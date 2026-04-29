# -*- coding: utf-8 -*-

# from DocentIMS.dashboard import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from plone import api
from Products.CMFCore.utils import getToolByName
from plone.stringinterp.interfaces import IStringInterpolator

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from  ..interfaces import IDocentimsSettings


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class IEmailPreView(Interface):
    """ Marker Interface for IEmailPreView"""

def build_message(raw_message, obj, context_vars):
    # 1️⃣ Python {} variables
    message = raw_message.format_map(SafeDict(context_vars))

    # 2️⃣ Plone ${} variables
    interpolator = IStringInterpolator(obj)
    message = interpolator(message)

    return message

@implementer(IEmailPreView)
class EmailPreView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('email_pre_view.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()


    def get_email_content(self):
            """ Event handler which will add users to project sites
            Not registered to content type since no content will be added to site
            """
            context = self.context
            project_url = context.absolute_url()
            project_title = context.Title()            
            user = api.user.get_current()

            if user is None:
                print(f"⚠️ User '{user}' not found")
                return "No user, can not preview"
                

            # Plone PAS user properties
            username = user.getUserName()
            fullname = user.getProperty("fullname")
            email = user.getProperty("email")
            first_name = user.getProperty("first_name")
            last_name =  user.getProperty("last_name")
            company = user.getProperty("company")
            portal = api.portal.get()
            portal_url = portal.absolute_url()
            reset_url = f"[password reset url goes here]"            
                
            dashboard_manager_fullname = '[Dashboar Manger for that project]'
            dashboard_manager_company = '[Company for that project]'
            register_url = f"[register_url goes here]"
                    
            
            #Different mail for first and next project
            mail_subject = "Welcome to a New Project / Welcome to Docent Dashboard site"
            mail_message = api.portal.get_registry_record('email_message_returning', interface=IDocentimsSettings) or ''
                        
            # mail_subject2 = 'Welcome to Docent Dashboard site'
            mail_message2 = api.portal.get_registry_record('email_message', interface=IDocentimsSettings) or ''
            # raw_message = mail_message.raw  if we can get rich text to work
            raw_message = f"{mail_message2} <div><p><hr/></p></div> {mail_message}"            
                    
            context_vars = {                    
                        "portal_url": portal_url,
                        "register_url" : register_url,
                        "email": email,
                        "fullname": fullname,
                        "username": username, 
                        "last_name" :  last_name, 
                        "first_name" : first_name,
                        "company" : company, 
                        "dashboard_manager_company" : dashboard_manager_company,
                        "dashboard_manager_fullname" : dashboard_manager_fullname,
                        "portal":  portal,     
                        "project_url": project_url,    
                        "project_title": project_title,
                        "project_name": project_title,
                        "user_name": username,
                        "username": username,   
                        "reset_url": reset_url, 
                        "dashboard_set_password_url": reset_url,                         
                    }
                    
            message = build_message(raw_message, self.context, context_vars)
            
            return message
                    
   
                    
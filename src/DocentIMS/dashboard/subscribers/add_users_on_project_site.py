# -*- coding: utf-8 -*-
import requests
from plone import api
from io import BytesIO
import base64
from  ..interfaces import IDocentimsSettings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.utils import formataddr
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.interface.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IMailSchema
from Acquisition import aq_inner
# from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from plone.stringinterp.interfaces import IStringInterpolator


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def build_message(raw_message, obj, context_vars):
    # 1️⃣ Python {} variables
    message = raw_message.format_map(SafeDict(context_vars))

    # 2️⃣ Plone ${} variables
    interpolator = IStringInterpolator(obj)
    message = interpolator(message)

    return message



def handler(obj, event):
    """ Event handler which will add users to project sites
    Not registered to content type since no content will be added to site
    """
    
    if obj.portal_type == "Project":
        project_url = obj.project_url
        user_list = obj.add_users
        
        #Dummy password, TO DO: Change / get from some settings
        # auth = ("admin", "admin")
        basik =  api.portal.get_registry_record('dashboard', interface=IDocentimsSettings) or ''
        users_endpoint = f"{project_url}/@users"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            'Authorization': f'Basic {basik}'
        }

        for userid in user_list:
            user = api.user.get(userid=userid)

            if user is None:
                print(f"⚠️ User '{userid}' not found")
                continue

            # Plone PAS user properties
            username = user.getUserName()
            fullname = user.getProperty("fullname")
            email = user.getProperty("email")
            first_name = user.getProperty("first_name")
            groups = api.group.get_groups(username=username) 
            first_time = 'PrjTeam' not in [g.id for g in groups]
            
            api.group.add_user(groupname='PrjTeam', username=username)
            last_name =  user.getProperty("last_name")
            company = user.getProperty("company")

            payload = {
                "email": email,
                "fullname": fullname,
                "username": username, 
                # Dont send password reset, we should include it in our email below
                # "sendPasswordReset": False,
                "last_name" : last_name,
                "first_name" : first_name,
                # "your_team_role" : user.getProperty("your_team_role"),
                "your_team_role" : '--',
                "office_phone_number" : user.getProperty("office_phone_number"),
                "cellphone_number" : user.getProperty("cellphone_number"),
                "company" : company,
                "description" : user.getProperty("description"),
                "groups" : [{"@id": "PrjTeam"}],
                "properties": {
                    "email": email,
                    "fullname": fullname,
                    "last_name" : last_name,
                    "first_name" : first_name,
                    # "your_team_role" : user.getProperty("your_team_role"),
                    "office_phone_number" : user.getProperty("office_phone_number"),
                    "cellphone_number" : user.getProperty("cellphone_number"),
                    "company" : company,
                    "description" : user.getProperty("description"),
                }
            }            
            
            response = requests.post(users_endpoint, headers=headers, json=payload)            
            
            
            # Add image to user and add user to group
            
            if response.status_code in (200, 201):  # 201 = created
                
                # user successfully added, lets send email
                #code to send email here
                
                
                # Add user to group:
                # TO DO: Keep only one when I know why users are not added with email instead of random username
                group_endpoint = f"{project_url}/@groups/PrjTeam"
                group_response = requests.patch(group_endpoint, headers=headers, json={"users": {username: 'true'} })
                groups_response = requests.patch(group_endpoint, headers=headers, json={"users": {response.json().get('username'): 'true'} })               
                
                #something =  api.portal.get_registry_record('something', interface=IDocentimsSettings) or ''
                
                dashboard_manager_fullname = 'My name'
                dashboard_manager_company = 'My company'
                portal = api.portal.get()
                portal_url = portal.absolute_url()
                register_url = f"{portal_url}/register"
                
                # 1. Find group
                db_group =  api.user.get_users(groupname="DashboardManagers")
                if db_group:
                    db_user = db_group[0]
                        
                    if db_user:
                            # 3. Full name
                            dashboard_manager_fullname = db_user.getProperty("fullname", "")
                            
                            # 4. Company
                            dashboard_manager_company = db_user.getProperty("company", "")

                #Different mail for first and next project
                mail_subject = "Welcome to a New Project"
                mail_message = api.portal.get_registry_record('email_message_returning', interface=IDocentimsSettings) or ''
                     
                if first_time:
                     mail_subject = 'Welcome to Docent Dashboard site'
                     mail_message = api.portal.get_registry_record('email_message', interface=IDocentimsSettings) or ''
                raw_message = mail_message.raw
                
                
                context_vars = {                    
                    "portal_url": portal_url,
                    "register_url" : register_url,
                    "email": email,
                    "fullname": fullname,
                    "username": username, 
                    "last_name" :  last_name, 
                    "first_name" : first_name,
                    "company" :  company, 
                    "dashboard_manager_company" : dashboard_manager_company,
                    "dashboard_manager_fullname" : dashboard_manager_fullname,
                    "portal":  portal,     
                    "project_url": project_url,        
                }
                
                # DO variable substitution of mail body
                # message = raw_message.format_map(SafeDict(context_vars))
                message = build_message(raw_message, obj, context_vars)
                
                registry = getUtility(IRegistry)
                
                mailhost = getToolByName(portal, "MailHost")
                if not mailhost:
                    abc = 1
                    raise ComponentLookupError(
                        "You must have a Mailhost utility to \
                    execute this action"
                    )
                
                message_html = MIMEText(message, 'html', _charset='UTF-8')
                
                     
                message_html['Subject'] = mail_subject
                message_html['From'] = api.portal.get_registry_record('plone.email_from_address') or ''
                message_html['To'] = email
                    
                mailhost.send(message_html.as_string())
                # Upload portrait if exists
                portal_membership = api.portal.get_tool('portal_membership')
                portrait = portal_membership.getPersonalPortrait(userid) 
                if portrait and hasattr(portrait, 'data'):
                    portrait_endpoint = response.json()['@id']
                    portrait_bytes = portrait.data # the binary image, None if it is the 'default image'
                    
                    if portrait_bytes:                        
                        portrait_mime = getattr(portrait, "contentType", "image/jpeg")
                        # filename = portrait.__name__ or "portrait"
                        filename =  "portrait"
                        portrait_b64 = base64.b64encode(portrait_bytes).decode("utf-8")
                        
                        r = requests.patch(portrait_endpoint, 
                                        headers= headers,
                                        json={'portrait': {'content-type': portrait_mime , 
                                                            'data': portrait_b64, 
                                                            'encoding': "base64", 
                                                            'filename': filename}}, 
                                        )
                        
                        if r.status_code == 204:
                            print(f"✅ Portrait for '{userid}' uploaded successfully")
                        else:
                            print(f"⚠️ Failed to upload portrait for '{userid}'")
            elif response.status_code == 409:
                print(f"⚠️ User {username} already exists")
                api.portal.show_message(message=f"⚠️ User {username} already exists", type='info')
            elif response.status_code == 500:
                api.portal.show_message(message=f"{fullname} not added to project site.  Will not send email to this user", type='info')
                api.portal.show_message(message=f"❌ Error creating {username}: {response.status_code} {response.text}", type='warning')                
            elif response.status_code == 401:
                api.portal.show_message(message=f"Password is incorrect. Fix it in control panel", type='warning ')
            else:
                print(f"❌ Error creating {username}: {response.status_code} {response.text}")
                api.portal.show_message(message=f"❌ Error creating {username}: {response.status_code} {response.text}", type='warning')
                
            
                
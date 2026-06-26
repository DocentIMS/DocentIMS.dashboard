# -*- coding: utf-8 -*-

# from DocentIMS.dashboard import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from plone import api
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from  ..interfaces import IDocentimsSettings
from ..mailing import build_message
from email.mime.text import MIMEText
from email.utils import formataddr
import json
import logging


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger(__name__)


class IEmailPreView(Interface):
    """ Marker Interface for IEmailPreView"""


@implementer(IEmailPreView)
class EmailPreView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('email_pre_view.pt')

    status = ''

    def __call__(self):
        if self.request.get('REQUEST_METHOD') == 'POST' and \
                self.request.get('send_test'):
            self.send_test_email()
            # AJAX caller (the box injected on the email settings tab) wants
            # JSON back rather than the full preview page.
            if self.request.get('ajax'):
                self.request.response.setHeader(
                    'Content-Type', 'application/json')
                return json.dumps({'status': self.status})
        return self.index()

    def send_test_email(self):
        """Send the previewed (variable-filled) welcome email to a manually
        entered address, using the same MailHost / no-reply sender as the
        real add-to-project send."""
        address = (self.request.get('test_email') or '').strip()
        if not address:
            self.status = 'Please enter an email address.'
            return
        try:
            message = self.get_email_content()
            portal = api.portal.get()
            mailhost = getToolByName(portal, 'MailHost')

            message_html = MIMEText(message, 'html', _charset='UTF-8')
            configured_from = api.portal.get_registry_record(
                'plone.email_from_address') or ''
            from_domain = (configured_from.split('@')[-1]
                           if '@' in configured_from else 'docentdashboard.org')
            noreply_sender = formataddr(
                ('Do Not Reply', f'do-not-reply@{from_domain}'))

            message_html['Subject'] = '[TEST] Welcome to Docent Dashboard'
            message_html['From'] = noreply_sender
            message_html['To'] = address
            message_html['Reply-To'] = noreply_sender
            message_html['Auto-Submitted'] = 'auto-generated'

            mailhost.send(message_html.as_string())
            self.status = 'Test email sent to %s.' % address
        except Exception as e:
            logger.warning('Test email send failed: %s', e)
            self.status = 'Could not send test email: %s' % e

    def get_email_content(self):
            """ Event handler which will add users to project sites
            Not registered to content type since no content will be added to site
            """
            context = self.context
            project_url = context.absolute_url()
            project_title = context.Title()            
            user = api.user.get_current()

            if user is None:
                logger.warning("No current user found; cannot preview email")
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
                    
   
                    
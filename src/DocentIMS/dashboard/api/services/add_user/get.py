# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface, implementer
import json
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides



from AccessControl import getSecurityManager
from plone.app.users.schema import ICombinedRegisterSchema
from plone.restapi import _
from plone.restapi.bbb import ISecuritySchema
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.permissions import PloneManageUsers
from plone.restapi.services import Service
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
from Products.CMFPlone.PasswordResetTool import InvalidRequestError
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AddUser(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request
    
    def __call__(self, expand=False):
        result = {
            'add_user': {
                '@id': '{}/@add_user'.format(self.context.absolute_url()),
            },
        }
        if not expand:
            return result

        try:
            body = self.request.get('BODY', '{}')
            request_data = json.loads(body) if body else {}
            fullname = request_data.get('fullname')
            first_name = request_data.get('first_name')
            last_name = request_data.get('last_name')
            office_phone_number = request_data.get('office_phone_number')
            cellphone_number = request_data.get('cellphone_number')
            company = request_data.get('company')
            description = request_data.get('description')
            email = request_data.get('email')
            username = request_data.get("username", None)
            password = request_data.get("password", None)
            # roles = request_data.get("roles", ["Member"])
            self.__create_user__(email=email, 
                                username=username, 
                                password=password, 
                                first_name = first_name,
                                last_name = last_name,
                                office_phone_number =  office_phone_number,
                                cellphone_number =  cellphone_number,
                                company = company,
                                description = description,
                                roles=('Member',), 
                                fullname=fullname)
            result = {'status': 'success', 'message': 'User created'}
        except Exception as e:
            result = {'status': 'error', 'message': str(e)}

        return result
    
    def __create_user__(self, username, email, fullname, password, roles):
            
        portal = api.portal.get()
        
        # alsoProvides(self.request, IDisableCSRFProtection)
        with api.env.adopt_roles(['Manager']):
            try:
                myuser = api.user.create(
                        email=email,
                        username=username,
                        # password="temporary-password",
                        roles=roles,
                        properties={'fullname': fullname}
                    )
            finally:
                print('error')
            
            return True


class AddUserGet(Service):

    def reply(self):
        service_factory = AddUser(self.context, self.request)
        return service_factory(expand=True)

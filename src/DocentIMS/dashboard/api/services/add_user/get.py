# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
import string
import random
import json


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AddUser(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        
        # result = {
        #     'add_user': {
        #         '@id': '{}/@add_user'.format(
        #             self.context.absolute_url(),
        #         ),
        #     },
        # }
        # if not expand:
        #     return result

        # === Your custom code comes here ===
        
        # TO DO: Not sure why / if we should use try
        request_data = json.loads(self.request.get('BODY', '{}'))
        # {'email':  password':  'roles': ['Member']}
        
        result =  'None'
            
        
        try:
            fullname = request_data.get('fullname')
            email = request_data.get('email')
            password = request_data.get('password')
            
            if not api.user.get(username=email):
                api.user.create(email=email, password=password, roles=('Member',), properties = dict(fullname=fullname)) 
                print('user created')
                result = 'True'
        except Exception as e:
            print(e)
            result = 'False'
            
        return result

         

class AddUserGet(Service):

    def reply(self):
        service_factory = AddUser(self.context, self.request)
        return service_factory(expand=True) 




# added_user = api.user.create(email='email@medialog.no',  password='password' ) 
                
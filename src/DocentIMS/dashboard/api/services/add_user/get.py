# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
import string
import random


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AddUser(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        result = {
            'add_user': {
                '@id': '{}/@add_user'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        # === Your custom code comes here ===

        if hasattr(self.request, "username"):
            username = self.request.username
            if not api.user.get(username=username):
                fullname = self.request.fullname
                email = self.request.email
                password = ''.join(random.choices(string.ascii_letters, k=27))
                api.user.create(email=email, username=username, password=password, roles=('Member',), properties = dict(fullname=fullname)) 
                result['add_user'] = 'user created'
        return result

class AddUserGet(Service):

    def reply(self):
        service_factory = AddUser(self.context, self.request)
        return service_factory(expand=True)['add_user']




# added_user = api.user.create(email='email@medialog.no',  password='password' ) 
                
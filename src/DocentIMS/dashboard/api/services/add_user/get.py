# -*- coding: utf-8 -*-
# NOTE: This service is currently not registered in ZCML
# (add_user/configure.zcml is fully commented out).
# The fixes below are applied so the code is correct if/when it is re-enabled.

from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface, implementer
import json
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zExceptions import Unauthorized


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AddUser(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        if api.user.is_anonymous():
            raise Unauthorized

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

            email    = request_data.get('email')
            username = request_data.get('username')
            password = request_data.get('password')
            fullname = request_data.get('fullname')

            # FIX: All extra properties are now collected into a dict and
            # forwarded to __create_user__.  Previously these keyword arguments
            # were passed in the call but the method signature only accepted
            # (username, email, fullname, password, roles), so every extra
            # property was silently dropped.
            extra_properties = {
                'first_name':           request_data.get('first_name'),
                'last_name':            request_data.get('last_name'),
                'office_phone_number':  request_data.get('office_phone_number'),
                'cellphone_number':     request_data.get('cellphone_number'),
                'company':              request_data.get('company'),
                'description':          request_data.get('description'),
            }

            self.__create_user__(
                email=email,
                username=username,
                password=password,
                fullname=fullname,
                roles=('Member',),
                extra_properties=extra_properties,
            )
            result = {'status': 'success', 'message': 'User created'}

        except Exception as e:
            result = {'status': 'error', 'message': str(e)}

        return result

    def __create_user__(self, username, email, fullname, password, roles,
                        extra_properties=None):
        """Create a user.

        FIX 1: Signature now accepts extra_properties so caller-supplied
                fields (first_name, last_name, phone numbers, etc.) are
                actually stored instead of being silently discarded.

        FIX 2: The original code used try/finally with print('error') in the
                finally clause, which printed 'error' on every successful
                creation as well.  Replaced with a proper try/except so the
                error is only reported when something actually goes wrong.
        """
        extra_properties = extra_properties or {}

        properties = {'fullname': fullname}
        properties.update(extra_properties)

        with api.env.adopt_roles(['Manager']):
            try:
                myuser = api.user.create(
                    email=email,
                    username=username,
                    password=password,
                    roles=roles,
                    properties=properties,
                )
            except Exception as e:
                # Re-raise so __call__ can catch it and return an error response.
                raise

        return True


class AddUserGet(Service):

    def reply(self):
        service_factory = AddUser(self.context, self.request)
        return service_factory(expand=True)

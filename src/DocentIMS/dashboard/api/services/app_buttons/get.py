# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zExceptions import Unauthorized


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AppButtons(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        if api.user.is_anonymous():
            raise Unauthorized

        result = {
            'app_buttons': {
                '@id': '{}/@app_buttons'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        projects = api.content.find(portal_type='Project')
        urls = [brain.project_url for brain in projects] if projects else []

        # FIX: Return the dict wrapper so callers can safely key into
        # ['app_buttons'].  Previously __call__ returned a bare list when
        # expanded, causing AppButtonsGet.reply() to crash with a TypeError
        # when it tried result['app_buttons'].
        return {'app_buttons': urls}


class AppButtonsGet(Service):

    def reply(self):
        service_factory = AppButtons(self.context, self.request)
        return service_factory(expand=True)['app_buttons']

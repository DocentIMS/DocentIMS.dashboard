# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

# curl -i -X GET https://dashboard.docentims.com/@app_buttons  -H "Accept: application/json"   -k --user admin:admin



@implementer(IExpandableElement)
@adapter(Interface, Interface)
class AppButtons(object):

    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        result = {
            'app_buttons': {
                '@id': '{}/@app_buttons'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        result['app_buttons']['items'] = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_buttons')
        return result


class AppButtonsGet(Service):

    def reply(self):
        service_factory = AppButtons(self.context, self.request)
        return service_factory(expand=True)['app_buttons']





 
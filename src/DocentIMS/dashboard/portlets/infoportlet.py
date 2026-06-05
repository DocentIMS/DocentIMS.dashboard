# -*- coding: utf-8 -*-
from __future__ import absolute_import
# from Acquisition import aq_inner
from DocentIMS.dashboard import _
from plone import schema
from plone.app.portlets.portlets import base
# from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
# from zope.component import getMultiAdapter
from zope.interface import implementer
from plone import api
import requests
import time

import json
import six.moves.urllib.error
import six.moves.urllib.parse
import six.moves.urllib.request



# 15 minutes in seconds
CACHE_TIMEOUT = 15 * 60


class IInfoportletPortlet(IPortletDataProvider):
    tittel = schema.TextLine(
        title=_(u'Title'),
        required=True,
        default=u''
    )


@implementer(IInfoportletPortlet)
class Assignment(base.Assignment):
    schema = IInfoportletPortlet

    def __init__(self, tittel=''):
        self.tittel = tittel.lower()

    @property
    def title(self):
        return _(u'Title')


class AddForm(base.AddForm):
    schema = IInfoportletPortlet
    form_fields = field.Fields(IInfoportletPortlet)
    label = _(u'Add Title')
    description = _(u'This portlet displays info from sites.')

    def create(self, data):
        return Assignment(
            tittel=data.get('tittel', ''),
        )


class EditForm(base.EditForm):
    schema = IInfoportletPortlet
    form_fields = field.Fields(IInfoportletPortlet)
    label = _(u'Edit Title')
    description = _(u'This portlet displays info from sites')




def cache_key_news(method, self):
        user = self.get_current()
        t = int(time.time() / CACHE_TIMEOUT)
        
        if self.request.get('refresh'):
            return f"news-{user}-refresh"

        return f"news-{user}-{t}"



class Renderer(base.Renderer):
    schema = IInfoportletPortlet
    _template = ViewPageTemplateFile('infoportlet.pt')

    def render(self):
        return self._template()


    @ram.cache(cache_key_news)
    def get_info(self):
        return self._data()

    def get_current(self):
        return api.user.get_current().getUserName()

    def _data(self):
        result = []
        user = self.get_current()

        projects = api.content.find(portal_type='Project')
        urls = [brain.project_url for brain in projects] if projects else []

        for siteurl in urls:
            try:
                response = requests.get(
                    f'{siteurl}/@item_count?user={user}',
                    timeout=3,
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                )

                if response.status_code == 200:
                    body = response.json()
                    dashboard = body.get('dashboard-list')

                    if dashboard:
                        result.append({
                            'name': dashboard['short_name'],
                            'url': siteurl,
                            'short_name': dashboard['short_name'],
                            'project_color': dashboard['project_color'],
                            'portlet_content': dashboard['portlet_content'],
                        })

            except requests.exceptions.RequestException:
                pass  # avoid noisy prints in production

        return result
 
  

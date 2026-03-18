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

import time
import socket
 


# 30 minutes in seconds
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

    refresh = self.request.get('refresh', None)
    if refresh:
        # unique key every time → bypass cache
        return f"news-{user}-{time.time()}"
    return f"news-{user}-{t}"


@ram.cache(cache_key_news) 
class Renderer(base.Renderer):
    schema = IInfoportletPortlet
    _template = ViewPageTemplateFile('infoportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return self._template()
    
    def get_info(self):
        return self._data()    
 
    def get_current(self):
        current = api.user.get_current()
        #return current.getId()
        return current.getUserName()
        # return current.getProperty('email')
    
    def _data(self):   
        urls = None
        
        result = []    
        
        projects = api.content.find(portal_type='Project')

        # 2) Create a list of URLs
        if projects:
            urls = [brain.project_url for brain in projects]
            
        if urls:
            for siteurl in urls:
                try:                
                    response = requests.get(f'{siteurl}/@item_count?user={self.get_current()}', timeout=3,
                                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
                    if response.status_code == 200:
                        body = response.json()
                        if body['dashboard-list'] != None:
                            
                            result.append({
                                        'name': body['dashboard-list']['short_name'], 
                                        'url': siteurl, 
                                        'short_name':  body['dashboard-list']['short_name'],
                                        'project_color': body['dashboard-list']['project_color'],
                                        'portlet_content': body['dashboard-list']['portlet_content'],
                            })
                
                except requests.exceptions.ConnectionError:
                    print("Failed to connect to the server. Please check your network or URL.")
                except requests.exceptions.Timeout:
                    print("The request timed out. Try again later.")
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
            
        return result
 
  

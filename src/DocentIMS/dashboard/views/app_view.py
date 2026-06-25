# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.interface import Interface
from plone import api
from plone.memoize import ram
from datetime import datetime
from .api_client import current_username, fetch_item_count
import time
import logging


logger = logging.getLogger(__name__)

# 15 minutes in seconds
CACHE_TIMEOUT = 15 * 60


def cache_key_buttons(method, self):
    user = self.get_current()
    t = int(time.time() / CACHE_TIMEOUT)

    refresh = self.request.get('refresh', None)
    if refresh:
        return f"buttons-{user}-refresh"

    return f"buttons-{user}-{t}"


class IAppView(Interface):
    """ Marker Interface for IAppView"""


class AppView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('app_view.pt')

    def __call__(self):
        return self.index()

    def get_current_time(self):
        # Get the current local time
        now = datetime.now()
        return now.strftime('%d %b %I:%M %p')

    @ram.cache(cache_key_buttons)
    def get_buttons(self):
        # 1) Find all 'Project' items
        projects = api.content.find(portal_type='Project')

        # 2) Build (project_url, absolute_url) pairs
        urls = [(brain.project_url, brain.getURL()) for brain in projects]

        buttons = []
        for siteurl, absolute_url in urls:
            body = fetch_item_count(siteurl, self.get_current(), timeout=2)
            if not body:
                continue
            dashboard_list = body.get('dashboard-list')
            if dashboard_list:
                buttons.append({
                    'name': dashboard_list.get('short_name'),
                    'url': siteurl,
                    'edit_url': absolute_url,
                    'project_color': dashboard_list.get('project_color'),
                    'last_login_time': dashboard_list.get('last_login_time'),
                })

        return buttons

    def get_current(self):
        return current_username()

    def check_editperm(self):
        roles = api.user.get_current().getRoles()
        allowed = {
            'Manager',
            'Site Administrator',
            'Dashboard Manager',
            'Project Manager',
        }
        return bool(allowed.intersection(roles))

    def get_fullname(self):
        return api.user.get_current().getProperty('fullname')

    def get_meeting_types(self):
        meeting_types = api.portal.get_registry_record(
            'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types'
        )
        if meeting_types:
            return [
                meeting.get('meeting_type')
                for meeting in meeting_types
                if meeting.get('meeting_type')
            ]
        return []

# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.interface import Interface
from plone import api
from ..interfaces import IDocentimsSettings
from plone.memoize import ram
from .api_client import current_username, fetch_item_count
import time
import logging


logger = logging.getLogger(__name__)

# 15 minutes in seconds
CACHE_TIMEOUT = 15 * 60


def cache_key_subbuttons(method, self):
    user = self.get_current()
    t = int(time.time() / CACHE_TIMEOUT)

    refresh = self.request.get('refresh', None)
    if refresh:
        # unique key every time → bypass cache
        return f"inject-{user}-refresh"

    return f"inject-{user}-{t}"


class IAppInjectView(Interface):
    """ Marker Interface for IAppInjectView"""


class AppInjectView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('app_inject_view.pt')

    def __call__(self):
        self.dashboard_info = self.get_dashboard_info()
        self.portlet_data = self.get_portlet_data()
        return self.index()

    def get_current(self):
        return current_username()

    def get_user_portrait(self):
        """URL of the current user's portrait, or None when they have not
        set one (so the dashboard circle falls back to the generic glyph)."""
        try:
            userid = api.user.get_current().getId()
            if not userid:
                return None
            mtool = api.portal.get_tool('portal_membership')
            portrait = mtool.getPersonalPortrait(userid)
            if portrait is not None and portrait.getId() != 'defaultUser.png':
                return portrait.absolute_url()
        except Exception as e:
            logger.warning("Could not resolve portrait: %s", e)
        return None

    @staticmethod
    def strip_weekday(value):
        """'Tuesday, 23 June 2026, 01:29 PM' -> '23 June 2026, 01:29 PM'.

        Only drops a leading weekday when the value has the expected
        weekday/date/time shape; otherwise returns it unchanged.
        """
        if not value:
            return ''
        parts = value.split(', ')
        if len(parts) >= 3:
            return ', '.join(parts[1:])
        return value

    def get_calendar_list(self):
        dashboard_info = self.get_dashboard_info()
        if dashboard_info and dashboard_info.get('dashboard-list'):
            return dashboard_info['dashboard-list'].get('calendar_list', [])
        return []

    @ram.cache(cache_key_subbuttons)
    def get_dashboard_info(self):
        # Refreshed every 15 minutes or on ?refresh=1 (see cache key).
        siteurl = self.request.get('siteurl', '')
        if not siteurl:
            return None
        basik = api.portal.get_registry_record(
            'dashboard', interface=IDocentimsSettings
        ) or ''
        return fetch_item_count(siteurl, self.get_current(), basic_auth=basik)

    @ram.cache(cache_key_subbuttons)
    def get_portlet_data(self):
        siteurl = self.request.get('siteurl', '')
        if not siteurl:
            return []
        body = fetch_item_count(siteurl, self.get_current())
        dashboard_list = body.get('dashboard-list') if body else None
        if not dashboard_list:
            return []
        return [{
            'name': dashboard_list['short_name'],
            'url': siteurl,
            'short_name': dashboard_list['short_name'],
            'project_color': dashboard_list['project_color'],
            'portlet_content': dashboard_list['portlet_content'],
        }]

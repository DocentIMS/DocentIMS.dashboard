# -*- coding: utf-8 -*-
"""Shared helpers for talking to project sites.

Both AppView and AppInjectView poll each project site's ``@item_count``
endpoint.  This module centralises the current-user lookup and the HTTP
call so the request building, timeout handling, status/JSON guarding and
logging live in exactly one place.
"""
from plone import api
import logging
import requests


logger = logging.getLogger(__name__)


def current_username():
    """Login name of the current user (empty string if anonymous)."""
    user = api.user.get_current()
    return user.getUserName() if user else ''


def fetch_item_count(siteurl, username, basic_auth=None, timeout=3):
    """Fetch and parse a project site's ``@item_count`` payload.

    Returns the decoded JSON ``dict`` on success, or ``None`` on any
    failure (no site url, connection/timeout error, non-200 status or a
    body that is not valid JSON).  A failing project site is logged and
    skipped so it can never break the whole dashboard.
    """
    if not siteurl:
        return None

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    if basic_auth:
        headers['Authorization'] = f'Basic {basic_auth}'

    url = f'{siteurl}/@item_count?user={username}'
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
    except requests.exceptions.ConnectionError:
        logger.warning("Failed to connect to project site %s", siteurl)
        return None
    except requests.exceptions.Timeout:
        logger.warning("Request to project site %s timed out", siteurl)
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Error contacting project site %s: %s", siteurl, e)
        return None

    if response.status_code != 200:
        logger.warning(
            "Project site %s returned HTTP %s", siteurl, response.status_code
        )
        return None

    try:
        return response.json()
    except ValueError as e:
        # 200 with a non-JSON / HTML error body — skip this site.
        logger.warning("Non-JSON response from project site %s: %s", siteurl, e)
        return None

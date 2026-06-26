# -*- coding: utf-8 -*-
"""Shared helpers for building interpolated email messages."""
import logging

from plone import api
from plone.stringinterp.interfaces import IStringInterpolator

logger = logging.getLogger(__name__)


def dashboard_manager_info():
    """(fullname, company) of the first user holding the 'Dashboard Manager'
    role, or ('', '') when there is none.

    Looks the manager up by *role* (not by the DashboardManagers group), and
    catches the role whether it is assigned directly or inherited via a group.
    """
    for user in api.user.get_users():
        try:
            roles = api.user.get_roles(user=user)
        except Exception:
            roles = user.getRoles()
        if 'Dashboard Manager' in roles:
            return (
                user.getProperty('fullname', '') or '',
                user.getProperty('company', '') or '',
            )
    return ('', '')


class SafeDict(dict):
    """dict subclass that leaves unknown ``{placeholders}`` untouched."""

    def __missing__(self, key):
        return "{" + key + "}"


def build_message(raw_message, obj, context_vars):
    # 1. Python {} variables. A client-edited template may contain literal
    #    braces (e.g. CSS in a <style> block); those make str.format_map raise.
    #    In that case skip the {} pass and rely on the ${} interpolation below
    #    rather than failing the whole send.
    try:
        message = raw_message.format_map(SafeDict(context_vars))
    except (ValueError, IndexError, KeyError) as exc:
        logger.warning(
            "Email template has literal braces; skipping {} substitution: %s", exc
        )
        message = raw_message

    # 2. Plone ${} variables
    interpolator = IStringInterpolator(obj)
    message = interpolator(message)

    return message

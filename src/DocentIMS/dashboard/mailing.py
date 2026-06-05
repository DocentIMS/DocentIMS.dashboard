# -*- coding: utf-8 -*-
"""Shared helpers for building interpolated email messages."""
from plone.stringinterp.interfaces import IStringInterpolator


class SafeDict(dict):
    """dict subclass that leaves unknown ``{placeholders}`` untouched."""

    def __missing__(self, key):
        return "{" + key + "}"


def build_message(raw_message, obj, context_vars):
    # 1. Python {} variables
    message = raw_message.format_map(SafeDict(context_vars))

    # 2. Plone ${} variables
    interpolator = IStringInterpolator(obj)
    message = interpolator(message)

    return message

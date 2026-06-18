# -*- coding: utf-8 -*-
"""Shared helpers for building interpolated email messages."""
import logging

from plone.stringinterp.interfaces import IStringInterpolator

logger = logging.getLogger(__name__)


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

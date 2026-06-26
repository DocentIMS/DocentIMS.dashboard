# -*- coding: utf-8 -*-
"""@docent_config — expose the Dashboard's canonical control-panel data.

The seven-tab "Add-on Configuration" control panel on the Dashboard is the
canonical source for the reference data that every team site needs: member
roles, company roles, companies, meeting types and meeting locations.

This service returns that data as plain JSON so it can be synced down to a
team site (by the team-site "Sync data with Dashboard" button, or by the
Dashboard's own auto-push on connector creation). The email-message tabs are
intentionally NOT included — those stay on the Dashboard.
"""
from plone import api
from plone.restapi.services import Service
from zExceptions import Unauthorized

import logging


logger = logging.getLogger(__name__)

# Registry keys for the five tabs we sync. See IDocentimsSettings.
_REG = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.%s'
_MEMBER_ROLES = _REG % 'vokabularies'       # IVocabulari  -> vocabulary_entry
_COMPANY_ROLES = _REG % 'vokabularies3'     # IVocabulari3 -> vocabulary_entry
_LOCATIONS = _REG % 'location_names'        # IVocabulari4 -> location_name
_MEETING_TYPES = _REG % 'meeting_types'     # IMeetingRows -> meeting_type/title/summary
_COMPANIES = _REG % 'companies'             # ICompany     -> full company record

_COMPANY_FIELDS = (
    'full_company_name',
    'short_company_name',
    'company_letter_kode',
    'company_full_street_address',
    'company_other_address',
    'company_city',
    'company_zip',
    'company_state',
)


def _rows(key):
    """Registry value as a list of dict rows (empty list when unset)."""
    return list(api.portal.get_registry_record(key) or [])


def collect_dashboard_config():
    """Assemble the canonical tab data into a JSON-serialisable dict.

    Shared so both the @docent_config GET service and (later) the auto-push
    on connector creation produce exactly the same payload.
    """
    member_roles = [
        r.get('vocabulary_entry') for r in _rows(_MEMBER_ROLES)
        if r.get('vocabulary_entry')
    ]
    company_roles = [
        r.get('vocabulary_entry') for r in _rows(_COMPANY_ROLES)
        if r.get('vocabulary_entry')
    ]
    meeting_locations = [
        r.get('location_name') for r in _rows(_LOCATIONS)
        if r.get('location_name')
    ]
    meeting_types = [
        {
            'meeting_type': r.get('meeting_type'),
            'meeting_title': r.get('meeting_title'),
            'meeting_summary': r.get('meeting_summary'),
        }
        for r in _rows(_MEETING_TYPES)
        if r.get('meeting_type')
    ]
    companies = [
        {field: r.get(field) for field in _COMPANY_FIELDS}
        for r in _rows(_COMPANIES)
        if r.get('full_company_name') or r.get('short_company_name')
    ]

    return {
        'member_roles': member_roles,
        'company_roles': company_roles,
        'meeting_locations': meeting_locations,
        'meeting_types': meeting_types,
        'companies': companies,
    }


class DocentConfigGet(Service):
    """GET @docent_config -> canonical control-panel data as JSON."""

    def reply(self):
        # Org reference data: never serve it to anonymous callers. Team sites
        # call with the shared Basic-auth token (same one used for @users).
        if api.user.is_anonymous():
            raise Unauthorized
        return collect_dashboard_config()

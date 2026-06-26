# TODO

## Sync control-panel reference data from the Dashboard to team sites

### Background / corrected diagnosis (2026-06)
The Dashboard's "Add-on Configuration" control panel (`@@medialog_controlpanel`)
is the **canonical source** for reference data: member roles, company roles,
companies, meeting types, meeting locations.

**The team site already PULLS this data from the Dashboard — by design.** In
`DocentIMS.ActionItems/vocabularies.py`, every control-panel pulldown is a
`Choice` bound to a `Dashboard…Vocabulary` factory
(`DashboardProjectRolesVocabulary`, `DashboardCompanyRolesVocabulary`,
`DashboardLocationsVocabulary`, `DashboardMeetingTypesVocabulary`,
`DashboardCompany…`). Each calls `get_registry_record("DocentIMS.dashboard…")`,
which fetches live from the Dashboard. The PM opens each tab, the pulldown is
filled from the Dashboard, the PM picks the subset that applies, and saves it
into the team site's own records.

So a **push from the Dashboard is the wrong tool** — it writes into the field
the PM picks *from*, which is why it kept failing with HTTP 500
(`ConstraintNotSatisfied`: the Choice validates against the pulled vocabulary).
The auto-push has been **removed** (see "DONE" below).

### The real bug: the team-site PULL is unreliable
`get_registry_records()` in `vocabularies.py` does:
`GET {dashboard_url}/@registry` with **timeout=2s**, which fetches the **entire**
Plone registry (huge). Espen's own note: `# Not working, it gets everything`. It
frequently times out → vocabularies come back empty → "the data doesn't come
through."

### DONE (this repo — Dashboard side)
- [x] `GET @docent_config` REST service + `collect_dashboard_config()` helper
      (`api/services/docent_config/get.py`): returns ONLY the five lists, small
      and fast — the right source for the team site to pull from.
- [x] **Removed** the connector auto-push (`push_config_to_site` /
      `_show_config_message` and the handler call) — it fought the pull design
      and 500'd. The connector handler is back to users-only.

### TODO — fix the pull (in DocentIMS.ActionItems / Espen's repo)
- [ ] Point the `Dashboard…Vocabulary` fetch at the Dashboard's
      **`@docent_config`** instead of the giant `@registry` (small/fast →
      reliable). Map: member_roles→roles pulldown, company_roles, meeting_types,
      meeting_locations, companies.
- [ ] Raise the 2-second timeout in `get_registry_records()` (e.g. 8–10s).
- [ ] Confirm `dashboard_url` + `dashboard` (Basic auth) registry records on the
      team site point at the live Dashboard.

### TODO — manual "Sync data with Dashboard" button (optional, Espen's repo)
- [ ] A button on `@@dims_controlpanel` that force-refreshes the pulled
      vocabularies (bypasses the 15-min cache) so a PM can re-pull on demand.

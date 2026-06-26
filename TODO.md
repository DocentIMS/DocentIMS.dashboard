# TODO

## Sync control-panel reference data from the Dashboard to team sites

### Background / diagnosis (2026-06)
The Dashboard's "Add-on Configuration" control panel (`@@medialog_controlpanel`,
7 tabs) is the **canonical source** for reference data: member roles, company
roles, companies, meeting types, meeting locations (plus email-message
templates, which stay on the Dashboard).

When a **Project connector** is created/saved, the only thing pushed to the
team site is the **selected users** (`subscribers/add_users_on_project_site.py`
→ `POST …/@users`, `…/@groups`). **None of the tab data is ever sent.** That is
why member roles / company roles etc. are missing on team sites — there is no
transport for them today (it is not intermittent; it never happens).

The team site is a **separate Plone product** (control panel `@@dims_controlpanel`,
endpoints `@users` / `@groups` / `@item_count`) — most likely in **Espen's repo**,
not in `DocentIMS.dashboard`. So the receiving/UI halves below must be done there.

### Agreed design: BOTH auto-push + manual button

#### DONE (this repo — Dashboard side)
- [x] `GET @docent_config` REST service + shared `collect_dashboard_config()`
      helper (`api/services/docent_config/get.py`). Returns all five tabs'
      canonical data as JSON. This is the data contract both halves rely on.

#### TODO — auto-push (needs the team-site / Espen repo)
- [ ] On connector create/save (`add_users_on_project_site.handler`, or a new
      sibling handler), after users, push `collect_dashboard_config()` to the
      team site.
- [ ] Decide the receiving mechanism on the team site:
      - a custom receiver endpoint (e.g. `POST …/@docent_config` in the
        team-site product) that writes into its own registry, **or**
      - a stock `PATCH …/@registry` if we map to the team site's exact
        registry keys (unknown until we have that repo).
- [ ] Use the existing Basic-auth token (`IDocentimsSettings.dashboard`) the
      user-push already uses; guard + log so a failed sync never aborts the
      connector save.

#### TODO — manual "Sync data with Dashboard" button (needs the team-site / Espen repo)
- [ ] Add a button on the team site at its add-on configuration page
      (`@@dims_controlpanel`), next to the matching tabs.
- [ ] Button pulls `GET {dashboard_url}/@docent_config` and writes the data
      into the team site's own control-panel registry.
- [ ] Lets a PM re-sync on demand without re-saving the connector on the
      Dashboard.

### Open questions for when the team-site repo is available
- Exact registry interface/keys the team-site product uses for these vocabs.
- Whether to merge (add missing) or replace on sync.
- Whether companies/meeting types sync as full records or just names.

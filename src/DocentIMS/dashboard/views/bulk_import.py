# -*- coding: utf-8 -*-
import io
import requests
import pandas as pd
from io import BytesIO

from plone import api
from Products.Five import BrowserView
from zope.interface import Interface
from zope.schema import Choice
from z3c.form import form, field, button
from plone.namedfile.field import NamedBlobFile
from openpyxl import load_workbook


class IBulkImportSchema(Interface):
    """Shared schema for all import types."""

    local_excel_file = Choice(
        title=u"Alternative 1: Select Excel file from site",
        vocabulary="DocentIMS.dashboard.ExcelFiles",
        required=False,
    )

    csv_file = NamedBlobFile(
        title=u"Alternative 2: Manually select Excel file",
        description=u"Upload an Excel file to import.",
        required=False,
    )


class BulkImport(form.Form):
    fields = field.Fields(IBulkImportSchema)
    ignoreContext = True
    label = u"Import from Excel"
    description = (
        u"Each button represents a data type you can import. If a button is "
        u"greyed out, that data has already been imported—but you can click it "
        u"again at any time to upload an updated Excel file and refresh the data."
    )

    def updateActions(self):
        super(BulkImport, self).updateActions()
        self.actions["cancel"].addClass("cancelbutton")

        button_keys = [
            {'name': "companies",         'key': 'DocentIMS.dashboard.interfaces.IDocentimsSettings.companies'},
            {'name': "meeting_types",     'key': 'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types'},
            {'name': "team_roles",        'key': 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies'},
            {'name': "meeting_locations", 'key': 'DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names'},
            {'name': "company_roles",     'key': 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3'},
        ]

        for act_button in button_keys:
            key_content = list(api.portal.get_registry_record(act_button['key']) or [])
            if len(key_content) > 1:
                self.actions[act_button['name']].addClass("duset")

        if len(list(api.user.get_users())) > 2:
            self.actions['import_users'].addClass("duset")

    # ── BUTTON: Users ─────────────────────────────────────────────────────
    @button.buttonAndHandler(u"Import Users", name='import_users')
    def handleImportUsers(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_users(raw)
        self._clear_file_widget()

    # ── BUTTON: Companies ─────────────────────────────────────────────────
    @button.buttonAndHandler(u"Companies", name='companies')
    def handleImportCompanies(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_companies(raw)
        self._clear_file_widget()

    # ── BUTTON: Company Roles ─────────────────────────────────────────────
    # FIX: Was named handleImportRolesLoc — same as the two methods below,
    # causing Python to silently discard both earlier definitions.  Each
    # button handler now has a unique method name.
    @button.buttonAndHandler(u"Company Roles", name="company_roles")
    def handleImportCompanyRoles(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_roles_locations(raw)
        self._clear_file_widget()

    # ── BUTTON: Member Roles ──────────────────────────────────────────────
    # FIX: Was named handleImportRolesLoc — shadowed by the definition above.
    @button.buttonAndHandler(u"Member Roles", name='team_roles')
    def handleImportMemberRoles(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_roles_locations(raw)
        self._clear_file_widget()

    # ── BUTTON: Meeting Types ─────────────────────────────────────────────
    @button.buttonAndHandler(u"Meeting Types", name="meeting_types")
    def handleImportMeetings(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_meetings(raw)
        self._clear_file_widget()

    # ── BUTTON: Meeting Locations ─────────────────────────────────────────
    # FIX: Was named handleImportRolesLoc — completely unreachable because
    # Python only kept the last of the three identically-named methods.
    @button.buttonAndHandler(u"Meeting Locations", name='meeting_locations')
    def handleImportMeetingLocations(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        self.status = self.import_roles_locations(raw)
        self._clear_file_widget()

    # ── BUTTON: Done ──────────────────────────────────────────────────────
    @button.buttonAndHandler(u"Done", name="cancel")
    def handleCancel(self, action):
        came_from = self.request.get('came_from') or api.portal.get().absolute_url()
        return self.request.response.redirect(came_from)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _clear_file_widget(self):
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None

    def _extract_raw(self):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return None

        file_data = data.get('csv_file')
        if file_data:
            if hasattr(file_data, 'data'):
                return file_data.data
            elif hasattr(file_data, 'read'):
                return file_data.read()
            elif isinstance(file_data, (bytes, bytearray)):
                return bytes(file_data)

        excel_obj = data.get("local_excel_file")
        if excel_obj:
            return excel_obj.file.data

        self.status = u"Please upload an Excel file or select one from the site."
        return None

    # ── Users import ──────────────────────────────────────────────────────

    def import_users(self, raw):
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        wb = load_workbook(filename=BytesIO(raw))
        ws = wb.active
        image_map = {}
        for img in ws._images:
            cell = img.anchor._from.row - 1, img.anchor._from.col
            image_map[cell] = img

        created_users = []
        portal_membership = api.portal.get_tool('portal_membership')

        for row_idx, row in enumerate(rows):
            email = row.get("email")
            if not email:
                continue

            required_fields = [
                "first_name", "last_name", "fullname",
                "cellphone", "officephone", "company",
            ]
            if any(not row.get(f) for f in required_fields):
                continue

            username = row.get("user_name")
            if not username or api.user.get(username=username):
                continue

            user = api.user.create(
                username=username,
                password=api.portal.get_tool("portal_registration").generatePassword(),
                properties={
                    "email": email,
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "fullname": row.get("fullname"),
                    "cellphone_number": row.get("cellphone"),
                    "office_phone_number": row.get("officephone"),
                    "your_team_role": row.get("your_team_role"),
                    "company": row.get("company"),
                    "description": row.get("prj_related_skills"),
                    "notes": row.get("notes"),
                },
            )

            portrait_img = None
            if "portrait" in df.columns:
                portrait_col = df.columns.get_loc("portrait")
                cell_key = (row_idx, portrait_col)
                if cell_key in image_map:
                    portrait_img = BytesIO(image_map[cell_key]._data())
                    portrait_img.filename = "portrait.jpg"
                elif row.get("portrait", "").startswith("http"):
                    try:
                        resp = requests.get(row["portrait"], timeout=10)
                        if resp.status_code == 200:
                            portrait_img = BytesIO(resp.content)
                            portrait_img.filename = "portrait.jpg"
                    except Exception:
                        pass

            if portrait_img:
                portal_membership.changeMemberPortrait(portrait_img, user.getUserId())

            created_users.append(username)

        if created_users:
            return f"Imported {len(created_users)} users: {', '.join(created_users)}"
        return "No new users imported."

    # ── Companies import ──────────────────────────────────────────────────

    def import_companies(self, raw):
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        reg_key = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.companies'

        # FIX: Load registry once before the loop, write once after.
        # The original code read and wrote inside the loop (N reads + N writes).
        companies = list(api.portal.get_registry_record(reg_key) or [])
        existing_codes = {c.get('company_letter_kode') for c in companies if c.get('company_letter_kode')}
        created = 0

        required_fields = ["full_company_name", "short_company_name",
                           "three_letter_code", "street_address", "city",
                           "state", "zip_code"]

        for row in rows:
            if any(not row.get(f) for f in required_fields):
                continue
            code = row.get("three_letter_code")
            if code in existing_codes:
                continue
            companies.append({
                'full_company_name': row.get("full_company_name"),
                'short_company_name': row.get("short_company_name"),
                'company_letter_kode': code,
                'company_role': None,
                'company_full_street_address': row.get("street_address"),
                'company_other_address': row.get("other_address"),
                'company_city': row.get("city"),
                'company_state': row.get("state"),
                'company_zip': row.get("zip_code"),
            })
            existing_codes.add(code)
            created += 1

        api.portal.set_registry_record(reg_key, companies)
        return f"Imported {created} new companies."

    # ── Meetings import ───────────────────────────────────────────────────

    def import_meetings(self, raw):
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        reg_key = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types'

        # FIX: Load registry once before the loop, write once after.
        meetings = list(api.portal.get_registry_record(reg_key) or [])
        existing = {m.get("meeting_type") for m in meetings if m.get("meeting_type")}
        created = 0

        for row in rows:
            if not all(row.get(f) for f in ["meeting_type", "meeting_title", "meeting_tag"]):
                continue
            code = row.get("meeting_type")
            if code in existing:
                continue
            meetings.append({
                "meeting_type": row.get("meeting_type"),
                "meeting_title": row.get("meeting_title"),
                "meeting_summary": row.get("meeting_tag"),
            })
            existing.add(code)
            created += 1

        api.portal.set_registry_record(reg_key, meetings)
        return f"Imported {created} new meeting types."

    # ── Roles & locations import ──────────────────────────────────────────

    def import_roles_locations(self, raw):
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        REG_MEMBER_ROLES  = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies'
        REG_LOCATIONS     = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names'
        REG_COMPANY_ROLES = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3'

        # FIX: Load all three registry lists once before the loop.
        member_roles   = list(api.portal.get_registry_record(REG_MEMBER_ROLES) or [])
        location_names = list(api.portal.get_registry_record(REG_LOCATIONS) or [])
        company_roles  = list(api.portal.get_registry_record(REG_COMPANY_ROLES) or [])

        existing_member  = {x.get('vocabulary_entry') for x in member_roles if x.get('vocabulary_entry')}
        existing_loc     = {x.get('location_name') for x in location_names if x.get('location_name')}
        existing_company = {x.get('vocabulary_entry') for x in company_roles if x.get('vocabulary_entry')}

        created = 0

        for row in rows:
            if row.get("member_roles"):
                val = row["member_roles"]
                if val not in existing_member:
                    member_roles.append({'vocabulary_entry': val})
                    existing_member.add(val)
                    created += 1

            if row.get("meeting_locations"):
                val = row["meeting_locations"]
                if val not in existing_loc:
                    location_names.append({'location_name': val})
                    existing_loc.add(val)
                    created += 1

            if row.get("company_roles"):
                val = row["company_roles"]
                if val not in existing_company:
                    company_roles.append({'vocabulary_entry': val})
                    existing_company.add(val)
                    created += 1

        # FIX: Write each registry value once after the loop completes.
        api.portal.set_registry_record(REG_MEMBER_ROLES, member_roles)
        api.portal.set_registry_record(REG_LOCATIONS, location_names)
        api.portal.set_registry_record(REG_COMPANY_ROLES, company_roles)

        return f"Imported {created} new role/location entries."

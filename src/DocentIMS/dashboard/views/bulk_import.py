# -*- coding: utf-8 -*-
import io
import requests
import pandas as pd
from io import BytesIO

from plone import api
from Products.Five import BrowserView
from zope.interface import Interface
from zope.schema import Bytes
from plone.app.vocabularies.catalog import CatalogSource
from zope.schema import Choice
from z3c.form import form, field, button
from plone.namedfile.field import NamedBlobFile
# from zope.schema.interfaces import IContextSourceBinder
# from zope.interface import provider
# from zope.component.hooks import getSite
# from plone.namedfile.file import NamedBlobImage
from openpyxl import load_workbook
 

 

class IBulkImportSchema(Interface):
    """Shared schema for both Users and Companies imports"""
    
    
    local_excel_file = Choice(
        title=u"Select Excel file from site",
        vocabulary="DocentIMS.dashboard.ExcelFiles",
        required=False
    )
    
    csv_file = NamedBlobFile(
        title=u"Alternatively: Manually select Excel file",
        description=u"Upload an Excel file to import.",
        required=False
    )
        


class BulkImport(form.Form):
    fields = field.Fields(IBulkImportSchema)
    ignoreContext = True
    label = u"Import from Excel"
    description = u"Each button represents a data type you can import. If a button is greyed out, that data has already been imported—but you can click it again at any time to upload an updated Excel file and refresh the data on the website."
    
    def updateActions(self):
        super(BulkImport, self).updateActions()
        self.actions["cancel"].addClass("cancelbutton")
        
        button_keys = [
            { 'name': "companies",          'key' : 'DocentIMS.dashboard.interfaces.IDocentimsSettings.companies'},
            { 'name': "meeting_types",      'key' : 'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types'},    
            { 'name': "team_roles",         'key' : 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies'},
            { 'name': "meeting_locations",  'key' : 'DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names'},
            { 'name': "company_roles",      'key' : 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3'},
        ]
        
        # Change opacity if value already exists
        for act_button in button_keys:
            reg_key = act_button['key']
            name = act_button['name']
            key_content = list(api.portal.get_registry_record(reg_key) or [])
            if len(key_content) > 1:
                self.actions[name].addClass("duset")
            users = api.user.get_users()
            if len(list(users)) > 2:
                self.actions['import_users'].addClass("duset")
            
    
    @button.buttonAndHandler(u"Done", name = "cancel")
    def handleCancel(self, action):
         # Try to read "came_from" from the request
        came_from = self.request.get('came_from')

        if not came_from:
            # fall back to site root (or any other default)
            came_from = api.portal.get().absolute_url()

        return self.request.response.redirect(came_from)
    
        # url = api.portal.get().absolute_url()  
        # return self.request.REQUEST["RESPONSE"].redirect(url)

    #
    # ----------- BUTTON: Users ----------------------------------------------
    #
    @button.buttonAndHandler(u"Import Users", name='import_users')
    def handleImportUsers(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_users(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
        

    #
    # ----------- BUTTON: Companies ------------------------------------------
    #
    @button.buttonAndHandler(u"Companies")
    def handleImportCompanies(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_companies(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
         
    
    # ----------------------------------------------------------------------
    # ------------------ BUTTON: ROLES & LOCATIONS ------------------------
    # ----------------------------------------------------------------------
    @button.buttonAndHandler(u"Company Roles", name = "company_roles")
    def handleImportRolesLoc(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_roles_locations(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
 

    @button.buttonAndHandler(u"Member Roles", name='team_roles' )
    def handleImportRolesLoc(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_roles_locations(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
 
     
    # ----------------------------------------------------------------------
    # ------------------------- BUTTON: MEETINGS ---------------------------
    # ----------------------------------------------------------------------
    @button.buttonAndHandler(u"Meeting Types", name = "meeting_types")
    def handleImportMeetings(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_meetings(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
 

   
    @button.buttonAndHandler(u"Meeting Locations", name='meeting_locations' )
    def handleImportRolesLoc(self, action):
        raw = self._extract_raw()
        if raw is None:
            return
        msg = self.import_roles_locations(raw)
        self.status = msg
        
        self.request.form['csv_file'] = None
        self.widgets['csv_file'].value = None
 
 
        


    # -------------------------------------------------------------------------
    # SHARED RAW EXTRACTOR
    # -------------------------------------------------------------------------
    def _extract_raw(self):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return None

        file_data = data['csv_file']
        
        if file_data:
            # 1 Convert upload to bytes
            if hasattr(file_data, 'data'):                 # NamedBlobFile
                return file_data.data
            elif hasattr(file_data, 'read'):               # FileUpload
                return file_data.read()
            elif isinstance(file_data, (bytes, bytearray)):
                return bytes(file_data)

        # 
        #file_data = data['local_excel_file']
        # 1) Picked from site
        excel_obj = data.get("local_excel_file")
        if excel_obj:
            # Should be bytes
            return excel_obj.file.data

        raise ValueError("Unsupported type for Excel file")



    # -------------------------------------------------------------------------
    # USERS IMPORT
    # -------------------------------------------------------------------------
    def import_users(self, raw):

        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        # Load workbook for image handling
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
                "cellphone", "officephone", "company"
            ]
            missing = [f for f in required_fields if not row.get(f)]
            if missing:
                continue

            username = row.get("user_name")
            if api.user.get(username=username):
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
                }
            )

            # Handle portrait
            portrait_img = None
            if "portrait" in df.columns:
                portrait_col = df.columns.get_loc("portrait")
                cell_key = (row_idx, portrait_col)

                # Embedded image
                if cell_key in image_map:
                    portrait_img = BytesIO(image_map[cell_key]._data())
                    portrait_img.filename = "portrait.jpg"

                # URL image
                elif row.get("portrait", "").startswith("http"):
                    try:
                        resp = requests.get(row["portrait"])
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
        else:
            return "No new users imported."

    # -------------------------------------------------------------------------
    # COMPANIES IMPORT
    # -------------------------------------------------------------------------
    def import_companies(self, raw):

        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        created_companies = 0

        reg_key = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.companies'
        companies = list(api.portal.get_registry_record(reg_key) or [])
        existing_codes = {c.get('company_letter_kode') for c in companies if c.get('company_letter_kode')}

        for row in rows:

            required_fields = [
                "full_company_name",
                "short_company_name",
                "three_letter_code",
                "street_address",
                "city",
                "state",
                "zip_code",
            ]
            missing = [f for f in required_fields if not row.get(f)]
            if missing:
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
            created_companies += 1

        api.portal.set_registry_record(reg_key, companies)

        return f"Imported {created_companies} new companies."



    # ======================================================================
    # ======================== MEETINGS IMPORT =============================
    # ======================================================================
    def import_meetings(self, raw):

        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        reg_key = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types'
        meetings = list(api.portal.get_registry_record(reg_key) or [])
        existing = {m.get("meeting_type") for m in meetings if m.get("meeting_type")}

        created = 0

        for row in rows:
            required = ["meeting_type", "meeting_title", "meeting_tag"]
            missing = [f for f in required if not row.get(f)]
            if missing:
                continue

            code = row.get("meeting_type")

            if code not in existing:
                created += 1
                meetings.append({
                    "meeting_type":    row.get("meeting_type"),
                    "meeting_title":   row.get("meeting_title"),
                    "meeting_summary": row.get("meeting_tag")
                })
                existing.add(code)

        api.portal.set_registry_record(reg_key, meetings)
        return f"Imported {created} New Meetings"

    # ======================================================================
    # =================== ROLES & LOCATIONS IMPORT =========================
    # ======================================================================
    def import_roles_locations(self, raw):

        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        created = 0

        # Registry keys
        REG_MEMBER_ROLES   = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies'
        REG_LOCATIONS      = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names'
        REG_COMPANY_ROLES  = 'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3'

        member_roles     = list(api.portal.get_registry_record(REG_MEMBER_ROLES) or [])
        location_names   = list(api.portal.get_registry_record(REG_LOCATIONS) or [])
        company_roles    = list(api.portal.get_registry_record(REG_COMPANY_ROLES) or [])

        existing_member  = {x.get('vocabulary_entry') for x in member_roles if x.get('vocabulary_entry')}
        existing_loc     = {x.get('location_name')     for x in location_names if x.get('location_name')}
        existing_company = {x.get('vocabulary_entry') for x in company_roles if x.get('vocabulary_entry')}

        for row in rows:

            # -----------------------
            # Member Roles
            # -----------------------
            if row.get("member_roles"):
                val = row["member_roles"]
                if val not in existing_member:
                    created += 1
                    member_roles.append({'vocabulary_entry': val})
                    existing_member.add(val)
                api.portal.set_registry_record(REG_MEMBER_ROLES, member_roles)
        

            # -----------------------
            # Meeting Locations
            # -----------------------
            if row.get("meeting_locations"):
                val = row["meeting_locations"]
                if val not in existing_loc:
                    created += 1
                    location_names.append({'location_name': val})
                    existing_loc.add(val)
                api.portal.set_registry_record(REG_LOCATIONS, location_names)
        

            # -----------------------
            # Company Roles
            # -----------------------
            if row.get("company_roles"):
                val = row["company_roles"]
                if val not in existing_company:
                    created += 1
                    company_roles.append({'vocabulary_entry': val})
                    existing_company.add(val)
                # Save updated registries
                api.portal.set_registry_record(REG_COMPANY_ROLES, company_roles)

        return f"Imported {created} New Role/Location Entries"

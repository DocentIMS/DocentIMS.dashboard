# -*- coding: utf-8 -*-
# NOTE: This view is currently not registered in ZCML (registration is
# commented out in views/configure.zcml).  The consolidated BulkImport form
# (bulk_import.py, registered as @@import-from-excel) supersedes this file.
# It is retained here with bugs corrected; consider removing once confident
# BulkImport covers all use-cases.

import requests
from plone import api
from zope.interface import Interface
from zope.schema import Bytes
from z3c.form import form, field, button
from plone.namedfile.field import NamedBlobFile
from io import BytesIO
import pandas as pd
from openpyxl import load_workbook


class IUsersImport(Interface):
    """Marker Interface for IUsersImport"""


class ICSVImportFormSchema(Interface):
    csv_file = NamedBlobFile(
        title=u"Excel File",
        description=u"Upload an Excel file to import.",
        required=True,
    )


class UsersImport(form.Form):
    fields = field.Fields(ICSVImportFormSchema)
    ignoreContext = True
    label = u"Import Users from Excel"

    @button.buttonAndHandler(u"Import")
    def handleImport(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        file_data = data['csv_file']

        if hasattr(file_data, 'data'):
            raw = file_data.data
        elif hasattr(file_data, 'read'):
            raw = file_data.read()
        elif isinstance(file_data, (bytes, bytearray)):
            raw = bytes(file_data)
        else:
            raise ValueError("Unsupported upload type for Excel file")

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
        missing_last = []
        portal_membership = api.portal.get_tool('portal_membership')

        for row_idx, row in enumerate(rows):
            email = row.get("email")
            if not email:
                continue

            required_fields = [
                "user_name", "first_name", "last_name", "fullname",
                "cellphone", "officephone", "company",
                "prj_related_skills", "notes",
            ]
            missing = [f for f in required_fields if not row.get(f)]
            if missing:
                missing_last = missing
                continue

            # FIX: Trailing comma made username a tuple instead of a string.
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
                portrait_col_index = df.columns.get_loc("portrait")
                cell_key = (row_idx, portrait_col_index)
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
            self.status = f"Imported {len(created_users)} users: {', '.join(created_users)}"
        else:
            self.status = "All users already exist or no valid rows found."

        if missing_last:
            self.status += f" Last skipped row was missing: {', '.join(missing_last)}."

# -*- coding: utf-8 -*-
import csv
import io
import requests
from plone import api
from Products.Five import BrowserView
from zope.interface import Interface
from zope.schema import Bytes
from z3c.form import form, field, button
from plone.autoform import directives as form_directives
from plone.namedfile.file import NamedBlobImage
from io import BytesIO
import pandas as pd  # needs openpyxl installed



class IUsersImport(Interface):
    """ Marker Interface for IUsersImport"""

class ICSVImportFormSchema(Interface):
    csv_file = Bytes(
        title=u"Excel File",
        description=u"Upload a Excel file with user data",
        required=True
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
        
        # Get raw bytes from the upload (works for NamedBlobFile, FileUpload, or raw bytes)
        if hasattr(file_data, 'data'):                 # plone.namedfile NamedBlobFile
            raw = file_data.data
        elif hasattr(file_data, 'read'):               # ZPublisher FileUpload
            raw = file_data.read()
        elif isinstance(file_data, (bytes, bytearray)):
            raw = bytes(file_data)
        else:
            raise ValueError("Unsupported upload type for Excel file")

        # Read first sheet as strings; requires 'openpyxl' for .xlsx and 'xlrd<2.0' for legacy .xls
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str)

        # Clean NaNs and make headers predictable (optional but helpful)
        df = df.fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Iterate correctly over dict rows
        rows = df.to_dict(orient="records")
        

        created_users = []
        for row in rows:
            email = row.get("email")
            if not email:
                continue  # skip if no email

            username = email.lower().strip()
            if api.user.get(username=username):
                continue  # skip existing

            user = api.user.create(
                username=username,
                email=email,
                password=api.portal.get_tool("portal_registration").generatePassword(),
                properties={
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "fullname": row.get("fullname"),
                    "cellphone": row.get("cellphone"),
                    "officephone": row.get("officephone"),
                    "your_team_role": row.get("your_team_role"),
                    "company": row.get("company"),
                    "notes": row.get("notes"),
                }
            )

            # Handle portrait (URL or local path)
            portrait_url = row.get("portrait")
            if portrait_url:
                try:
                    if portrait_url.startswith("http"):
                        resp = requests.get(portrait_url)
                        if resp.status_code == 200:
                            img_data = NamedBlobImage(data=resp.content,
                                                      filename=u"portrait.jpg")
                            user.setMemberProperties({'portrait': img_data})
                    # Local file handling could be added here
                except Exception:
                    pass

            created_users.append(username)

        self.status = f"Imported {len(created_users)} users: {', '.join(created_users)}"

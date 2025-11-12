# -*- coding: utf-8 -*-
import csv
import io
import requests
from plone import api
from Products.Five import BrowserView
from zope.interface import Interface
from zope.schema import Bytes
from z3c.form import form, field, button
# from plone.autoform import directives as form_directives
from plone.namedfile.file import NamedBlobImage 
from plone.namedfile.field import NamedBlobFile 
from io import BytesIO
import pandas as pd  # needs openpyxl installed
from openpyxl import load_workbook
import requests



class IUsersImport(Interface):
    """ Marker Interface for IUsersImport"""

class ICSVImportFormSchema(Interface):
    # csv_file = Bytes(
    #     title=u"Excel File",
    #     description=u"Upload a Excel file with user data",
    #     required=True
    # )
    
    csv_file = NamedBlobFile(
        title=u"Excel File",
        description=u"Upload a Excel file to import.",
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

        # Get raw bytes from the upload
        if hasattr(file_data, 'data'):                 # plone.namedfile NamedBlobFile
            raw = file_data.data
        elif hasattr(file_data, 'read'):               # ZPublisher FileUpload
            raw = file_data.read()
        elif isinstance(file_data, (bytes, bytearray)):
            raw = bytes(file_data)
        else:
            raise ValueError("Unsupported upload type for Excel file")

        # Read the sheet as strings for the rest of the data
        df = pd.read_excel(BytesIO(raw), sheet_name=0, dtype=str)
        df = df.fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        rows = df.to_dict(orient="records")

        # Load workbook with openpyxl to access images
        wb = load_workbook(filename=BytesIO(raw))
        ws = wb.active

        # Map images to cells
        image_map = {}
        for img in ws._images:  # _images contains all images in the sheet
            cell = img.anchor._from.row - 1, img.anchor._from.col  # zero-based row/col
            image_map[cell] = img

        created_users = []
        portal_membership = api.portal.get_tool('portal_membership')

        for row_idx, row in enumerate(rows):
            email = row.get("email")
            if not email:
                continue

            username = email.lower().strip()
            if api.user.get(username=username):
                continue

            user = api.user.create(
                username=username,
                email=email,
                password=api.portal.get_tool("portal_registration").generatePassword(),
                properties={
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "fullname": row.get("fullname"),
                    "cellphone_number": row.get("cellphone"),
                    "office_phone_number": row.get("officephone"),
                    "your_team_role": row.get("your_team_role"),
                    "company": row.get("company"),
                    "description": row.get("description"),
                }
            )

            # Handle portrait
            portrait_img = None

            # First try embedded image
            portrait_col_index = df.columns.get_loc("portrait")
            cell_key = (row_idx, portrait_col_index)
            if cell_key in image_map:
                portrait_img = BytesIO(image_map[cell_key]._data())  # get image bytes
                portrait_img.filename = "portrait.jpg"

            # If no embedded image, fallback to URL
            elif row.get("portrait") and row.get("portrait").startswith("http"):
                try:
                    resp = requests.get(row.get("portrait"))
                    if resp.status_code == 200:
                        portrait_img = BytesIO(resp.content)
                        portrait_img.filename = "portrait.jpg"
                except Exception:
                    pass

            if portrait_img:
                portal_membership.changeMemberPortrait(portrait_img, user.getUserId())

            created_users.append(username)

        self.status = f"Imported {len(created_users)} users: {', '.join(created_users)}"

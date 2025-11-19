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
from plone.namedfile.field import NamedBlobFile 
from io import BytesIO
import pandas as pd  # needs openpyxl installed
import requests



class ICompaniesImport(Interface):
    """ Marker Interface for ICompaniesImport"""

class ICSVImportFormSchema(Interface):
    
    csv_file = NamedBlobFile(
        title=u"Excel File",
        description=u"Upload a Excel file to import.",
        required=True
    )
 


class CompaniesImport(form.Form):
    fields = field.Fields(ICSVImportFormSchema)
    ignoreContext = True
    label = u"Import Companies from Excel"

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

        
        created_companies = 0
        
        for row_idx, row in enumerate(rows):
            
            required_fields = [
                "full_company_name",
                "short_company_name",
                "three_letter_code",
                "street_address",
                "city",
                "state",
                "zip_code",
            ]
            
            # TO DO: Check only once

            missing = [field for field in required_fields if not row.get(field)]

            if missing:
                self.status = f"Missing required fields: {', '.join(missing)}"
                continue 
            
            companies = list(api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.companies') or [])
            existing_codes = {c.get('company_letter_kode') for c in companies if c.get('company_letter_kode')}

            new_code = row.get("three_letter_code")

            # Only add if code does NOT already exist
            if new_code not in existing_codes:
                
                created_companies += 1

                new_company = {
                            'full_company_name': row.get("full_company_name"),
                            'short_company_name': row.get("short_company_name"),
                            'company_letter_kode': new_code,
                            'company_role': None,
                            'company_full_street_address': row.get("street_address"),
                            'company_other_address': row.get("other_address"),
                            'company_city': row.get("city"),
                            'company_state': row.get("state"),
                            'company_zip': row.get("zip_code"),
                        }

                companies.append(new_company)
                                        
            # Save back to the registry
            api.portal.set_registry_record(
                'DocentIMS.dashboard.interfaces.IDocentimsSettings.companies', companies
            )
                        
                
  

        self.status = f"Imported {created_companies} New Companies"
        
        if missing:
            self.status += f"Missing required fields: {', '.join(missing)}"

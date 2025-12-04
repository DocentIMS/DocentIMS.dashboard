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



class IRolesLocationsImport(Interface):
    """ Marker Interface for IRolesLocationsImport"""

class ICSVImportFormSchema(Interface):
    
    csv_file = NamedBlobFile(
        title=u"Excel File",
        description=u"Upload a Excel file to import.",
        required=True
    )
 

class RolesLocationsImport(form.Form):
    fields = field.Fields(ICSVImportFormSchema)
    ignoreContext = True
    label = u"Import RolesLocations Settings from Excel"

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

        
        created  = 0
        
        for row_idx, row in enumerate(rows):
            
            # required_fields = [
            #     "member_roles",
            #     "company_roles",
            #     "meeting_locations"
            # ]
            
            # TO DO: Check only once
            # missing = [field for field in required_fields if not row.get(field)]

            # if missing:
            #     self.status = f"Missing required fields: {', '.join(missing)}"
            #     continue 
            
            if row.get("member_roles"):
                member_roles = list(api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies') or [])
                existing_codes = {c.get('vocabulary_entry') for c in member_roles if c.get('vocabulary_entry')}
                new_code = row.get("member_roles")
                
                # Only add if code does NOT already exist
                if new_code not in existing_codes:                
                    created  += 1
                    new_member_role = {
                                'vocabulary_entry':     row.get("member_roles") 
                            }

                    member_roles.append(new_member_role)
                                            
                # Save back to the registry
                api.portal.set_registry_record(
                    'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies', member_roles
                )
            
            
            if row.get("meeting_locations"):
                location_names = list(api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names') or [])
                
                existing_codes = {c.get('location_name') for c in location_names if c.get('location_name')}
                new_code = row.get("meeting_locations")
                
                # Only add if code does NOT already exist
                if new_code not in existing_codes:                
                    created  += 1
                    new_location_name = {
                                'location_name':  row.get("meeting_locations") 
                            }

                    location_names.append(new_location_name)
                                            
                # Save back to the registry
                api.portal.set_registry_record(
                    'DocentIMS.dashboard.interfaces.IDocentimsSettings.location_names', location_names
                )
                
            
            if row.get("company_roles"):
                company_roles = list(api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3') or [])      
                existing_codes = {c.get('vocabulary_entry') for c in company_roles if c.get('vocabulary_entry')}
                new_code = row.get("company_roles")
                
                # Only add if code does NOT already exist
                if new_code not in existing_codes:                
                    created  += 1
                    new_company_role = {
                                'vocabulary_entry':     row.get("company_roles") 
                            }

                    company_roles.append(new_company_role)
                                            
                # Save back to the registry
                api.portal.set_registry_record(
                    'DocentIMS.dashboard.interfaces.IDocentimsSettings.vokabularies3', company_roles
                )
                         
   

        self.status = f"Imported {created} New Settings"
        
        # if missing:
        #    self.status += f"Missing required fields: {', '.join(missing)}"

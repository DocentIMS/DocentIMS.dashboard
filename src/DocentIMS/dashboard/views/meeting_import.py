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



class IMeetingImport(Interface):
    """ Marker Interface for IMeetingImport"""

class ICSVImportFormSchema(Interface):
    
    csv_file = NamedBlobFile(
        title=u"Excel File",
        description=u"Upload a Excel file to import.",
        required=True
    )
 

class MeetingImport(form.Form):
    fields = field.Fields(ICSVImportFormSchema)
    ignoreContext = True
    label = u"Import Meetings Settings from Excel"

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

        
        created_meeting = 0
        
        for row_idx, row in enumerate(rows):
            
            required_fields = [
                "meeting_types",
                "meeting_title",
                "meeting_tag"
            ]
            
            # TO DO: Check only once
            missing = [field for field in required_fields if not row.get(field)]

            if missing:
                self.status = f"Missing required fields: {', '.join(missing)}"
                continue 
            
            meetings = list(api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types') or [])
            
            existing_codes = {c.get('meeting_type') for c in meetings if c.get('meeting_type')}
            new_code = row.get("meeting_types")
            
            # Only add if code does NOT already exist
            if new_code not in existing_codes:                
                created_meeting += 1
                new_meeting = {
                            'meeting_type':      row.get("meeting_types"),
                            'meeting_title':     row.get("meeting_title"),
                            'meeting_summary':   row.get("meeting_tag")
                        }

                meetings.append(new_meeting)
                                        
            # Save back to the registry
            api.portal.set_registry_record(
                'DocentIMS.dashboard.interfaces.IDocentimsSettings.meeting_types', meetings
            )
                         
   

        self.status = f"Imported {created_meeting} New Meeting"
        
        if missing:
            self.status += f"Missing required fields: {', '.join(missing)}"

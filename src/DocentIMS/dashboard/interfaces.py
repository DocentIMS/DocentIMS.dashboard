# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from zope import schema
from plone.supermodel import model
from plone.autoform.directives import widget
from zope.interface import alsoProvides
# from collective.z3cform.colorpicker.colorpicker  import ColorpickerFieldWidget
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from z3c.form.browser.password import PasswordFieldWidget


from plone import api
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import  InvalidValue


# from plone.registry.interfaces import IRegistry
# from zope.component import getUtility
# from plone import api

# from zope.interface import Interface
# import base64
# import hashlib
# from cryptography.fernet import Fernet

# # Your custom password
# password = b'supersekretpasswordsupersekretpa'

# # Derive a 32-byte key using a hashing function
# key = base64.urlsafe_b64encode(hashlib.sha256(password).digest())

# # Create a Fernet instance with the derived key
# fernet = Fernet(key)
# from DocentIMS.ActionItems.interfaces import IDocentimsSettings
# from DocentIMS.dashboard.interfaces import IDocentimsSettings 
# KEY = base64.urlsafe_b64encode(b'suxxxxpersekretpasswordsupersekretpa')
# fernet = Fernet(KEY)

from DocentIMS.dashboard import _


     
def not_required_in_debug_mode():
    return not api.env.debug_mode()


def company_letter_kodeConstraint(value):
    """Check that the company_3 letter code is upperclass
    """
    if value != None and value != '':
        if len(value) != 3:
             raise InvalidValue()
             #Works with datagridfield, but will show error message 'Constraint not satisfied /The system could not process the given value.'
             return True
        
        if not value.isupper():
            raise  InvalidValue("Only capital letters for Company 3 letter code")
            return True
    return True

def stateConstraint(value):
    """Check lenght = 2 and upperclass
    """
    if value != None and value != '':
        if len(value) != 2:
             raise InvalidValue()
             #Works with datagridfield, but will show error message 'Constraint not satisfied /The system could not process the given value.'
             return True
        if not value.isupper():
            # Raises error, but do not 'render the text'
            raise  InvalidValue("Only 2 capital letters for State")
            return True
        if not value in [ 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 
                        'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 
                        'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']:
            
            api.portal.show_message(message="Company State does not exist", type='warning')
            #raise InvalidValue()
            #return True

    return True

class IVocabulari4(model.Schema):
    location_name = schema.TextLine(
        title=_(u'Vocabulary entries', 'Locations'),
        description=u"Location Name",
        required=False,
    )
 
 
class IVocabulari(model.Schema):
    vocabulary_entry = schema.TextLine(
        title=_(u'Vocabulary entries', 'Team Roles'),
        description=u"Each team member will be assigned a “Role” during their membership creation.  The role for each member must be created here before their account can be created.",
        required=False,
    )

class IVocabulari3(model.Schema):
    vocabulary_entry = schema.TextLine(
        title=_(u'Vocabulary entries', 'Company Roles'),
        description=u"Each company will be assigned a “Role” during their creation. You need to save this form before continuing",
        required=False,
    )
    
class IMeetingRows(model.Schema):
    meeting_type = schema.TextLine(
        title=_(u'meeting_type', 'Meeting Type'),
        # description=u"Meeting Type",
        required=False,
    )
    
    meeting_title = schema.TextLine(
        title=_(u'meeting_title', 'Meeting Title'),
        # description=u"Default Meeting Title",
        required=False,
    )
     
    meeting_summary = schema.Text(
        title=_(u'Vmeeting_summary', 'Meeting Tag'),
        # description=u"Default Summary",
        required=False,
    )
     
     

class ICompany(model.Schema):
    full_company_name = schema.TextLine(
        required = False,
        title=_(u"label_company_name", default=u"Full Company Name")
        )
    
    short_company_name= schema.TextLine(
        required = False,
        title=_(u"label_company_short_name", default=u"Short Company Name")
        )
    
    company_letter_kode = schema.TextLine(
        required = False,
        title=_(u"label_company_letter_code", default=u"Company 3-letter code (All Caps)"),
        constraint=company_letter_kodeConstraint,
        )

    company_full_street_address = schema.Text(
        required = False,
        title=_(u"label_company_full_street_adress", default=u"Full Street Address")
        )
    company_other_address = schema.Text(
        required = False,
        title=_(u"label_company_other_adress", default=u"Other Address - Optional")
        )

    company_city = schema.TextLine(
        required = False,
        title=_(u"label_company_city", default=u"City")
        )
    
    company_zip = schema.TextLine(
        required = False,
        title=_(u"label_company_ZIP", default=u"ZIP code")
        )
    
    company_state = schema.TextLine(
        required = False,
        title=_(u"label_company_state", default=u"State"),
        constraint=stateConstraint,
        )
    

    

class IDocentimsDashboardLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


# # Utility function to encrypt and decrypt the password
# def encrypt_password(plain_text):
#     return fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

# def decrypt_password(encrypted_text):
#     print('starting')
#     print(encrypted_text)
#     pw = fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
#     print('running')
#     print(pw)
#     return pw

# # Example of storing and retrieving the encrypted password
# def store_password(password):
#     encrypted_password = encrypt_password(password)
#     api.portal.set_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_password',  encrypted_password)

# def retrieve_password():
#     # import pdb; pdb.set_trace()
#     encrypted_password = api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.app_password',  default='admin') 
#     encrypted_password = b'supersekretpasswordsupersekretpa'
#     return decrypt_password('encrypted_password')

# class IVocabulari(model.Schema):
#     location_name = schema.URI(
#         title=_(u'Site URL', 'Sites'),
#         description=u"Sites",
#         required=False,
#     )


class IDocentimsSettings(model.Schema):
    """Adds settings to medialog.controlpanel
    """    
    
    # model.fieldset(
    #     'project',
    #     label=_(u'Dashboard'),
    #     fields=[
    #         'app_buttons',         
    #         ],
    #     )
    
    # widget(app_buttons=DataGridFieldFactory)
    # app_buttons = schema.List(
    #     title = _(u"URL of sites",
    #         default=u""),
    #     description=u"Include 'https://' in front of the domain name.  For example, enter:  https://ibm.com",
    #     # value_type=DictRow(schema=IVocabulari),
    #     value_type=schema.URI(
    #         title= (u'URL'),  
    #     ),     
    #     required=False,
    # )
    
     
    # model.fieldset(
    #     'project',
    #     label=_(u'Project Information'),
    #     fields=[
    #         'project_title',
    #         'project_short_name',
    #         'very_short_name',
    #         'project_description',
    #         'project_contract_number',
    #         'project_document_naming_convention',
    #         'color1',
    #         'color2',
    #         'planning_project',
    #         'template_password',
    #         'dashboard',
    #         'url'
    #         ],
    #     )
    
    widget(dashboard=PasswordFieldWidget)
    dashboard  = schema.TextLine(
        title=_(u'Basic', 'Basic'),
        description=u"Basic",
        required=True,
    )
    
    widget(location_names=DataGridFieldFactory)
    location_names = schema.List(
        title = _(u" ",
            default=u""),
        value_type=DictRow(schema=IVocabulari4),
        required=not_required_in_debug_mode(),
    )
   

    model.fieldset(
        'vocabularies',
        label=_(u'Member Roles'),
        fields=[
            'vokabularies', 
        ] 
    )
    
    model.fieldset(
        'locations',
        label=_(u'Locations'),
        fields=[
            'location_names'
        ] 
    )

    model.fieldset(
        'meeting_types',
        label=_(u'Meeting Types'),
        fields=[
            'meeting_types'
        ] 
    )


    model.fieldset(
        'vocabularies3',
        label=_(u'Company Roles'),
        fields=[
            'vokabularies3',
        ] 
    )

 
    model.fieldset(
        'companies',
        label=_(u'Companies'),
        description=u"Please create all project companies involved in this project.",
        fields=[
            'companies',
            ],
        )

     
    widget(vokabularies=DataGridFieldFactory)
    vokabularies = schema.List(
        title = _(u" ",
            default=u""),
        value_type=DictRow(schema=IVocabulari),
        required=not_required_in_debug_mode(),
    )
    
    widget(vokabularies3=DataGridFieldFactory)
    vokabularies3 = schema.List(
        title = _(u" ",
            default=u""),
        value_type=DictRow(schema=IVocabulari3),
        required=not_required_in_debug_mode(),
    )
    
    widget(meeting_types=DataGridFieldFactory)
    meeting_types = schema.List(
        title = _(u" ",
            default=u""),
        value_type=DictRow(schema=IMeetingRows),
        required=not_required_in_debug_mode(),
    )

    widget(companies=DataGridFieldFactory)
    companies = schema.List(
        title = _(u"Companies",
            default=u"Companies"),
        value_type=DictRow(schema=ICompany), 
         required=not_required_in_debug_mode(),
        
    )
 
 

alsoProvides(IDocentimsSettings, IMedialogControlpanelSettingsProvider)
# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item
# from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from plone import api
 
# from z3c.form import interfaces
# from zope import schema
# from zope.interface import alsoProvides
# from plone.supermodel import model
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.autoform.directives import widget
from plone.app.textfield import RichText
# from plone.app.z3cform.widgets.richtext import RichTextFieldWidget
from collective.z3cform.colorpicker.colorpicker  import ColorpickerFieldWidget
# from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
# from plone import api
# from plone.api.portal import show_message
# from plone.app.contentrules.handlers  import execute_user_rules
# from plone.app.discussion.interfaces import IComment
# from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget, SelectWidget
# from plone.autoform.interfaces import IFormFieldProvider
# from plone.dexterity.interfaces import IDexterityContent
# from plone.namedfile import field
# from plone.registry.field import PersistentField
# from plone.supermodel import model
# from zope.component import adapter
# from zope.interface import implementer
# from zope.interface import Interface
from zope.schema.interfaces import  InvalidValue



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
            
            show_message(message="Company State does not exist", type='warning')
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

    # company_role = schema.Text(
    #     required = False,
    #     title=_(u"label_company_role", default=u"Company role")
    #     )
    
    # company_role = schema.Choice(
    #     required = False,
    #     title=_(u"label_company_role", default=u"Company role"),
    #     vocabulary=u"DocentIMS.ActionItems.CompanyRolesVocabulary",
    # )
        
    #company_logo = schema.Text(
    #    required = False,
    #    title=_(u"label_company_logo", default=u"Company Logo")
    #    )

    #company_logo = field.NamedBlobImage(title=u"Company Logo")


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
        title=_(u"label_company_citye", default=u"City")
        )
    
    company_state = schema.TextLine(
        required = False,
        title=_(u"label_company_state", default=u"State"),
        constraint=stateConstraint,
        )
    

    

class IProject(model.Schema):
    """ Marker interface and Dexterity Python Schema for Project
    """
    
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
    
    
    
    # project_title = schema.TextLine(
    #     required = not_required_in_debug_mode(),
    #     title=_(u"label_title", default=u"Project Full Name"),
    #     description=_(u"",
    #                   default=u""), 
    #     )
    
    title = schema.TextLine(
        title=_(u"label_project_short_name",
        default=u"Project Control Panel"),
        description=_(u"",
                      default=u""),
        required=not_required_in_debug_mode(),
        default=u"Project Control Panel",
    )
    
    
    # very_short_name = schema.TextLine(
    #     title=_(u"label_project_very_short_name",
    #     default=u"Project Very Short Name"),
    #      required=not_required_in_debug_mode(),
    #     description=_(u"",
    #                   default=u"")
    #     )
 
    # project_description = RichText(
    #     title="Project Description",
    #     required=False,
    # )

    # project_contract_number = schema.TextLine(
    #     required = False,
    #     title=_(u"label_project_contract_number", default=u"Project Contract Number"),
    #     description=_(u"",
    #                   default=u""),
    #     )
    
    
    # widget(color1=ColorpickerFieldWidget)
    # color1 = schema.TextLine(
    #     title=u"Project Color",
    #     description=u"",
    #     # max_length=10,
    #     required=not_required_in_debug_mode(),
    #     default="#ff0000"
    # )
    
    # widget(color2=ColorpickerFieldWidget)
    # color2 = schema.TextLine(
    #     title=u"Markings Color",
    #     description=u"",
    #     # max_length=10,
    #     required=not_required_in_debug_mode(),
    #     default="#ff0000"
    # )
    
    # planning_project = schema.Bool(
    #     title=u"Is Planning Project?",
    #     required=False,
    #     default=0,
    # ) 
    
    # widget(project_document_naming_convention=SelectFieldWidget)
    # project_document_naming_convention = schema.List(
    #     title=u"Project Document Naming Convention",
    #     value_type=schema.Choice(values=[
    #         u'PrjName',
    #         u'ContractNumber',
    #         u'DocState',
    #         u'Doctype',
    #         u'DocDate',
    #         u'DocTime',
    #     ]),
    #     required=False,
    #     default=[],
    #     missing_value=[],
    # )
    
    
    # template_password = schema.TextLine(title=u"Password")
    # dashboard = schema.TextLine(title=u"Dashboard")
    # url = schema.TextLine(title=u"URL")
 
    
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
            # 'vokabularies2',
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

    # model.fieldset(
    #     'notifications',
    #     label=_(u'Due Dates'),
    #     description=u"Docent IMS color codes certain due dates to aid users in identifying how close an item is to a due date. We use three colors, and you can choose the number of days from the due date each color represents.",
    #     fields=[
    #         'future_green',
    #         'soon_yellow',
    #         'urgent_red',
    #         ],
    #     )
 


    model.fieldset(
        'companies',
        label=_(u'Companies'),
        description=u"Please create all project companies involved in this project.",
        fields=[
            'companies',
            ],
        )

    
    # urgent_red = schema.Int(
    #     title=_(u"label_red", default=u"Urgent days/value (displayed as Red)"),
    #     description=" ",
    #      required=not_required_in_debug_mode(),
    #     )
    
    # future_green = schema.Int(
    #     title=_(u"label_green", default=u"Future days/value (displayed as Green)"),
    #     description="",
    #      required=not_required_in_debug_mode(),
    #     )

    # soon_yellow = schema.Int(
    #     title=_(u"label_yellow", default=u"Soon days/value (displayed as Yellow)"),
    #     description="",
    #      required=not_required_in_debug_mode(),
    #     )
 


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
 
 
 

@implementer(IProject)
class Project(Item):
    """ Content-type class for IProject
    """


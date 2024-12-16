# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from zope import schema
from plone.supermodel import model
from plone.autoform.directives import widget
from zope.interface import alsoProvides
from collective.z3cform.colorpicker.colorpicker  import ColorpickerFieldWidget

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


class IDocentimsSettings(model.Schema):
    """Adds settings to medialog.controlpanel
    """    
    
    model.fieldset(
        'project',
        label=_(u'Dashboard'),
        fields=[
            'app_buttons', 
            'color1',
            'color2',
            'color3',
            'color4',
            'color5',            
            ],
        )
    
    app_buttons = schema.List(
        title = _(u"Sites",
            default=u"Sites"),
        value_type=schema.URI(
            title= (u'URL'),  
        ),        
    )
    
    # app_user = schema.TextLine(
    #     title = _(u"App Admin User",),        
    # )
    
    # app_password = schema.TextLine(
    #     title = _(u"Password",), 
    #     # defaultFactory=retrieve_password,      
    # )
    
    widget(color1=ColorpickerFieldWidget)
    color1 = schema.TextLine(
        title=u"Color 1",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )
    
    widget(color1=ColorpickerFieldWidget)
    color1 = schema.TextLine(
        title=u"Color 1",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )
    
    widget(color2=ColorpickerFieldWidget)
    color2 = schema.TextLine(
        title=u"Color 2",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )
    
    widget(color3=ColorpickerFieldWidget)
    color3 = schema.TextLine(
        title=u"Color 3",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )
    
    widget(color4=ColorpickerFieldWidget)
    color4 = schema.TextLine(
        title=u"Color 4",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )
    
    widget(color5=ColorpickerFieldWidget)
    color5 = schema.TextLine(
        title=u"Color 5",
        description=u"",
        # max_length=10,
        required=True,
        default="#ff0000"
    )

alsoProvides(IDocentimsSettings, IMedialogControlpanelSettingsProvider)

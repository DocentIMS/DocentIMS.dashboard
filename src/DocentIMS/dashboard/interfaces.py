# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from zope import schema
from plone.supermodel import model
from plone.autoform.directives import widget
from zope.interface import alsoProvides
from collective.z3cform.colorpicker.colorpicker  import ColorpickerFieldWidget

from DocentIMS.dashboard import _


class IDocentimsDashboardLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDocentimsSettings(model.Schema):
    """Adds settings to medialog.controlpanel
    """    
    
    model.fieldset(
        'project',
        label=_(u'Dashboard'),
        fields=[
            'app_buttons', 
            'app_user',
            'app_password',
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
    
    app_user = schema.TextLine(
        title = _(u"App Admin User",),        
    )
    
    app_password = schema.TextLine(
        title = _(u"Password",),        
    )
    
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

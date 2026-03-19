# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from z3c.formwidget.query.widget import OrderedSelectFieldWidget
from plone.autoform import directives as form
from zope.interface import implementer


class IProject(model.Schema):
    """ Marker interface for Project
    """    
    model.load("project.xml")
    form.widget("add_users", OrderedSelectFieldWidget)
    
    
@implementer(IProject)
class Project(Item):
    """
    """
        
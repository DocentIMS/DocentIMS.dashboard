# -*- coding: utf-8 -*-
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.component import adapter
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


@implementer(INameFromTitle)
@adapter(IProject)
class NameFromProjectTitle(object):
    """Generate the object id/name from the required "Project Title" field.

    The standard "Title" field (plone.namefromtitle) is not used on the Add
    Project Connection form; "Project Title" takes its place, so the object's
    name is normalized from "Project Title" instead.
    """

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return getattr(self.context, "project_title", None)

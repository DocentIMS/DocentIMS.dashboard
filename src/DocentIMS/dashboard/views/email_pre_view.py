# -*- coding: utf-8 -*-

# from DocentIMS.dashboard import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IEmailPreView(Interface):
    """ Marker Interface for IEmailPreView"""


@implementer(IEmailPreView)
class EmailPreView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('email_pre_view.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()

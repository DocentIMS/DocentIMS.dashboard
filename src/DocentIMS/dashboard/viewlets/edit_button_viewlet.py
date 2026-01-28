# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase


class EditButtonViewlet(ViewletBase):

    def update(self):
        self.portal_type = self.context.portal_type
        # self.message = self.get_message()

    # def get_message(self):
    #     return u'My message'
    
    def get_url(self):
        return self.context.absolute_url()

    def index(self):
        return super(EditButtonViewlet, self).render()

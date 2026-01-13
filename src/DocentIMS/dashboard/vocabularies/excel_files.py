# -*- coding: utf-8 -*-

# from plone import api
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from DocentIMS.dashboard import _
from plone.dexterity.interfaces import IDexterityContent
from zope.globalrequest import getRequest
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone import api


class VocabItem(object):
    def __init__(self, token, value):
        self.token = token
        self.value = value


@implementer(IVocabularyFactory)
class ExcelFiles(object):
    """
    """
    def __call__(self, context):
        brains = api.content.find(portal_type="File")

        terms = []
        for brain in brains:
            obj = brain.getObject()
            if not obj.file:
                continue

            filename = obj.file.filename.lower()
            
            # TO do, fix this for mime type

            if filename.endswith((".xls", ".xlsx")):
                terms.append(
                    SimpleTerm(
                        value=obj,
                        token=brain.UID,
                        title=brain.Title or filename
                    )
                )

        return SimpleVocabulary(terms)


ExcelFilesFactory = ExcelFiles()

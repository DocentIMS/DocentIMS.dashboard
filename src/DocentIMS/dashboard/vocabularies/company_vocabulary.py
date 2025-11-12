# -*- coding: utf-8 -*-

# from plone import api
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from DocentIMS.dashboard import _
from plone.dexterity.interfaces import IDexterityContent
from zope.globalrequest import getRequest
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from  ..interfaces import IDocentimsSettings
from plone import api



class VocabItem(object):
    def __init__(self, token, value):
        self.token = token
        self.value = value


@implementer(IVocabularyFactory)
class CompanyVocabulary(object):
    """
    """

    def __call__(self, context):
        items  =  api.portal.get_registry_record('DocentIMS.dashboard.interfaces.IDocentimsSettings.companies')
        # Possible feature to get users without added companies
        
        if items:
            unique_items = []
            seen = set()
            for item in items:
                # Convert dict to a tuple of sorted key-value pairs (hashable)
                marker = tuple(sorted(item.items()))
                if marker not in seen:
                    seen.add(marker)
                    unique_items.append(item)
            items = unique_items
            # Assuming items is a list of dictionaries

            # Use sorted() to create a sorted list of items based on 'short_company_name'
            #sorted_items = sorted(items, key=lambda x: x['short_company_name'])
            sorted_items = sorted(
                filter(lambda x: x.get('short_company_name', '') is not None, items),
                key=lambda x: x.get('short_company_name', '').lower() if x.get('short_company_name') else ''
            )

            # Create SimpleTerm objects from the sorted list, excluding empty 'short_company_name'
            terms = [
                SimpleTerm(value=item['short_company_name'], token=item['short_company_name'], title=item['short_company_name'])
                for item in sorted_items if item['short_company_name'] and len(item['short_company_name']) > 1
            ]
            if terms:
                return SimpleVocabulary(terms)
        
        return SimpleVocabulary([])

# directlyProvides(CompanyVocabulary, IVocabularyFactory)


CompanyVocabularyFactory = CompanyVocabulary()

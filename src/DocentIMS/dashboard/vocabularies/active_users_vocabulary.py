# -*- coding: utf-8 -*-

from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone import api
import logging

logger = logging.getLogger(__name__)


@implementer(IVocabularyFactory)
class ActiveUsersVocabulary(object):
    """Vocabulary of users that currently exist in the site.

    Unlike ``plone.app.vocabularies.Users``, which enumerates every principal
    any PAS plugin knows about (so a user that was deleted but left a stale
    member-data/properties record behind keeps showing up), this vocabulary
    only lists users that the auth system can still resolve. Once a user is
    deleted, ``acl_users.getUserById`` no longer finds them and they drop out
    of the "Add Employee(s)" list.
    """

    def __call__(self, context):
        acl_users = api.portal.get().acl_users

        terms = []
        seen = set()
        for user in api.user.get_users():
            userid = user.getId()
            if not userid or userid in seen:
                continue
            # Canonical existence check: a deleted user no longer resolves
            # here, even if a stale properties record lingers.
            if acl_users.getUserById(userid) is None:
                continue
            seen.add(userid)
            fullname = user.getProperty('fullname') or userid
            terms.append(SimpleTerm(value=userid, token=userid, title=fullname))

        terms.sort(key=lambda term: (term.title or '').lower())
        return SimpleVocabulary(terms)


ActiveUsersVocabularyFactory = ActiveUsersVocabulary()

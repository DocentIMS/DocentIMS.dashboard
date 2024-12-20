# # -*- coding: utf-8 -*-
# from plone import api
# from plone.restapi.interfaces import IExpandableElement
# from plone.restapi.services import Service
# from zope.component import adapter
# from zope.interface import Interface, implementer
# import json
# from plone.protect.interfaces import IDisableCSRFProtection
# from zope.interface import alsoProvides


# @implementer(IExpandableElement)
# @adapter(Interface, Interface)
# class AddUser(object):

#     def __init__(self, context, request):
#         self.context = context.aq_explicit
#         self.request = request
    
#     def createuser(self, email, roles, fullname):
#         alsoProvides(self.request, IDisableCSRFProtection)
#         portal = api.portal.get()  # Ensure you have the Plone portal
#         with api.env.adopt_roles(['Manager']):
#             try:
#                 if not api.user.get(username=email):
#                     print('creating user')
#                     api.user.create(
#                         email='email@medialog.no'
#                     )
#                     # api.user.create(
#                     #     email=email,
#                     #     username=email,
#                     #     password="temporary-password",
#                     #     roles=roles,
#                     #     properties={'fullname': fullname}
#                     # )
#                     print(f"User {email} created successfully")
#             except Exception as e:
#                 print(f"Error creating user: {e}")
#                 raise

#     def __call__(self, expand=False):
#         result = {
#             'add_user': {
#                 '@id': '{}/@add_user'.format(self.context.absolute_url()),
#             },
#         }
#         if not expand:
#             return result

#         try:
#             body = self.request.get('BODY', '{}')
#             request_data = json.loads(body) if body else {}
            
#             fullname = request_data.get('fullname')
#             email = request_data.get('email')
#             self.createuser(email=email, roles=('Member',), fullname=fullname)
#             result = {'status': 'success', 'message': 'User created'}
#         except Exception as e:
#             result = {'status': 'error', 'message': str(e)}

#         return result


# class AddUserGet(Service):

#     def reply(self):
#         service_factory = AddUser(self.context, self.request)
#         return service_factory(expand=True)

# from plone.restapi.interfaces import IFieldSerializer
# from plone.app.textfield.interfaces import IRichTextValue
# from zope.component import adapter
# from zope.interface import implementer
# from zope.schema.interfaces import IField
# from zope.schema import getFields

# def html_to_text(html):
#     h =  html2text.HTML2Text()
#     return h.handle(html)


# from plone.restapi.interfaces import IFieldSerializer
# from plone.app.textfield.interfaces import IRichText
# from zope.component import adapter
# from zope.interface import implementer
# from zope.schema.interfaces import IField

# from DocentIMS.dashboard.interfaces import  RichTextFieldRegistry 
 

# @implementer(IFieldSerializer)
# @adapter(RichTextFieldRegistry, IField)
# class RegistryRichTextFieldSerializer:
#     def __init__(self, field, value, request):
#         self.field = field
#         self.value = value
#         self.request = request

#     def __call__(self):
#         import pdb; pdb.set_trace()
#         if not self.value:
#             return None

#         return {
#             "data": self.value.raw,
#             "content-type": self.value.mimeType,
#             "encoding": "utf-8",
#         }

# #  RichTextValue
# # adapter(getFields(IRichTextValue)["message"].__class__, IRichTextValue, None)


# # plone.registry.field.TextLine
# # @implementer(IFieldSerializer)
# # # @adapter(getFields(["message"]))
 
# # @adapter(IRichTextValue, IField)
# # class  RegistryRichTextFieldSerializer:
# #     def __init__(self, field, context, request):
# #         self.field = field
# #         self.context = context
# #         self.request = request

# #     def __call__(self):
# #         value = self.field.get(self.context)

# #         if not value:
# #             return ""

# #         return html_to_text(value.output)
        


# # @implementer(IFieldSerializer)
# # @adapter(IRichTextValue, IField)
# # class RegistryRichTextFieldSerializer:
# #     def __init__(self, field, context, request):
# #         self.field = field
# #         self.context = context
# #         self.request = request

# #     def __call__(self):
# #         value = self.field.get(self.context)

# #         if not value:
# #             return ""

# #         return html_to_text(value.output)
        
 
 
 
# #  RichTextValue
# # @implementer(IFieldSerializer)
# # @adapter(IRichTextValue, IField)
# # class RegistryRichTextFieldSerializer:
# #     def __init__(self, field, context, request):
# #         self.field = field
# #         self.context = context
# #         self.request = request

# #     def __call__(self):
# #         value = self.field.get(self.context)

# #         if not value:
# #             return ""

# #         return html_to_text(value.output)
        
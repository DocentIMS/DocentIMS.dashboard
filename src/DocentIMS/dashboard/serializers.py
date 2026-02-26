from plone.restapi.interfaces import IFieldSerializer
from plone.app.textfield.interfaces import IRichText
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IField


@implementer(IFieldSerializer)
@adapter(IRichText, IField)
class RegistryRichTextFieldSerializer:
    def __init__(self, field, value, request):
        self.field = field
        self.value = value
        self.request = request

    def __call__(self):
        if not self.value:
            return None

        return {
            "data": self.value.raw,
            "content-type": self.value.mimeType,
            "encoding": "utf-8",
        }
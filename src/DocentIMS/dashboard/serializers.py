from plone.restapi.interfaces import IFieldSerializer
from plone.app.textfield.interfaces import IRichText
from zope.component import adapter
from zope.interface import implementer
from plone.registry.interfaces import IRegistryRecord


@implementer(IFieldSerializer)
@adapter(IRichText, IRegistryRecord)
class RegistryRichTextFieldSerializer:
    def __init__(self, field, record, request):
        self.field = field
        self.record = record
        self.request = request

    def __call__(self):
        value = self.record.value
        if not value:
            return None

        return {
            "data": value.raw,
            "content-type": value.mimeType,
            "encoding": "utf-8",
        }
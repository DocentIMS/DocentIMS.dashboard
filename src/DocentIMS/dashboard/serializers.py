from plone.restapi.interfaces import IFieldSerializer
from plone.app.textfield.interfaces import IRichText
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IField


def html_to_text(html):
    h =  html2text.HTML2Text()
    return h.handle(html)


@implementer(IFieldSerializer)
@adapter(IRichText, IField)
class RegistryRichTextFieldSerializer:
    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __call__(self):
        value = self.field.get(self.context)

        if not value:
            return ""

        return html_to_text(value.output)
        
 
 
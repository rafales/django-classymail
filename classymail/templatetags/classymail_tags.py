from django import template
from classymail import utils


register = template.Library()


@register.simple_tag(takes_context=True)
def build_absolute_url(context, object=None, path=None, **kwargs):
    """
    Builds absolute urls in e-mail templates.
    """
    if not (object or path):
        raise TypeError("One of 'object', 'path' arguments is required")

    kw = dict({
        'builder': context.get('builder'),
        'request': context.get('request'),
        'site': context.get('site'),
        'context': context,
        'object': object,
        'path': path,
    }, **kwargs)

    return utils.build_absolute_url(**kw)

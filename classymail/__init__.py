from .base import EmailBuilder
from .mixins import LocalizationMixin, ContextMixin, SiteMixin
from .mixins import HtmlAndTextTemplateMixin


class ClassyMail(LocalizationMixin, HtmlAndTextTemplateMixin, SiteMixin,
        EmailBuilder):
    """
    A class which combines functionality of several mixins:

    * EmailBuilder - base class for constructing e-mail messages
    * ContextMixin - adds get_context_data() method
    * LocalizationMixin - generating e-mails with given timezone and language
    * HtmlAndTextTemplateMixin - rendering e-mails using templates, with plain
      text content and html alternative
    * SiteMixin - adds current site to the template context
    """
    pass

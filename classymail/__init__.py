from .base import EmailBuilder
from .mixins import LocalizationMixin, ContextMixin, SiteMixin
from .mixins import HtmlAndTextTemplateMixin, ContextProcessorMixin


class ClassyMail(LocalizationMixin, HtmlAndTextTemplateMixin, SiteMixin,
        ContextProcessorMixin, EmailBuilder):
    """
    A class which combines functionality of several mixins:

    * EmailBuilder - base class for constructing e-mail messages
    * ContextMixin - adds get_context_data() method
    * LocalizationMixin - generating e-mails with given timezone and language
    * HtmlAndTextTemplateMixin - rendering e-mails using templates, with plain
      text content and html alternative
    * SiteMixin - adds current site to the template context
    * ContextProcessorMixin - adds data collected from context processors to
      the template context
    """
    pass

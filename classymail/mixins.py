"""
classymail.mixins
~~~~~~~~~~~~~~~~~

A set of mixins for EmailBuilder. Some of them are part of ClassyMail class,
rest of them can be mixed when needed.
"""
from django.core import mail
from django.contrib.sites.models import Site
from django.utils import timezone, translation
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured
from .base import EmailBuilder
from .utils import isolate_language, isolate_timezone, get_css_inline_function
from .utils import get_context_processors


class ContextMixin(EmailBuilder):
    """
    A mixin for providing context data for e-mail rendering.
    """
    extra_context = None

    def get_context_data(self):
        """
        Returns a dictionary used as a template context.
        """
        data = {
            'builder': self
        }
        if self.extra_context:
            data.update(self.extra_context)
        return data


class ContextProcessorMixin(ContextMixin):
    """
    A mixin which collects data from context processors and adds it to the
    template context.
    """
    def get_context_data(self):
        data = super(ContextProcessorMixin, self).get_context_data()
        for processor in get_context_processors():
            data.update(processor(builder=self))
        return data


class LocalizationMixin(EmailBuilder):
    """
    A mixin for email builder which will build e-mail message using specified
    language and timezone.

    By default language and timezone are not changed - you have to provide
    `timezone` and/or `language` arguments/attributes or override
    `get_timezone()` or `get_language()` methods.
    """
    timezone = None
    language = None

    def get_timezone(self):
        """
        Returns timezone to be activated while rendering e-mail contents.
        """
        return self.timezone

    def get_language(self):
        """
        Returns language to be activated while rendering e-mail contents.
        """
        return self.language

    def build(self):
        tz, lang = self.get_timezone(), self.get_language()
        with isolate_language(), isolate_timezone():
            if tz:
                timezone.activate(tz)
            if lang:
                translation.activate(lang)

            return super(LocalizationMixin, self).build()


class HtmlAndTextTemplateMixin(ContextMixin):
    html_template_name = None
    text_template_name = None
    mail_class = mail.EmailMultiAlternatives

    def get_html_template_name(self):
        """
        Returns name of html template.
        """
        if self.html_template_name is None:
            raise ImproperlyConfigured(
                "'html_template_name' missing on %s" %
                self.__class__.__name__)

        return self.html_template_name

    def get_text_template_name(self):
        """
        Returns name of text template.
        """
        if self.text_template_name is None:
            raise ImproperlyConfigured(
                "'text_template_name' missing on %s" %
                self.__class__.__name__)
        return self.text_template_name

    def render_html_template(self, context):
        """
        Renders html template.

        Returns string.
        """
        css_inline_fn = get_css_inline_function()
        template_name = self.get_html_template_name()
        body = render_to_string(template_name, context)
        body = css_inline_fn(body)
        return body

    def render_text_template(self, context):
        """
        Renders text template.

        Returns string.
        """
        template_name = self.get_text_template_name()
        return render_to_string(template_name, context)

    def get_message(self):
        # set context on self and attach html alternative
        self.context = self.get_context_data()
        msg = super(HtmlAndTextTemplateMixin, self).get_message()
        html_body = self.render_html_template(self.context)
        msg.attach_alternative(html_body, 'text/html')
        return msg

    def get_body(self):
        return self.render_text_template(self.context)


class SiteMixin(ContextMixin):
    """
    Adds current site to the rendering context.

    You can override site by using `site` argument/attribute.
    """
    site = None

    def get_site(self):
        """
        Returns site to be used.
        """
        if self.site is not None:
            return self.site
        if not Site._meta.installed:
            return None
        return Site.objects.get_current()

    def get_context_data(self):
        data = super(SiteMixin, self).get_context_data()
        data['site'] = self.get_site()
        return data

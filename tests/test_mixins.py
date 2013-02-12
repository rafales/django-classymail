from django.core import mail
import pytz
import pytest
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation, timezone
from classymail import mixins


class TestLocalizationMixin(object):
    def test_get_timezone_method(self):
        mixin = mixins.LocalizationMixin()
        assert mixin.get_timezone() is None
        mixin = mixins.LocalizationMixin(timezone=timezone.utc)
        assert mixin.get_timezone() is timezone.utc

    def test_get_language_method(self):
        mixin = mixins.LocalizationMixin()
        assert mixin.get_language() is None
        mixin = mixins.LocalizationMixin(language='en-gb')
        assert mixin.get_language() == 'en-gb'

    def test_language_change(self, monkeypatch):
        def check_lang():
            assert translation.get_language() == 'pl'

        with translation.override('de'):
            mixin = mixins.LocalizationMixin(language='pl')
            monkeypatch.setattr(mixin, 'get_message', check_lang)
            mixin.build()
            assert translation.get_language() == 'de'

    def test_timezone_change(self, monkeypatch):
        warsaw = pytz.timezone("Europe/Warsaw")
        berlin = pytz.timezone("Europe/Berlin")

        def check_tz():
            assert timezone.get_current_timezone() == warsaw

        with timezone.override(berlin):
            mixin = mixins.LocalizationMixin(timezone=warsaw)
            monkeypatch.setattr(mixin, 'get_message', check_tz)
            mixin.build()
            assert timezone.get_current_timezone() == berlin

    def test_without_change(self, monkeypatch):
        """
        When timezone and language are not provided mixin should use timezone
        and language that are already active
        """
        berlin = pytz.timezone("Europe/Berlin")

        def check():
            assert translation.get_language() == 'de'
            assert timezone.get_current_timezone() == berlin

        with timezone.override(berlin), translation.override('de'):
            mixin = mixins.LocalizationMixin()
            monkeypatch.setattr(mixin, 'get_message', check)
            mixin.build()
            assert timezone.get_current_timezone() == berlin
            assert translation.get_language() == 'de'


class TestContextMixin(object):
    def test_default_context_data(self):
        builder = mixins.ContextMixin()
        ret = builder.get_context_data()
        assert len(ret) == 1
        assert ret['builder'] is builder

    def test_extra_context(self):
        builder = mixins.ContextMixin(extra_context={'name': 'test'})
        ret = builder.get_context_data()
        assert ret == {'builder': builder, 'name': 'test'}


class TestSiteMixin(object):
    def test_get_site(self, monkeypatch):
        site = Site(domain='test', name='test')
        site2 = Site(domain='test2', name='test2')
        monkeypatch.setattr(Site.objects, 'get_current', lambda: site)

        mixin = mixins.SiteMixin(site=site2)
        ret = mixin.get_site()
        assert ret.domain == 'test2' and ret.name == 'test2'

        mixin = mixins.SiteMixin()
        ret = mixin.get_site()
        assert ret.domain == 'test' and ret.name == 'test'

    def test_sites_not_installed(self, monkeypatch):
        monkeypatch.setattr(Site._meta, 'installed', False)

        mixin = mixins.SiteMixin(site=Site(domain='test2', name='test2'))
        ret = mixin.get_site()
        assert ret.domain == 'test2' and ret.name == 'test2'

        mixin = mixins.SiteMixin()
        assert mixin.get_site() is None

    def test_context_data(self):
        """Checks if 'site' has been added to context"""
        mixin = mixins.SiteMixin(site=Site(domain='test', name='test'))
        ret = mixin.get_context_data()
        # make sure data is just updated, not replaced
        assert ret['builder'] is mixin
        # check if 'site' is in context and if it's valid
        assert ret['site'].domain == 'test' and ret['site'].name == 'test'


class TestHtmlAndTextTemplateMixin(object):
    def test_get_html_template_name(self):
        builder = mixins.HtmlAndTextTemplateMixin(
            html_template_name='test_template.html')
        ret = builder.get_html_template_name()
        assert ret == 'test_template.html'

    def test_html_template_not_set(self):
        builder = mixins.HtmlAndTextTemplateMixin()
        with pytest.raises(ImproperlyConfigured):
            builder.get_html_template_name()

    def test_get_text_template_name(self):
        builder = mixins.HtmlAndTextTemplateMixin(
            text_template_name='test_template.txt')
        ret = builder.get_text_template_name()
        assert ret == 'test_template.txt'

    def test_text_template_not_set(self):
        builder = mixins.HtmlAndTextTemplateMixin()
        with pytest.raises(ImproperlyConfigured):
            builder.get_text_template_name()

    def test_html_rendering(self):
        builder = mixins.HtmlAndTextTemplateMixin(
            html_template_name='classymail/email.html')
        ret = builder.render_html_template({})
        assert ret.strip() == '<html><body><b>This is a test</b></body></html>'

    def test_text_rendering(self):
        builder = mixins.HtmlAndTextTemplateMixin(
            text_template_name='classymail/email.txt')
        ret = builder.render_text_template({})
        assert ret.strip() == 'This is a test'

    def test_creating_message(self):
        mixins.HtmlAndTextTemplateMixin.send(
            text_template_name='classymail/email.txt',
            html_template_name='classymail/email.html',
            to=['test@example.com'])

        assert len(mail.outbox) == 1

        # Note: this is email.mime.multipart.MIMEMultipart instance
        msg = mail.outbox[0].message()
        assert msg['To'] == 'test@example.com'
        assert msg.is_multipart()
        parts = msg.get_payload()
        assert len(parts) == 2
        assert parts[0].get_content_type() == 'text/plain'
        assert parts[0].get_payload() == 'This is a test'
        assert parts[1].get_content_type() == 'text/html'
        assert parts[1].get_payload().strip() == '<html><body><b>This is a test</b></body></html>'

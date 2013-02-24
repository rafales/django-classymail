import os
import mock
import pytest
import premailer
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from classymail import utils


class TestUtils(object):
    def test_get_function_by_path(self):
        """Tests if get_function_by_path() imports functions correctly"""
        fn = utils.get_function_by_path('os.path.abspath')
        assert os.path.abspath is fn

    def test_get_css_inline_function(self, settings):
        # None is useful if you want to deactivate inlining
        settings.CLASSYMAIL_CSS_INLINE_FUNCTION = None
        assert utils.get_css_inline_function() is utils._css_inline_noop

        # use premailer's transform by default
        del settings.CLASSYMAIL_CSS_INLINE_FUNCTION
        assert utils.get_css_inline_function() is premailer.transform

    def test_css_inline_noop_function(self):
        expected = object()
        assert utils._css_inline_noop(expected) == expected

    def test_get_context_processors(self, settings):
        from .context_processors import ctx_processor1, ctx_processor2
        if hasattr(settings, 'CLASSYMAIL_CONTEXT_PROCESSORS'):
            del settings.CLASSYMAIL_CONTEXT_PROCESSORS
        assert utils.get_context_processors() == []

        settings.CLASSYMAIL_CONTEXT_PROCESSORS = None
        assert utils.get_context_processors() == []

        settings.CLASSYMAIL_CONTEXT_PROCESSORS = (
            'tests.context_processors.ctx_processor1',
            'tests.context_processors.ctx_processor2',
        )

        processors = utils.get_context_processors()
        assert processors == [ctx_processor1, ctx_processor2]

    @mock.patch('classymail.utils.default_url_function')
    def test_generate_url_with_default_generator(self, m, settings):
        assert isinstance(m, mock.Mock)

        if hasattr(settings, 'CLASSYMAIL_URL_FUNCTION'):
            del settings.CLASSYMAIL_URL_FUNCTION

        m.return_value = '/test/'
        assert utils.build_absolute_url(foo='bar') == '/test/'
        m.assert_called_once_with(
            site=None, object=None, path=None, secure=False, builder=None,
            foo='bar', context=None)

    @mock.patch('tests.custom_url_function')
    def test_generate_url_with_custom_function(self, m, settings):
        assert isinstance(m, mock.Mock)
        settings.CLASSYMAIL_URL_FUNCTION = 'tests.custom_url_function'

        m.return_value = '/test/'
        assert utils.build_absolute_url(foo='bar') == '/test/'
        m.assert_called_once_with(
            site=None, object=None, path=None, secure=False, builder=None,
            foo='bar', context=None)

    @pytest.mark.django_db
    def test_get_domain_defaults(self):
        s = Site(domain='spam', name='spam')
        # use site if not None by default
        assert utils.get_domain(site=s) == 'spam'
        # use current site if site param is None (SIDE_ID setting)
        assert utils.get_domain() == 'example.com'

    def test_get_domain_override(self, settings):
        """
        Always use CLASSYMAIL_DOMAIN if CLASSYMAIL_OVERRIDE_DOMAIN is True.
        """
        s = Site(domain='spam', name='spam')
        settings.CLASSYMAIL_OVERRIDE_DOMAIN = True
        settings.CLASSYMAIL_DOMAIN = 'eggs'
        assert utils.build_absolute_url(path='/bar/') == 'http://eggs/bar/'
        assert utils.build_absolute_url(path='/bar/', site=s) \
               == 'http://eggs/bar/'

    def test_get_domain_no_sites_framework(self, settings, monkeypatch):
        """
        Use CLASSYMAIL_DOMAIN if sites framework is not installed.
        """
        s = Site(domain='spam', name='spam')
        monkeypatch.setattr(Site._meta, 'installed', False)
        settings.CLASSYMAIL_DOMAIN = 'eggs'

        assert utils.get_domain() == 'eggs'
        assert utils.get_domain(site=s) == 'spam'

        settings.CLASSYMAIL_DOMAIN = None
        with pytest.raises(ImproperlyConfigured):
            utils.get_domain()

    def test_get_secure(self, settings):
        """
        Tests get_secure() function.
        """
        assert utils.get_secure(secure=True) is True
        assert utils.get_secure(secure=False) is False

        settings.CLASSYMAIL_ALLOW_SECURE = False
        assert utils.get_secure(secure=True) is False

        settings.CLASSYMAIL_ALWAYS_SECURE = True
        assert utils.get_secure(secure=False) is True

    def test_default_url_function_path_and_object_params(self):
        obj = mock.Mock()
        obj.get_absolute_url.return_value = '/eggs/'
        s = Site(domain='spam', name='spam')
        fn = utils.build_absolute_url
        # path and object
        assert fn(path='/bar/', site=s) == 'http://spam/bar/'
        assert fn(object=obj, site=s) == 'http://spam/eggs/'

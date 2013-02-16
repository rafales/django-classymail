from os.path import abspath
import premailer
from classymail import utils


class TestUtils(object):
    def test_get_function_by_path(self):
        """Tests if get_function_by_path() imports functions correctly"""
        fn = utils.get_function_by_path('os.path.abspath')
        assert abspath is fn

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

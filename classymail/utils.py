from django.conf import settings
from django.utils import timezone, translation
from django.utils.importlib import import_module


class isolate_timezone(object):
    """
    This context manager makes sure that any change to an active timezone
    will be reverted.
    """
    def __enter__(self):
        self.timezone = getattr(timezone._active, 'value', None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timezone is None:
            timezone.deactivate()
        else:
            timezone.activate(self.timezone)


class isolate_language(object):
    """
    This context manager makes sure that any change to an active timezone
    will be reverted.
    """
    def __enter__(self):
        self.language = translation.get_language()

    def __exit__(self, exc_type, exc_val, exc_tb):
        translation.activate(self.language)


def get_function_by_path(fn_path):
    """
    Returns function identified by dotted path.

    Path is something like mypackage.mymodule.myfunction.
    """
    mod_path, fn_name = fn_path.rsplit('.', 1)
    mod = import_module(mod_path)
    return getattr(mod, fn_name)


def _css_inline_noop(arg):
    return arg


def get_css_inline_function():
    """
    Returns function used for css inlining.

    If CLASSYMAIL_CSS_INLINE_FUNCTION is set to None then no-op function is
    returned.
    """
    fn_path = getattr(settings, 'CLASSYMAIL_CSS_INLINE_FUNCTION',
        'premailer.transform')
    if not fn_path:
        return _css_inline_noop
    return get_function_by_path(fn_path)

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
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


def get_context_processors():
    """
    Returns list of classymail context processors.
    """
    return [
        get_function_by_path(path) for path in
        (getattr(settings, 'CLASSYMAIL_CONTEXT_PROCESSORS', None) or ())
    ]


def get_secure(secure):
    """
    Returns "secure" param based on CLASSYMAIL_ALLOW_SECURE and
    CLASSYMAIL_ALWAYS_SECURE settings.
    """
    ALLOW_SECURE = getattr(settings, 'CLASSYMAIL_ALLOW_SECURE', None)
    ALWAYS_SECURE = getattr(settings, 'CLASSYMAIL_ALWAYS_SECURE', None)

    if ALWAYS_SECURE:
        return True

    if ALLOW_SECURE or ALLOW_SECURE is None:
        return secure

    return False


def get_site(site=None):
    """
    Returns site based on site param and SITE_ID setting.

    Returns None if site framework is not installed.
    """
    if site is None and Site._meta.installed:
        site = Site.objects.get_current()
    return site


def get_domain(site=None):
    """
    Returns "domain" param based on CLASSYMAIL_DEFAULT_DOMAIN,
    CLASSYMAIL_OVERRIDE_DOMAIN and current site.
    """
    site = get_site(site)

    domain = getattr(settings, 'CLASSYMAIL_DOMAIN', None)
    if site and not getattr(settings, 'CLASSYMAIL_OVERRIDE_DOMAIN', None):
        domain = site.domain

    if not domain:
        raise ImproperlyConfigured(
            "Sites framework is not installed and CLASSYMAIL_DEFAULT_DOMAIN "
            " or CLASSYMAIL_OVERRIDE_DOMAIN is not set."
        )

    return domain


def get_path(path=None, object=None):
    """
    Returns "path" param based on path and object params.
    """
    if not path and hasattr(object, 'get_absolute_url'):
        path = object.get_absolute_url()
    return path


def default_url_function(site=None, object=None, path=None, secure=False,
                          **kwargs):
    """
    Default url generator.
    """
    domain = get_domain(site)
    protocol = 'https' if get_secure(secure) else 'http'
    path = get_path(path, object)

    return "%s://%s%s" % (protocol, domain, path)


def build_absolute_url(object=None, path=None, site=None,
                 secure=False, context=None, builder=None, **kwargs):
    """
    Generates urls for {% build_absolute_url %} tag using builtin function or function
    set by CLASSYMAIL_URL_FUNCTION setting.
    """
    fn_path = getattr(settings, 'CLASSYMAIL_URL_FUNCTION', None)
    if fn_path:
        fn = get_function_by_path(fn_path)
    else:
        fn = default_url_function

    return fn(builder=builder, object=object, path=path, site=site,
              secure=secure, context=context, **kwargs)

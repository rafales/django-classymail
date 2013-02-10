# Debug options
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Localization
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-US'
SITE_ID = 1
USE_L10N = True
USE_TZ = True


MIDDLEWARE_CLASSES = ()
TEMPLATE_CONTEXT_PROCESSORS = ()

STATICFILES_FINDERS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',

    'tests',
)

SECRET_KEY = 'local'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
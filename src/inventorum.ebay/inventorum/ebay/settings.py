# -*- coding: utf-8 -*-

"""Base settings shared by all environments"""
import os
import logging
from datetime import datetime

here = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(here, '..', '..', 'VERSION')).read().strip()

# ==============================================================================
# Generic Django project settings
# ==============================================================================

SITE_ID = 1
TIME_ZONE = 'Europe/Berlin'
USE_TZ = True
USE_I18N = True
USE_L10N = True
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
USE_THOUSAND_SEPARATOR = True

FORMAT_MODULE_PATH = 'inventorum.ebay.conf.locale'

# Needed to suppress 1_6.W001 warning
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# if True use nginx to serve protected files
# Else user django default django.views.static.serve (which would not be for production)
USE_NGINX_X_ACCEL_REDIRECT = True

# alphabetically ordered
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',

    'inventorum.ebay.apps.accounts',
    'inventorum.ebay.apps.auth',
    'inventorum.ebay.apps.categories',
    'inventorum.ebay.apps.products',

    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework_swagger',
    'mptt'
)

AUTH_USER_MODEL = 'inventorum.ebay.apps.accounts.models.EbayAccountModel'

ADMINS = (
    ('Development', 'tech@inventorum.com'),
)

# TODO jm: Correct?
ALLOWED_HOSTS = [
    'localhost:5777',
    'localhost',
    '127.0.0.1:9000',
    '127.0.0.1:5777',
    '127.0.0.1',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')


# ==============================================================================
# Third party configurations
# ==============================================================================

# REST framework ===============================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'inventorum.ebay.lib.auth.backends.TrustedHeaderAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # TODO jm: check compatibility with new rest framework version
    # 'DEFAULT_THROTTLE_RATES': {
    # 'default': '20/sec', # Default one for everything
    # },
    'EXCEPTION_HANDLER': 'inventorum.ebay.lib.rest.exceptions.custom_exception_handler'
}

# RabbitMQ/Celery settings ==============================================================

RABBITMQ_VHOST = 'inventorum_ebay'
RABBITMQ_USER = 'ebay'
RABBITMQ_PASSWORD = 'ebay'

BROKER_URL = "amqp://ebay:ebay@localhost:5672/inventorum_ebay"


# Others =======================================================================

logging.getLogger('factory').setLevel(logging.WARN)
logging.getLogger("requests").setLevel(logging.WARN)
logging.getLogger("ebaysdk").setLevel(logging.WARN)
logging.getLogger("vcr").setLevel(logging.WARN)


# ==============================================================================
# Calculation of directories relative to the project module location
# ==============================================================================

PROJECT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
BUILDOUT_ROOT = os.path.join(PROJECT_DIR, '..', '..', '..')
CASSETTES_DIR = os.path.join(PROJECT_DIR, 'fixtures', 'cassettes')
ENCRYPTED_FIELD_KEYS_DIR = os.path.join(PROJECT_DIR, 'fieldkeys')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR,  'ebay', 'templates'),
)

# ==============================================================================
# Project URLS and media settings
# ==============================================================================

ROOT_URLCONF = 'inventorum.ebay.urls'

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

# ==============================================================================
# Middleware
# ==============================================================================

MIDDLEWARE_CLASSES = (
    # BH: This adds `X-Sentry-ID` header, so error can be tracked down
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'inventorum.ebay.lib.rest.middleware.ExceptionLoggingMiddleware',
    'inventorum.util.django.middlewares.CrequestMiddleware',
    # TODO jm: Needed?
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # TODO jm: Move to utils?!
    # 'inventorum.api.lib.middleware.LocaleMiddleware',
    # 'inventorum.api.lib.middleware.TimezoneMiddleware',
    # 'inventorum.api.lib.middleware.ErrorFormatterMiddleware',   # This must be above the ErrorLoggingMiddleware
    # 'inventorum.api.lib.middleware.ErrorLoggingMiddleware',
    # 'inventorum.api.lib.middleware.CustomHeaderMiddleware',
    # TODO jm: Decouple event-header middleware from api, only use zmq?!
    # 'inventorum.util.django.signals.EventHeaderMiddleware',
)

# Language codes must be LOWERCASE always
_ = lambda s: s
LANGUAGE_CODE = 'en'
LANGUAGES = (('de', _('German'),),
             ('en', _('English'),),)

LOCALE_PATHS = (os.path.join(PROJECT_DIR, 'ebay', 'conf', 'locale'), )

AVAILABLE_LANGUAGES = [l[0] for l in LANGUAGES]

# ==============================================================================
# Auth / security
# ==============================================================================

AUTHENTICATION_BACKENDS = (
)


# ==============================================================================
# Ebay
# ==============================================================================

# Ebay settings (LIVE KEYS!)
EBAY_DOMAIN = "api.ebay.com"
EBAY_SIGNIN = "https://signin.ebay.de/"
EBAY_DEVID = "dbedb016-ee04-4fce-a8e3-22c134fbb3c7"
EBAY_APPID = "Inventor-9021-41d8-9c25-9bae93f76429"
EBAY_CERTID = "6be1b82a-0372-4e15-822d-e93797d623ac"


# https://developer.ebay.com/DevZone/xml/docs/Reference/ebay/types/SiteCodeType.html
EBAY_SUPPORTED_SITES = {
    "DE": 77,  # Currency EUR
    "AT": 16  # Currency EUR
}

EBAY_ERROR_LANGUAGE_BY_SITE_ID = {
    77: "de_DE",
    16: "de_AT"
}

# Changed main token to andis one, we need to swap it to inventorums one later!
EBAY_LIVE_TOKEN = 'AgAAAA**AQAAAA**aAAAAA**6g3+Ug**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJk4OmC5KKpAydj6x9nY+seQ**qeUBAA**AAMAAA**K8w7vV+LcRadcdBD8ziMmdCRr/1k8OpEdzlvuNEWspZNp5ydVJw3ZkHG2x3Vp9Qwj3g0hP4rJA9/ENIJfl+Zfee+V62fIbHjbhRSUD7L8/TZqdS8Y1NlNLcfYGJfMJJLBXpYxnhv93C3W/1v8FsiqFBsjl6Zgo9eRyGlzDNPlGKUJQp4m1CLv21GHBf8QN1kz9gVa5uFVknBpZtjZ15bDiCy1vHZ5erjw8vTxFhrqsDYWSabxwCvDd8cRoBvDJxGZYol4I1Su6XtDhjuS5ptf1RvYeKo496IMoAj3aHFNRNWG9mtEC1T8gawBjmhNB54dxbRG1s41lcMhdi+mXHhZj8OxtxG9k0O1xxmJHNXVMeh67uNx/okxspUPMIXjtYR8i55sONunSrAIobxdr+UbNEnrzvUT/fMsqWm3CD4Lcr1rn94KTr4yoTn0wCMEZx5yqR7NiO+XL0QjrKskhJGo/EVK06izKIVOza818A1bRBF/kf4tUrOFqxTBzO3h4F9jMezz37IQFmrMQ4yZ2JQNYtkv+5t7CQhpxHBUzQ/kM/lG521TlLwsSvBfxBPVvX55YRSjtDdPLVP91iICCLYldyJ/ugb64+bHynhCTRbNsD7BDbEVCjBumlHPi02nSNuSQRnwTxSJS8/XG89vpE/rCBIKsEEXjVploEx4OF4GtYX+d0eUhqn7+sHR0U0CwOZko7UpbziHh7kwTLZnrSush6HJ6GEDpZJJUwoidskZE7PzjjdGk0KZrPXPNq56hb+'

EBAY_LIVE_TOKEN_EXPIRATION_DATE = datetime(2016, 9, 21, 13, 18, 38)

EBAY_LISTING_URL = "http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={listing_id}"

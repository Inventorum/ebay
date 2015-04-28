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
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',

    'inventorum.ebay.apps.accounts',
    'inventorum.ebay.apps.auth',
    'inventorum.ebay.apps.categories',
    'inventorum.ebay.apps.notifications',
    'inventorum.ebay.apps.orders',
    'inventorum.ebay.apps.products',
    'inventorum.ebay.apps.shipping',

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
    'DEFAULT_THROTTLE_RATES': {
        'default': '20/sec',
    },
    'DEFAULT_PAGINATION_CLASS': 'inventorum.ebay.lib.rest.APIPagination',
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
EBAY_LIVE_TOKEN = 'AgAAAA**AQAAAA**aAAAAA**VPo4VQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AFkYKnDpiFoQ6dj6x9nY+seQ**qeUBAA**AAMAAA**hm7IZ6+9b1WTNSGOMQEdijzrGPgniZfog17a2QN3WsUAcoZk67KsJGj55R+Q9vyfPQjVOgcfH7CcK587xCEu9EzWIKFgBfBvZ5q0Ykk9UUOLxiHfaZJcdWNnQ3RG1EkXgYPt95COGQjZx0rSLACHhhI5c2kc5QuI+8AsG4pPH/px7HQmjM8RDFD9/6wmor5PgKYMWlF3iCTDUEVS1m36+AOthGjyTvUApZ9JoXkwhHXeStvKyNwsbaU+VjSlzp/L+Rxk0H16MwFhFc6jx8yPDcccbVbKejcB30lxHQFyHOm5d3BVTxEnw2un1GXr0uE7qd9fynAdGnsNUk/zf8D/U/RNFHHDOEvaz/XuCy6HS7asJL0duLdG+RtjMuWy0lHmaY84yd47aTLL0t1q374O2ypvUDyvyuCEEKbV+PTHG83VJDQbivlPitI2o9wNg81xIiGW+qpGbwffWHU2B42MmreA3XcOL/cqQtHBK+gz1j3a9MuXl36LiXETYFC7F/t6OXHnIJFzbiKYU4ozWERb+2wDhVadw1JcKxJako9J74caQUmMJ1Shg/FvbO7QtnxbjzR63rp7661O64I6GFe6EgvFQVLGXcbEmsoPAE0mE4QkVEBKrvgfPCDjCZZcvpIy5yzibT6KNZMvBizlC5vx5+xPSvXRMjc5bWsT1kVZb7hiao9/uC4e7UZDanykuyUfYHsuj2aHWdtgqcb92WCaJQ28zlwudRlsmTsrSngI0yP7IG4ZwhXsKVRFTzZ9pWEh'

EBAY_LIVE_TOKEN_EXPIRATION_DATE = datetime(2016, 10, 14, 13, 57, 40)

EBAY_LISTING_URL = "http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={listing_id}"

# -*- coding: utf-8 -*-

"""Base settings shared by all environments"""
from __future__ import absolute_import

import os
import logging
import sys
from datetime import datetime, timedelta
from celery.schedules import crontab
from inventorum.ebay.lib.celery import get_anonymous_task_execution_context

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

# if True use nginx to serve protected files
# Else user django default django.views.static.serve (which would not be for production)
USE_NGINX_X_ACCEL_REDIRECT = True

# alphabetically ordered
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',

    'inventorum.ebay.apps.accounts',
    'inventorum.ebay.apps.auth',
    'inventorum.ebay.apps.categories',
    'inventorum.ebay.apps.notifications',
    'inventorum.ebay.apps.orders',
    'inventorum.ebay.apps.returns',
    'inventorum.ebay.apps.products',
    'inventorum.ebay.apps.shipping',
    'inventorum.ebay.lib.core_api',

    'mptt',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework_swagger'
)

AUTH_USER_MODEL = 'accounts.EbayAccountModel'

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

FIXTURE_DIR = os.path.join(here, "..", 'fixtures')

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

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'periodic_ebay_orders_sync_task': {
        'task': 'inventorum.ebay.apps.orders.tasks.periodic_ebay_orders_sync_task',
        'schedule': timedelta(minutes=10),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_core_orders_sync_task': {
        'task': 'inventorum.ebay.apps.orders.tasks.periodic_core_orders_sync_task',
        'schedule': timedelta(seconds=30),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_core_returns_sync_task': {
        'task': 'inventorum.ebay.apps.returns.tasks.periodic_core_returns_sync_task',
        'schedule': timedelta(minutes=1),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_core_products_sync_task': {
        'task': 'inventorum.ebay.apps.products.tasks.periodic_core_products_sync_task',
        'schedule': timedelta(seconds=30),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_ebay_categories_sync_task': {
        'task': 'inventorum.ebay.apps.categories.tasks.initialize_periodic_ebay_categories_sync_task',
        'schedule': crontab(hour=3, minute=0),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_ebay_shipping_sync_task': {
        'task': 'inventorum.ebay.apps.shipping.tasks.periodic_ebay_shipping_sync_task',
        'schedule': crontab(hour=3, minute=10),
        'kwargs': {
            "context": get_anonymous_task_execution_context()
        }
    },
    'periodic_ebay_timeouted_item_check_task': {
        'task': 'inventorum.ebay.apps.products.tasks.periodic_ebay_timeouted_item_check_task',
        'schedule': timedelta(seconds=300),
        'kwargs': {
            'timeout': 300,
            'context': get_anonymous_task_execution_context()
        }
    },
    'periodic_synchronise_ebay_item_to_api': {
        'task': 'inventorum.ebay.apps.products.tasks.periodic_synchronise_ebay_item_to_api',
        'schedule': timedelta(seconds=300),
        'kwargs': {
            'timeout': 300,
            'context': get_anonymous_task_execution_context()
        }
    },
}

# will be used by util.celery.InventorumTask to handle async celery exceptions
CELERY_MIDDLEWARE = 'inventorum.ebay.celery.CeleryMiddleware'

# https://github.com/celery/celery/issues/2437
CELERYD_HIJACK_ROOT_LOGGER = False

# Celery queues
CELERY_ROUTES = {
    # Fetching
    'inventorum.ebay.apps.categories.tasks.initialize_periodic_ebay_categories_sync_task': {'queue': 'fetching'},
    'inventorum.ebay.apps.categories.tasks.ebay_category_specifics_sync_task': {'queue': 'fetching'},
    'inventorum.ebay.apps.categories.tasks.ebay_category_features_sync_task': {'queue': 'fetching'},
    'inventorum.ebay.apps.categories.tasks.ebay_categories_sync_task': {'queue': 'fetching'},
    'inventorum.ebay.apps.categories.tasks.ebay_category_specifics_batch_task': {'queue': 'fetching'},

    # Syncing
    'inventorum.ebay.apps.orders.tasks.periodic_ebay_orders_sync_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.orders.tasks.ebay_orders_sync': {'queue': 'syncing'},
    'inventorum.ebay.apps.orders.tasks.periodic_core_orders_sync_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.orders.tasks.core_order_creation_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.returns.tasks.periodic_core_returns_sync_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.orders.tasks.click_and_collect_status_update_with_event_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.orders.tasks.ebay_order_status_update_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.products.tasks.periodic_core_products_sync_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.products.tasks.periodic_ebay_timeouted_item_check_task': {'queue': 'syncing'},
    'inventorum.ebay.apps.products.tasks.periodic_synchronise_ebay_item_to_api': {'queue': 'syncing'},

    # Publishing
    'inventorum.ebay.apps.products.tasks._initialize_ebay_item_publish': {'queue': 'publishing'},
    'inventorum.ebay.apps.products.tasks._ebay_item_publish': {'queue': 'publishing'},
    'inventorum.ebay.apps.products.tasks.synchronise_ebay_item_to_api': {'queue': 'publishing'},
    'inventorum.ebay.apps.products.tasks._initialize_ebay_item_unpublish': {'queue': 'publishing'},
    'inventorum.ebay.apps.products.tasks._ebay_item_unpublish': {'queue': 'publishing'},
    'inventorum.ebay.apps.products.tasks._finalize_ebay_item_unpublish': {'queue': 'publishing'},

    # Updating
    'inventorum.ebay.apps.products.tasks.ebay_item_update': {'queue': 'updating'},
    'inventorum.ebay.apps.products.tasks.ebay_product_deletion': {'queue': 'updating'},
    'inventorum.ebay.apps.products.tasks.core_api_publishing_status_update_task': {'queue': 'updating'},
}



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
    'django.middleware.locale.LocaleMiddleware',
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
EBAY_HTTPS = True

# https://developer.ebay.com/DevZone/xml/docs/Reference/ebay/types/SiteCodeType.html
EBAY_SUPPORTED_SITES = {
    "DE": 77,  # Currency EUR
    "AT": 16  # Currency EUR
}

EBAY_ERROR_LANGUAGE_BY_SITE_ID = {
    77: "de_DE",
    16: "de_AT"
}

CORE_ORDER_NOTE_TEMPLATE = "Ebay order id: {ebay_order_id}"

# newmade
EBAY_LIVE_TOKEN = 'AgAAAA**AQAAAA**aAAAAA**rp4aVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHlYunD5KLqA+dj6x9nY+seQ**qeUBAA**AAMAAA**O2lrsU8I6yjrricneQO018oJ2GChsYf5PaV62oYlcDgguiGB/IPq89cLIHfiHXjsz5ONAxNsjSzR+elJQkx6NlF+LTw0p3DdPItRFahsbY3O5+iVksmJr++E1+QF7PvkudovYAb183wTZpnZ8np7bsOPAWvFeuRZHbVmwvROSGDQOsAzbWFyVF/6l9xJpHAKULDMzR/nnaCnE24tiTn0V2KH+iBAMZzVbuoXM1kEtIll+N6S0JEvvhtTUW8qlmM0blGaXC7uVfd8CeLDudxEi7T2CSLzsqszuzf+fzBsbSHmAWLWwndHmgnhqyrOXoDrrL9bd2w8jAgO5Lg58/2LoEPbo7TzFXlqv6RPjr0A/gp2/rpbbTl5XTsApPyUN+YiYHuZe0MzxJxgDD6BsGKFK4FmeL+GoC8J9qox5Rk8ynGFOdpjTT29c9gA0NRW0x3iA9zzB5O81Z20+euQJ1L58iVFOcDSHbN2pae0kgafUVJsq96yBz7EB56q9jt1KegCbGXVUrkfCzDUrEmZuJCm3qw6edh6Xir6x+esSnG65toiF/TuiyyC76UYVXctEFxmJFpHbEOou8fzfEHq4FR8LFM5xEmqsx4tUKUFRoxO6pCWHEjPEeOu5Hgl8/JxWDSp/JmTgGwofeIHrgHLJsnA6bhoo6heiAo2O8bGw/sReKccSGNV8JlFZJXCL7leA3APeVt3yi4itCaSCq0JsDpILTCAdC6vnUEQHcVvowhzN7ck1qmY0gUcOo6IOMuJlxn/'
EBAY_LIVE_TOKEN_EXPIRATION_DATE = datetime(2016, 10, 14, 13, 57, 40)

EBAY_LISTING_URL = "http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={listing_id}"

# http://stackoverflow.com/questions/6957016/detect-django-testing-mode
TEST = 'test' in sys.argv

if TEST:
    # http://stackoverflow.com/questions/25161425/disable-migrations-when-running-unit-tests-in-django-1-7
    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"

    MIGRATION_MODULES = DisableMigrations()

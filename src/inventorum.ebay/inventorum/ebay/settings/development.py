from .base import *

VAR_ROOT = "{here}/../../../var".format(here=here)
admin_email = "tech@inventorum.com"
STATIC_URL = "/static/"

DEBUG = True
TEMPLATE_DEBUG = True

# https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-bcrypt-with-django
PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.BCryptSHA256PasswordHasher"
    ]

JOHNNY_MIDDLEWARE_KEY_PREFIX = "local"
TEMPLATE_STRING_IF_INVALID = "INVALID %s"

STATIC_ROOT = "{VAR_ROOT}/inventorum/ebay/static".format(VAR_ROOT=VAR_ROOT)

# TODO jm: This should be changed, right?! :-)
SECRET_KEY = "kregvegWoon2osyitwap}ebogyebJadWawmisyokidWoytkehaxbyicNomyefEwdEdCymwatHomUgucfikWiabziBicAjtijuctinyefmytdaicyegCyxHogEcthilsh"

DEFAULT_FROM_EMAIL = "%s" % admin_email
INVOICES_FROM_EMAIL = "%s" % admin_email

# reconnect after 10 minutes
DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "inventorum_ebay_develop",
            "HOST": "db",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "OPTIONS": {
                "sslmode": "disable",
                "client_encoding": "utf8"
            },
            "CONN_MAX_AGE": 0
        }
    }


SQL_META_EXTRA = False

EMAIL_HOST = "inventorum.com"
EMAIL_PORT = 25
SERVER_EMAIL = "ebay@slingshot.inventorum.net"

ALLOWED_HOSTS = ["*"]


INV_CORE_API_HOST = "app.intern.inventorum.net"
INV_CORE_MEDIA_HOST = "app.inventorum.net"
INV_CORE_API_SECURE = False

EBAY_RUNAME = "Inventorum_GmbH-Inventor-9021-4-ptdrwjhq"
EBAY_SKU_FORMAT = "invdev_{0}"
EBAY_LOCATION_ID_FORMAT = "invdev_{0}"

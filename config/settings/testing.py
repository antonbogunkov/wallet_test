from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("MYSQL_DATABASE", default="wallet"),
        "USER": "root",
        "PASSWORD": env.str("MYSQL_ROOT_PASSWORD", default="walletroot"),
        "HOST": env.str("MYSQL_HOST", default="db"),
        "PORT": env.str("MYSQL_PORT", default="3306"),
    }
}

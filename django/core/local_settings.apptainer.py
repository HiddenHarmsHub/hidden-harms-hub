"""
Settings that are specific to this particular instance of the project.
This can contain sensitive information (such as keys) and should not be shared with others.

REMEMBER: If modifying the content of this file, reflect the changes in local_settings.example.py
"""

import os
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

LOCAL_PATH = env.str("DJANGO_LOCAL_PATH", "/local/")
LOG_DIR = env.str("DJANGO_LOG_DIR", os.path.join(LOCAL_PATH, "logs"))


# Create a SECRET_KEY.
# Online tools can help generate this for you, e.g. https://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = env.str("DJANGO_SECRET_KEY")  # throw an error if this is not set, as it is required for security reasons

# Set to True if in development, or False is in production
DEBUG = env.bool("DJANGO_DEBUG", default=True)

# Set to ['*'] if in development, or specific IP addresses and domains if in production
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=['*'])

# Provide the email address for the site admin (e.g. the researcher/research team)
ADMIN_EMAIL = env.str("DJANGO_ADMIN_EMAIL", "")

MSE_CALCULATOR_URL = 'url.for.julia.service'

# Set the database name below
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(LOCAL_PATH, 'hidden-harms-hub-dev.sqlite3'),
        'TEST': {
            'NAME': os.path.join(LOCAL_PATH, 'hidden-harms-hub-dev_TEST.sqlite3'),
        },
    }
}

STATICFILES_DIRS = [os.path.join(BASE_DIR, "core/static")]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(LOCAL_PATH, "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = env.str("DJANGO_MEDIA_PATH")  # force a value for this

# over-write the entire settings.py
SET_LOGGING = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'stream': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG' if DEBUG else 'INFO',  # NOQA
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['stream', 'mail_admins'],
            'level': 'DEBUG' if DEBUG else 'INFO',  # NOQA
            'propagate': 'True',
        },
    },
}

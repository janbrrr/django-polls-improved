import datetime

from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')  # Keep the secret key used in production secret!

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE'),
        'NAME': os.environ.get('SQL_DATABASE'),
        'USER': os.environ.get('SQL_USER'),
        'PASSWORD': os.environ.get('SQL_PASSWORD'),
        'HOST': os.environ.get('SQL_HOST'),
        'PORT': os.environ.get('SQL_PORT'),
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',  # Note the host name (taken from docker-compose)
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Add django.middleware.security.SecurityMiddleware
# to your MIDDLEWARE_CLASSES setting (it is by default)

# Use HTTP Strict Transport Security (HSTS)
# which always forces a HTTPS connection
# Requires that everything on the site is served
# over HTTPS
# Do NOT use this on the development server

SECURE_HSTS_SECONDS = 31536000  # 31536000 = 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Disable content sniffing by the browser
# where it tries to guess the content type
# rather than follow the Content-Type header

SECURE_CONTENT_TYPE_NOSNIFF = True

# Make CSRF token and session cookie
# only get sent over secure connections:

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

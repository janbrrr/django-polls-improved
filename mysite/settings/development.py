from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Use simple hasher to increase speed
)

AUTH_PASSWORD_VALIDATORS = []  # Allow insecure passwords during development

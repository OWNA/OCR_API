from .base import *
import os

SECRET_KEY = os.environ['OCR_SERVER_SECRET_KEY']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ownaocrdev',
        'USER': 'owna',
        'PASSWORD': os.environ['OCR_SERVER_DATABASE_PASSWORD'],
        'HOST': 'ocrdev.ccq1iaivakzu.us-west-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}

MIDDLEWARE = [
    'ddtrace.contrib.django.TraceMiddleware',
] + MIDDLEWARE

DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'ocr-server',
    'TAGS': {'env': 'staging'},
}

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']


FRONTEND_URL = "http://localhost:4200"

BACKEND_URL = "http://localhost:8000"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]


CORS_ALLOW_CREDENTIALS = True

WSGI_APPLICATION = 'DjangoBlogChat.wsgi.application'

ROOT_URLCONF = 'DjangoBlogChat.urls'

STATIC_URL = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='plextaskmanager@gmail.com'
EMAIL_HOST_PASSWORD='oklqtynssjxzztuj'

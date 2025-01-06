from dotenv import load_dotenv
import os

load_dotenv()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


FRONTEND_URL = "http://localhost:4200"

BACKEND_URL = "http://localhost:8000"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]


CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
]

WSGI_APPLICATION = 'DjangoBlogChat.wsgi.application'

ROOT_URLCONF = 'DjangoBlogChat.urls'

STATIC_URL = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')

MEDIA_URL = '/media/'

EMAIL_BACKEND=os.getenv('BACKEND')
EMAIL_HOST=os.getenv('HOST')
EMAIL_PORT=os.getenv('PORT')
EMAIL_USE_TLS=os.getenv('USE_TLS')
EMAIL_HOST_USER=os.getenv('HOST_USER')
EMAIL_HOST_PASSWORD=os.getenv('HOST_PASSWORD')

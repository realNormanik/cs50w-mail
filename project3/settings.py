"""
Django settings for project3 project.

Wersja produkcyjna przystosowana do wdrożenia na Vercel z bazą Neon PostgreSQL.
"""

import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv('.env.local')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOB_READ_WRITE_TOKEN = os.environ.get('BLOB_READ_WRITE_TOKEN')
BLOB_STORE_ID = os.environ.get('BLOB_STORE_ID')  # np. "abc123xyz" ze store'a

DEFAULT_FILE_STORAGE = 'mail.storage.VercelBlobStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# UWAGA: system plików na Vercel jest tylko-do-odczytu (poza /tmp) i efemeryczny.
# Jeśli aplikacja przyjmuje uploady od użytkowników, MEDIA_ROOT NIE nadaje się
# do przechowywania plików w produkcji — użyj np. S3 / Cloudflare R2 / Vercel Blob.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    '05$4$3aew(8ywondz$g!k4m779pbvn9)euj0zp7-ae*x@4pxr+',  # fallback tylko na dev
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Lista dozwolonych hostów pobierana z ENV, np. "twojadomena.com,www.twojadomena.com"
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()
]

# Vercel automatycznie wstrzykuje VERCEL_URL (bez protokołu) dla każdego deploya
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# W deweloperce zostaw dostęp lokalny
if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
]
if VERCEL_URL:
    CSRF_TRUSTED_ORIGINS.append(f'https://{VERCEL_URL}')

# Dodaj własną domenę produkcyjną, jeśli ją podłączysz w Vercel
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Application definition

INSTALLED_APPS = [
    'mail',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serwuje pliki statyczne bez dysku trwałego
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'project3.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project3.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# Neon wymaga połączenia SSL — stąd ssl_require=True.
# conn_max_age=0 jest celowo zachowane: środowisko serverless na Vercel odpala
# nową instancję funkcji przy (prawie) każdym żądaniu, więc trzymanie długo
# żyjących połączeń nic nie daje i tylko szybciej wyczerpie limit połączeń Neona.

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=0,
        ssl_require=True,
    )
}

AUTH_USER_MODEL = 'mail.User'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mail', 'static', 'mail')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise: kompresja + cache-busting dla plików statycznych.
# Jeśli Twoja wersja Django jest starsza niż 4.2, zamień powyższy STORAGES
# na:  STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STORAGES = {
    "default": {
        "BACKEND": "mail.storage.VercelBlobStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Authentication user with Social media

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')


# Ustawienia bezpieczeństwa aktywne tylko w produkcji (DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 7 dni, można zwiększyć po testach
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

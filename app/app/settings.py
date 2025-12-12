"""
Django settings for app project.
"""

from pathlib import Path
import os
import pymysql

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-pf7lx3f(rk7&qqs33&(#sfgg2-_d=g9f9g=bfw2e5gr59vhnrt'
DEBUG = True

ALLOWED_HOSTS = ['altos-de-fontibon.onrender.com', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    "https://altos-de-fontibon.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ---------------------------------------
# 🧩 APLICACIONES
# ---------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'usuario',
    'administrador',
    'residente',
    'vigilante',
    'crispy_forms',
    'channels',
]

# ---------------------------------------
# ⚙️ MIDDLEWARE
# ---------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # OK
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middlewares.NoCacheMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# ------------------------
# Channels (WebSockets)
# ------------------------
ASGI_APPLICATION = "app.asgi.application"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# ---------------------------------------
# 🗄️ BASE DE DATOS
# ---------------------------------------
pymysql.install_as_MySQLdb()

default_db = 'mysql'  # 'mysql' o 'postgres'

if default_db == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'proyecto_bd',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        }
    }
elif default_db == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {'sslmode': 'require'}
        }
    }

# ---------------------------------------
# 🔐 VALIDACIÓN DE CONTRASEÑAS
# ---------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------
# 🌎 INTERNACIONALIZACIÓN
# ---------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ---------------------------------------
# 🎨 ESTÁTICOS Y MEDIA
# ---------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------
# 📧 CORREO PRODUCCIÓN (SendGrid)
# ---------------------------------------
#EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

#SENDGRID_API_KEY = os.getenv("EMAIL_HOST_PASSWORD")
#DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "altosdefontibon.cr@gmail.com")

#SENDGRID_SANDBOX_MODE_IN_DEBUG = False
#SENDGRID_ECHO_TO_STDOUT = True

# ---------------------------------------
# 📧 CORREO DESARROLLO (Gmail) — Comentado
# ---------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'altosdefontibon.cr@gmail.com'
EMAIL_HOST_PASSWORD = 'heho zywq sayt pexm'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------------------------------
# EXTRA
# ---------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Se respeta tu forma, pero solo se define una vez
CSRF_TRUSTED_ORIGINS = [
    "https://altos-de-fontibon.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

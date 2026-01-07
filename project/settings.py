import os
from pathlib import Path
import dj_database_url
import stripe

# ===================================
# Base directory
# ===================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===================================
# Security
# ===================================
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-secret-key')  # في PythonAnywhere استخدم env var
DEBUG = False
ALLOWED_HOSTS = ["*"]  # مؤقتًا

# ===================================
# Auth
# ===================================
LOGIN_REDIRECT_URL = '/products/my-orders/' 
LOGOUT_REDIRECT_URL = '/login/' 
AUTH_USER_MODEL = 'accounts.User'

# ===================================
# Installed Apps
# ===================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps
    'products',
    'accounts',
    'app',
    
    # Third-party
    'rest_framework',
    'widget_tweaks',
    'embed_video',
]

# ===================================
# Middleware
# ===================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

# ===================================
# Templates
# ===================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.cart_counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# ===================================
# Database
# ===================================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False
    )
}

# ===================================
# Stripe
# ===================================
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_1234567890abcdef')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_1234567890abcdef')
stripe.api_key = STRIPE_SECRET_KEY

# ===================================
# Password validation
# ===================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ===================================
# Internationalization
# ===================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ===================================
# Static files
# ===================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===================================
# Media files
# ===================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===================================
# Paymob (Environment Variables)
# ===================================
PAYMOB_API_KEY = os.getenv('PAYMOB_API_KEY', '')
IFRAME_ID = os.getenv('IFRAME_ID', '')
INTEGRATION_ID = os.getenv('INTEGRATION_ID', '')

# ===================================
# Email
# ===================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

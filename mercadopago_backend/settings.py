import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mercadopago_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'mercadopago_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS settings
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    # Em produção, seja mais restritivo
    CORS_ALLOWED_ORIGINS = [
        "https://seudominio.com",
        "https://www.seudominio.com",
    ]
    CORS_ALLOW_ALL_ORIGINS = False

# ===============================
# CONFIGURAÇÕES PAGBANK/PAGSEGURO (COMPATIBILIDADE TOTAL)
# ===============================

# Função auxiliar para pegar configurações com fallback
def get_payment_config(pagbank_key, pagseguro_key, default_value=None):
    """Pega configuração do PagBank primeiro, depois PagSeguro, depois default"""
    return config(pagbank_key, default=config(pagseguro_key, default=default_value))

# Credenciais principais
PAGBANK_EMAIL = get_payment_config('PAGBANK_EMAIL', 'PAGSEGURO_EMAIL')
PAGBANK_TOKEN = get_payment_config('PAGBANK_TOKEN', 'PAGSEGURO_TOKEN')
PAGBANK_ENVIRONMENT = get_payment_config('PAGBANK_ENVIRONMENT', 'PAGSEGURO_ENVIRONMENT', 'sandbox')

# URLs de retorno
PAGBANK_SUCCESS_URL = get_payment_config(
    'PAGBANK_SUCCESS_URL', 
    'PAGSEGURO_SUCCESS_URL', 
    'http://localhost:3000/success'
)
PAGBANK_FAILURE_URL = get_payment_config(
    'PAGBANK_FAILURE_URL', 
    'PAGSEGURO_FAILURE_URL', 
    'http://localhost:3000/failure'
)
PAGBANK_NOTIFICATION_URL = get_payment_config(
    'PAGBANK_NOTIFICATION_URL', 
    'PAGSEGURO_NOTIFICATION_URL', 
    'http://localhost:8000/api/payments/webhook/'
)

# Configurações opcionais
PAGBANK_TIMEOUT = config('PAGBANK_TIMEOUT', default=30, cast=int)
PAGBANK_MAX_RETRIES = config('PAGBANK_MAX_RETRIES', default=3, cast=int)

# ===============================
# COMPATIBILIDADE REVERSA (manter código antigo funcionando)
# ===============================

# Garantir que as variáveis PagSeguro existam (para código antigo)
PAGSEGURO_EMAIL = PAGBANK_EMAIL
PAGSEGURO_TOKEN = PAGBANK_TOKEN
PAGSEGURO_ENVIRONMENT = PAGBANK_ENVIRONMENT
PAGSEGURO_SUCCESS_URL = PAGBANK_SUCCESS_URL
PAGSEGURO_FAILURE_URL = PAGBANK_FAILURE_URL
PAGSEGURO_NOTIFICATION_URL = PAGBANK_NOTIFICATION_URL

# ===============================
# LOGGING CONFIGURADO
# ===============================

# Criar diretório de logs se não existir
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': log_dir / 'pagbank.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'payments': {
            'handlers': ['console', 'file'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if DEBUG else 'WARNING',
    },
}

# ===============================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ===============================

if not DEBUG:
    # Configurações de segurança para produção
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True
    
    # Configurações de sessão
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

# ===============================
# CONFIGURAÇÕES ADICIONAIS DE DESENVOLVIMENTO
# ===============================

if DEBUG:
    # Configurações úteis para desenvolvimento
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Permitir hosts locais para desenvolvimento
    if 'localhost' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0'])

# ===============================
# VALIDAÇÃO DE CONFIGURAÇÕES CRÍTICAS
# ===============================

# Verificar se as configurações críticas estão definidas
CRITICAL_SETTINGS = {
    'PAGBANK_EMAIL': PAGBANK_EMAIL,
    'PAGBANK_TOKEN': PAGBANK_TOKEN,
}

missing_settings = [key for key, value in CRITICAL_SETTINGS.items() if not value]

if missing_settings and not DEBUG:
    # Em produção, falhar se configurações críticas estiverem faltando
    raise ValueError(f"Configurações críticas faltando: {', '.join(missing_settings)}")
elif missing_settings and DEBUG:
    # Em desenvolvimento, apenas avisar
    print(f"⚠️  AVISO: Configurações faltando no .env: {', '.join(missing_settings)}")
    print("   Adicione essas configurações para usar o gateway de pagamento.")

# ===============================
# CONFIGURAÇÕES DO DJANGO-EXTENSIONS (se instalado)
# ===============================

try:
    import django_extensions
    INSTALLED_APPS.append('django_extensions')
except ImportError:
    pass

# ===============================
# INFORMAÇÕES DO SISTEMA (para debug)
# ===============================

if DEBUG:
    SYSTEM_INFO = {
        'BASE_DIR': str(BASE_DIR),
        'DEBUG': DEBUG,
        'ENVIRONMENT': PAGBANK_ENVIRONMENT,
        'EMAIL_CONFIGURED': bool(PAGBANK_EMAIL),
        'TOKEN_CONFIGURED': bool(PAGBANK_TOKEN),
        'LOG_DIR': str(log_dir),
    }
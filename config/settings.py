"""
Config for video proc
"""
import os
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from celery.schedules import crontab

TIME_ZONE = 'Europe/London'
USE_TZ = True

ROOT_URLCONF = 'config.urls'

##### Dev settings
DEBUG = True
#####

DJANGO_SETTINGS_MODULE = 'config.settings'

# Set the tracer provider
trace.set_tracer_provider(TracerProvider())

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

otlp_exporter = OTLPSpanExporter(OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,backend,0.0.0.0,127.0.0.1").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'opentelemetry.instrumentation.django',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'django_celery_beat',
    'apps.videos',
]


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # or your custom path to static files
]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', "redis://localhost:6379/0")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    'retry-failed-videos': {
        'task': 'apps.videos.tasks.retry_failed_videos',
        'schedule': crontab(minute=0, hour='*'),
    },
}

# Celery Logging configuration

CELERYD_LOG_FORMAT = '[%(asctime)s: %(levelname)s] %(message)s'
CELERYD_LOG_LEVEL = 'INFO'  # or DEBUG, ERROR as per your needs
CELERYD_LOG_FILE = 'celery.log'  # Optional log file for Celery worker logs

# If you are using Celery with Django's logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'celery': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'videoproc'),
        'USER': os.getenv('POSTGRES_USER', 'admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'adminSecret'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-default-secret-key")

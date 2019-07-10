import os

from celery.schedules import crontab
from kombu import Queue, Exchange

BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672/')


CELERY_ALWAYS_EAGER = False
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_SERIALIZER = 'pickle'
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_IGNORE_RESULT = True
CELERY_TASK_RESULT_EXPIRES = 30


CELERY_DEFAULT_QUEUE = 'celery'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'celery'

CELERY_ROUTES = {
    's3bucket.apps.core.tasks.*': {
        'exchange': 'celery',
        'routing_key': 'celery'
    }
}


CELERYBEAT_SCHEDULE = {
    'update_bucket': {
        'task': 's3bucket.apps.core.tasks.update_bucket',
        'schedule': crontab(minute="*"),
    }
}

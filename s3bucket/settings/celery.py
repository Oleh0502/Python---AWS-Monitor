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


CELERY_QUEUES = (
    Queue('scheduler', Exchange('scheduler'), 'scheduler'),
    Queue('process', Exchange('process'), 'process'),
    Queue('download', Exchange('download'), 'download'),
    Queue('notify', Exchange('notify'), 'notify')
)

CELERY_ROUTES = {
    's3bucket.apps.core.tasks.update_bucket': {
        'exchange': 'scheduler',
        'routing_key': 'scheduler'
    },
    's3bucket.apps.core.tasks.process_bucket': {
        'exchange': 'process',
        'routing_key': 'process'
    },
    's3bucket.apps.core.tasks.download_file': {
        'exchange': 'download',
        'routing_key': 'download'
    },
    's3bucket.apps.core.tasks.send_pushover_notification': {
        'exchange': 'notify',
        'routing_key': 'notify'
    }
}


CELERYBEAT_SCHEDULE = {
    'update_bucket': {
        'task': 's3bucket.apps.core.tasks.update_bucket',
        'schedule': crontab(minute="*"),
    }
}

CELERY_IMPORTS = [
    "s3bucket.apps.core.tasks"
]

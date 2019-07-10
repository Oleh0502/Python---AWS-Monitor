import os

import dotenv
from celery import Celery

dotenv.load_dotenv(dotenv.find_dotenv())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's3bucket.settings')

from s3bucket.settings.apps import INSTALLED_APPS
from s3bucket.settings.celery import BROKER_URL

app = Celery('s3bucket', broker=BROKER_URL, backend='amqp')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: INSTALLED_APPS)

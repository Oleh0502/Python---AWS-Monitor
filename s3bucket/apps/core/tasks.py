import os
import traceback
import datetime as dt
from django.utils import timezone
from pushover import Client

from s3bucket.apps.amazon.bucket import BucketParser
from s3bucket.apps.amazon.download import DownloadFromBucket
from s3bucket.apps.core.models import Bucket, ContentHistory, ContentFile, Notifier
from s3bucket.celery import app


@app.task
def process_bucket(bucket: Bucket):
    try:
        BucketParser(bucket).main()
    except Exception:
        print(f'Error updating bucket {bucket.name}')
        traceback.print_exc()
        return


@app.task
def download_file(content_history: ContentHistory):
    try:
        filename = DownloadFromBucket(content_id=content_history.content.id).save_to_file()
        ContentFile.objects.create(history=content_history, filepath=filename)
    except Exception:
        print(traceback.format_exc())
        return


@app.task
def update_bucket():
    current_time = timezone.now()
    buckets = Bucket.objects.filter(public=True)
    for bucket in buckets:
        if bucket.update_every and current_time.minute % bucket.update_every == 0:
            process_bucket(bucket)


@app.task()
def send_pushover_notification(notifier_id):
    if notifier_id is None:
        raise ValueError

    try:
        notifier = Notifier.objects.get(id=notifier_id)
        if notifier.notification_status != Notifier.SETTLED:
            print('Already processed')
            return

        client = Client(os.environ.get('PUSHOVER_USER_KEY'), api_token=os.environ.get('PUSHOVER_API_KEY'))
        title = ''
        content = ''
        if notifier.notification_type == Notifier.FILE_CREATED:
            title = 'FILE ADDED'
            content = f'BUCKET NAME : {notifier.bucket.name} \nFILE ID : {notifier.bucket_file_id}'
        elif notifier.notification_type == Notifier.FILE_UPDATED:
            title = 'FILE UPDATED'
            content = f'BUCKET NAME : {notifier.bucket.name} \nFILE ID : {notifier.bucket_file_id}'
        elif notifier.notification_type == Notifier.FILE_EMPTY:
            title = 'NO FILES'
            content = f'BUCKET NAME : {notifier.bucket.name} \nNO FILES IN BUCKET'
        if title and content:
            client.send_message(content, title=title)
            notifier.finished_at = dt.datetime.utcnow()
            notifier.notification_status = Notifier.PROCESSED
            notifier.save()
            print('Notification sent')
        else:
            notifier.finished_at = dt.datetime.utcnow()
            notifier.notification_status = Notifier.CANCELLED
            notifier.save()
    except Exception as e:
        print(e)
        print(f'Error occurs while notifying to user. notifier_id: {notifier_id}')

from django.utils import timezone

from s3bucket.apps.amazon.bucket import BucketParser
from s3bucket.apps.core.models import Bucket
from s3bucket.celery import app


@app.task
def process_bucket(bucket: Bucket):
    try:
        BucketParser(bucket).main()
    except Exception:
        print(f'Error updating bucket {bucket.name}')
        return


@app.task
def update_bucket():
    current_time = timezone.now()
    buckets = Bucket.objects.filter(public=True)
    for bucket in buckets:
        if bucket.update_every and current_time.minute % bucket.update_every == 0:
            process_bucket.delay(bucket)

from datetime import datetime
from boto3.session import Session
from botocore.exceptions import ClientError

from s3bucket.apps.core.models import Bucket, BucketContent, ContentHistory, Notifier
from s3bucket.settings.credentials import AWS_ACCESS_KEY, AWS_SECRET_KEY


class BucketParser:
    def __init__(self, bucket: Bucket):
        self.bucket = bucket
        self.s3 = self.init_boto3()
        self.existed_files = []

    @staticmethod
    def init_boto3():
        return Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY).resource("s3")

    def main(self):
        bucket = self.s3.Bucket(self.bucket.name)
        try:
            from s3bucket.apps.core.tasks import download_file, send_pushover_notification
            empty = True
            if self.bucket.name == 'new-test-th':
                pass
            for obj in bucket.objects.all():
                if self.bucket.empty:
                    self.bucket.empty = False
                    self.bucket.save()

                empty = False
                self.existed_files.append(obj.key)
                content, created = BucketContent.objects.get_or_create(name=obj.key, bucket=self.bucket, defaults={
                    "last_modified": obj.last_modified, "e_tag": obj.e_tag
                })
                if created:
                    ch = ContentHistory.objects.create(content=content, action=ContentHistory.CREATED)
                    self.notify(content, Notifier.FILE_CREATED)
                    download_file.delay(ch)
                elif obj.last_modified != content.last_modified:
                    current_state = {"last_modified": str(obj.last_modified)}
                    ch = ContentHistory.objects.create(content=content, action=ContentHistory.UPDATED,
                                                       previous_state=current_state)
                    content.last_modified = obj.last_modified
                    content.save('last_modified')
                    self.notify(content, Notifier.FILE_UPDATED)
                    download_file.delay(ch)
                else:
                    continue
            self.check_deleted()

            if empty and not self.bucket.empty:
                self.bucket.empty = True
                self.bucket.save()
                self.notify(False, Notifier.FILE_EMPTY)

        except ClientError as e:
            if 'AccessDenied' in e.args[0]:
                self.bucket.public = False
                self.bucket.save(update_fields=["public"])
                return

    def check_deleted(self):
        removed_items = BucketContent.objects.filter(bucket=self.bucket, removed=False).exclude(
            name__in=self.existed_files)
        for removed_item in removed_items:
            removed_item.removed = True
            removed_item.save()
            ContentHistory.objects.create(content=removed_item, action=ContentHistory.DELETED)
            self.notify(removed_item, Notifier.FILE_DELETED)

    def notify(self, content, notification_type: str):
        if content:
            notifier = Notifier(bucket=Bucket.objects.get(name=self.bucket.name), bucket_file=content,
                                notification_type=notification_type,
                                notification_status=Notifier.SETTLED)

        else:
            dummy, _ = BucketContent.objects.get_or_create(name='Notifications_dummy', bucket=self.bucket, defaults={
                "last_modified": datetime.today(), "e_tag": 'notification_dummy'
            })
            notifier = Notifier(bucket=Bucket.objects.get(name=self.bucket.name), bucket_file=dummy,
                                notification_type=notification_type,
                                notification_status=Notifier.SETTLED)
        notifier.save()

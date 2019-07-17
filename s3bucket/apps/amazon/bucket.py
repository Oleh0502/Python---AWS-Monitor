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
            for obj in bucket.objects.all():
                self.existed_files.append(obj.key)
                content, created = BucketContent.objects.get_or_create(name=obj.key, defaults={
                    "last_modified": obj.last_modified, "bucket": self.bucket, "e_tag": obj.e_tag
                })

                if created:
                    ch = ContentHistory.objects.create(content=content, action=ContentHistory.CREATED)
                    notifier = Notifier(bucket=Bucket.objects.get(name=bucket.name), bucket_file=content,
                                        notification_type=Notifier.FILE_CREATED,
                                        notification_status=Notifier.SETTLED)
                    notifier.save()
                    download_file.delay(ch)
                elif obj.last_modified != content.last_modified:
                    current_state = {"last_modified": str(obj.last_modified)}
                    ch = ContentHistory.objects.create(content=content, action=ContentHistory.UPDATED,
                                                       previous_state=current_state)
                    content.last_modified = obj.last_modified
                    content.save('last_modified')
                    notifier = Notifier(bucket=Bucket.objects.get(name=bucket.name), bucket_file=content,
                                        notification_type=Notifier.FILE_UPDATED,
                                        notification_status=Notifier.SETTLED)
                    notifier.save()
                    download_file.delay(ch)
                else:
                    continue
            self.check_deleted()
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
            notifier = Notifier(bucket=Bucket.objects.get(name=removed_item.name), bucket_file=removed_item.name,
                                notification_type=Notifier.FILE_DELETED,
                                notification_status=Notifier.SETTLED)
            notifier.save()

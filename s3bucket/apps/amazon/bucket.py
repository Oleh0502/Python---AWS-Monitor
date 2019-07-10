from boto3.session import Session

from s3bucket.apps.core.models import Bucket, BucketContent, ContentHistory
from s3bucket.settings.credentials import AWS_ACCESS_KEY, AWS_SECRET_KEY


class BucketParser:
    def __init__(self, bucket: Bucket):
        self.bucket = bucket
        self.s3 = self.init_boto3()

    @staticmethod
    def init_boto3():
        return Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY).resource("s3")

    def main(self):
        bucket = self.s3.Bucket(self.bucket.name)
        for obj in bucket.objects.all():
            content, created = BucketContent.objects.get_or_create(name=obj.key, defaults={
                "last_modified": obj.last_modified, "bucket": self.bucket, "e_tag": obj.e_tag
            })
            if created:
                ContentHistory.objects.create(content=content, action=ContentHistory.CREATED)
            elif obj.last_modified != content.last_modified:
                current_state = {"last_modified": str(obj.last_modified)}
                ContentHistory.objects.create(content=content, action=ContentHistory.UPDATED,
                                              previous_state=current_state)
                content.last_modified = obj.last_modified
                content.save('last_modified')
            else:
                continue

    def check_deleted(self):
        pass

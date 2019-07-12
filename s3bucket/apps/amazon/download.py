from boto3 import Session
from django.http import HttpResponse

from s3bucket.apps.core.models import BucketContent
from s3bucket.settings.credentials import AWS_ACCESS_KEY, AWS_SECRET_KEY


class DownloadFromBucket:
    def __init__(self, content_id: int):
        self.content = BucketContent.objects.get(id=content_id)
        self.s3 = self.init_boto3()

    @staticmethod
    def init_boto3():
        return Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY).client("s3")

    def request_file(self):
        file_binary = self.s3.get_object(Bucket=self.content.bucket.name, Key=self.content.name)["Body"]
        response = HttpResponse(file_binary, content_type = 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{self.content.name}"'
        return response

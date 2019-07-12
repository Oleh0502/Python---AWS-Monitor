import os
import uuid

from boto3 import Session
from django.http import HttpResponse

from s3bucket.apps.core.models import BucketContent
from s3bucket.settings.common import MEDIA_ROOT
from s3bucket.settings.credentials import AWS_ACCESS_KEY, AWS_SECRET_KEY


class DownloadFromBucket:
    def __init__(self, content_id: int):
        self.content = BucketContent.objects.get(id=content_id)
        self.s3 = self.init_boto3()

    @staticmethod
    def init_boto3():
        return Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY).client("s3")

    def request_file(self):
        return self.s3.get_object(Bucket=self.content.bucket.name, Key=self.content.name)

    def download(self):
        response = HttpResponse(self.request_file()["Body"], content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{self.content.name}"'
        return response

    def save_to_file(self):
        filename = f"{uuid.uuid4()}_{self.content.name.split('/')[-1]}"
        stream = self.request_file()
        with open(os.path.join(MEDIA_ROOT, self.content.bucket.name, filename), 'wb') as binary_file:
            binary_file.write(stream["Body"].read())
        return filename

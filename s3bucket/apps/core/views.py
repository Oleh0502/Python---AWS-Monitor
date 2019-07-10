import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from s3bucket.apps.core.models import Bucket, BucketContent, ContentHistory


class Home(View):
    template_name = "home.html"

    def get(self, request):
        return render(request, self.template_name)


class BucketList(View):

    def get(self, request):
        response = {"aaData": [], "sEcho": 0}
        start = int(request.GET.get('start', '0'))
        length = int(request.GET.get('length', '0'))
        buckets = Bucket.objects.all()
        response['iTotalDisplayRecords'] = buckets.count()
        response['iTotalRecords'] = buckets.count()
        for bucket in buckets[start: start + length]:
            response['aaData'].append(
                [bucket.name, bucket.public, bucket.id]
            )
        return HttpResponse(json.dumps(response))


class BucketContentView(View):
    template_name = "bucket_content.html"

    def get(self, request, bucket_id):
        return render(request, self.template_name, context={"bucket_id": bucket_id})


class BucketContentList(View):

    def get(self, request, bucket_id):
        response = {"aaData": [], "sEcho": 0}
        start = int(request.GET.get('start', '0'))
        length = int(request.GET.get('length', '0'))
        content = BucketContent.objects.filter(bucket_id=bucket_id)
        response['iTotalDisplayRecords'] = content.count()
        response['iTotalRecords'] = content.count()
        for obj in content[start: start + length]:
            response['aaData'].append(
                [obj.name, str(obj.last_modified), obj.history.last().get_action_display(), obj.id]
            )
        return HttpResponse(json.dumps(response))


class ContentHistoryView(View):
    template_name = "content_history.html"

    def get(self, request, content_id):
        return render(request, self.template_name, context={"content_id": content_id})


class ContentHistoryList(View):

    def get(self, request, content_id):
        response = {"aaData": [], "sEcho": 0}
        start = int(request.GET.get('start', '0'))
        length = int(request.GET.get('length', '0'))
        content = ContentHistory.objects.filter(content_id=content_id).order_by('-updated')
        response['iTotalDisplayRecords'] = content.count()
        response['iTotalRecords'] = content.count()
        for obj in content[start: start + length]:
            response['aaData'].append(
                [obj.get_action_display(), str(obj.content.last_modified),
                 obj.previous_state.get('last_modified', '') if obj.previous_state else '']
            )
        return HttpResponse(json.dumps(response))

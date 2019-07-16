from datetime import date, timedelta
import json

from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from s3bucket.apps.core.models import Bucket, BucketContent, ContentHistory, ContentFile


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
        last = {
            "day": date.today() - timedelta(days=1),
            "week": date.today() - timedelta(days=7),
            "month": date.today() - timedelta(days=30),
            "three_months": date.today() - timedelta(days=90),
        }
        for bucket in buckets[start: start + length]:
            files_count = bucket.content.all().count()
            content_changes_for_day = self.content_change(bucket, last['day'], files_count)
            content_changes_for_week = self.content_change(bucket, last['week'], files_count)
            content_changes_for_month = self.content_change(bucket, last['month'], files_count)
            content_changes_for_three_months = self.content_change(bucket, last['three_months'], files_count)

            response['aaData'].append(
                [bucket.name,
                 bucket.public,
                 content_changes_for_day,
                 content_changes_for_week,
                 content_changes_for_month,
                 content_changes_for_three_months,
                 files_count,
                 bucket.id]
            )
        return HttpResponse(json.dumps(response))

    def content_change(self, bucket, filter_date, files_count):
        content_query = bucket.content.filter(Q(updated__gt=filter_date))
        content_changes = {
            'added': 0,
            'modified': 0,
            'no_change': 0,
            'removed': 0,
        }
        if not content_query.count() > 0:
            content_changes.update({'no_change': files_count})
            return content_changes

        content_changes['added'] += content_query.filter(history__action=1).count()
        content_changes['modified'] += content_query.filter(history__action=2).count()
        # ContentHistory.objects.values(content_id__in=content_query, action=2).annotate(Count('content_id'))
        content_changes['removed'] += content_query.filter(history__action=3).count()
        content_changes['no_change'] += bucket.content.exclude(id__in=content_query).count()
        return content_changes


class BucketContentView(View):
    template_name = "bucket_content.html"

    def get(self, request, bucket_id):
        return render(request, self.template_name, context={"bucket": Bucket.objects.get(id=bucket_id)})


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
                [obj.name.split('/'), str(obj.last_modified), obj.state, obj.id]
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
                 obj.previous_state.get('last_modified', '') if obj.previous_state else '', obj.id]
            )
        return HttpResponse(json.dumps(response))


class DownloadFile(View):

    def get(self, request, content_id):
        content = ContentFile.objects.filter(history__content_id=content_id).order_by('-updated').first()
        if not content:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()
        with open(content.get_full_path(), 'rb') as download:
            response = HttpResponse(download.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{content.history.content.name}"'
            return response


class DownloadHistory(View):

    def get(self, request, history_id):
        try:
            content = ContentFile.objects.get(history_id=history_id)
            with open(content.get_full_path(), 'rb') as download:
                response = HttpResponse(download.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{content.history.content.name}"'
                return response
        except Exception:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()

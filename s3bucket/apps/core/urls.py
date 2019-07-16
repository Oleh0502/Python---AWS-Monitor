from django.contrib.auth.decorators import login_required
from django.urls import path, include

from s3bucket.apps.core.views import Home, BucketList, BucketContentView, BucketContentList, ContentHistoryView, \
    ContentHistoryList, DownloadFile, DownloadHistory

app_name = "core"

ajax_patterns = [
    path('bucket_list', login_required(BucketList.as_view()), name='bucket_list'),
    path('bucket_content/<bucket_id>', login_required(BucketContentList.as_view())),
    path('content_history/<content_id>', login_required(ContentHistoryList.as_view())),
    path('download/<content_id>', login_required(DownloadFile.as_view())),
    path('download/history/<history_id>', login_required(DownloadHistory.as_view())),
]

urlpatterns = [
    path('', login_required(Home.as_view()), name='home'),
    path('ajax/', include(ajax_patterns)),
    path('bucket_content/<bucket_id>', login_required(BucketContentView.as_view())),
    path('content_history/<content_id>', login_required(ContentHistoryView.as_view()))
]

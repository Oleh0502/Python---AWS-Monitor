from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from s3bucket.settings.common import STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('s3bucket.apps.accounts.urls', namespace='accounts')),
    path('', include("s3bucket.apps.core.urls", namespace="core"))
] + static(STATIC_URL, document_root=STATIC_ROOT)

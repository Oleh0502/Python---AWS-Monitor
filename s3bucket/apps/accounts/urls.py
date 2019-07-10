from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path

from s3bucket.apps.accounts.views import Login, Logout
from s3bucket.settings.common import STATIC_ROOT, STATIC_URL

app_name = "accounts"

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + static(STATIC_URL, document_root=STATIC_ROOT)

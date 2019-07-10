from django.contrib import admin

from s3bucket.apps.core.models import Bucket


class BucketAdmin(admin.ModelAdmin):
    list_display = ('name', )


admin.site.register(Bucket, BucketAdmin)

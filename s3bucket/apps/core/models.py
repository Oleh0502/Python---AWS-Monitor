from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from django_mysql.models import JSONField


class Bucket(models.Model):
    name = models.CharField(max_length=128, null=False)
    public = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    update_every = models.IntegerField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated = timezone.now()
        super(Bucket, self).save()


class BucketContent(models.Model):
    e_tag = models.CharField(max_length=64)
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='content')
    name = models.CharField(null=False, max_length=256)
    last_modified = models.DateTimeField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('e_tag', 'name')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated = timezone.now()
        super().save()

    def to_dict(self):
        return model_to_dict(self, exclude=['id', 'created', 'updated'])


class ContentHistory(models.Model):
    CREATED = 1
    UPDATED = 2
    DELETED = 3

    ACTION_CHOICE = (
        (CREATED, "Created"),
        (UPDATED, "Updated"),
        (DELETED, "Deleted")
    )

    content = models.ForeignKey(BucketContent, on_delete=models.CASCADE, related_name='history')
    updated = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField(choices=ACTION_CHOICE, default=CREATED)
    previous_state = JSONField(null=True, blank=True, default=None)

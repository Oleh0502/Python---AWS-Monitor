# Generated by Django 2.2.3 on 2019-07-12 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_bucket_update_every'),
    ]

    operations = [
        migrations.AddField(
            model_name='bucketcontent',
            name='removed',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.2.3 on 2019-07-10 12:40

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('public', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BucketContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('e_tag', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=256)),
                ('last_modified', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content', to='core.Bucket')),
            ],
            options={
                'unique_together': {('e_tag', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ContentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('action', models.IntegerField(choices=[(1, 'Created'), (2, 'Updated'), (3, 'Deleted')], default=1)),
                ('previous_state', django_mysql.models.JSONField(blank=True, default=None, null=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='core.BucketContent')),
            ],
        ),
    ]

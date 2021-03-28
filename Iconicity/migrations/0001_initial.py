# Generated by Django 3.1.6 on 2021-03-28 18:33

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('type', models.CharField(default='comment', max_length=10)),
                ('author', models.URLField(default='')),
                ('post', models.URLField(default='')),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(default='')),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalServer',
            fields=[
                ('host', models.URLField(default='', primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='Follow', max_length=10)),
                ('summary', models.TextField(default='')),
                ('actor', models.URLField(default='')),
                ('object', models.URLField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='inbox', max_length=10)),
                ('author', models.URLField(default='')),
                ('items', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(default='Like', max_length=10)),
                ('context', models.URLField(default='')),
                ('summary', models.TextField(default='')),
                ('author', models.JSONField(default=dict)),
                ('object', models.URLField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_type', models.CharField(default='author', max_length=10)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('display_name', models.CharField(default='', max_length=30)),
                ('github', models.URLField(default='')),
                ('host', models.URLField(default='')),
                ('url', models.URLField(default='')),
                ('externalFollows', models.JSONField(default=dict)),
                ('follow', models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(default='', max_length=100)),
                ('type', models.CharField(default='post', max_length=10)),
                ('source', models.URLField(default='')),
                ('origin', models.URLField(default='')),
                ('description', models.CharField(default='', max_length=250)),
                ('contentType', models.CharField(choices=[('text/plain', 'text/plain'), ('text/markdown', 'text/markdown'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='', max_length=40)),
                ('content', models.TextField(default='')),
                ('categories', models.JSONField(default=dict)),
                ('count', models.IntegerField(default=0)),
                ('size', models.IntegerField(default=0)),
                ('external_likes', models.JSONField(default=dict)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS')], default='PUBLIC', max_length=10)),
                ('unlisted', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('host', models.URLField(default='')),
                ('author', models.ForeignKey(default=django.contrib.auth.models.User, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('like', models.ManyToManyField(related_name='blog_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 3.1.6 on 2021-03-29 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iconicity', '0002_auto_20210328_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.JSONField(default=dict, max_length=500),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='actor',
            field=models.URLField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='object',
            field=models.URLField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='inbox',
            name='items',
            field=models.JSONField(default=dict, max_length=10000),
        ),
        migrations.AlterField(
            model_name='like',
            name='author',
            field=models.JSONField(default=dict, max_length=500),
        ),
        migrations.AlterField(
            model_name='like',
            name='object',
            field=models.JSONField(default=dict, max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='external_likes',
            field=models.JSONField(default=dict, max_length=5000),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='externalFollows',
            field=models.JSONField(default=dict, max_length=5000),
        ),
    ]

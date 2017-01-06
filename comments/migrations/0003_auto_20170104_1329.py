# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_comment_max_depth'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedUserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.TextField(blank=True)),
                ('last_name', models.TextField(blank=True)),
                ('email', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(related_name='comments', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='commentversion',
            name='posting_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='deleted_user_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='comments.DeletedUserInfo', null=True),
        ),
        migrations.AddField(
            model_name='commentversion',
            name='deleted_user_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='comments.DeletedUserInfo', null=True),
        ),
    ]

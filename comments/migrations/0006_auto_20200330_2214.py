# Generated by Django 2.2.11 on 2020-03-31 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0005_comment_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]

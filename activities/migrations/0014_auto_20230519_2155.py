# Generated by Django 3.1.1 on 2023-05-19 19:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_activity_punctures_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessory',
            name='activities',
        ),
        migrations.AddField(
            model_name='accessory',
            name='deregistered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='deregistered at'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='registered_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='registered at'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'chain'), (2, 'tyre'), (3, 'tube'), (4, 'other')], default=1, verbose_name='type'),
            preserve_default=False,
        ),
    ]
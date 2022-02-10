# Generated by Django 3.1.1 on 2022-02-10 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_auto_20201010_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='max_heartrate',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='max heartrate'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Run'), (2, 'Ride'), (3, 'Hike'), (4, 'Nordic Ski'), (5, 'Roller Ski'), (6, 'Alpine Ski'), (7, 'Swim'), (8, 'Walk'), (9, 'Canoeing'), (10, 'Rock Climbing'), (11, 'Ice Skate'), (12, 'Workout'), (13, 'Other'), (14, 'Virtual Ride'), (15, 'Virtual Run'), (16, 'Backcountry Ski')], verbose_name='type'),
        ),
    ]

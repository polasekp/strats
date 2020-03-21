# Generated by Django 3.0 on 2020-03-21 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0006_auto_20191211_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Run'), (2, 'Ride'), (3, 'Hike'), (4, 'Nordic Ski'), (5, 'Roller Ski'), (6, 'Alpine Ski'), (7, 'Swim'), (8, 'Walk'), (9, 'Canoeing'), (10, 'Rock Climbing'), (11, 'Ice Skate'), (12, 'Workout'), (13, 'Other'), (14, 'Virtual Ride')], verbose_name='type'),
        ),
    ]

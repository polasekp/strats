# Generated by Django 2.1.7 on 2019-04-11 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accessory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('changed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='changed at')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'accessory',
                'verbose_name_plural': 'accessories',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('changed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='changed at')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('strava_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='strava ID')),
                ('distance', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='distance (m)')),
                ('average_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='average speed (m/s)')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('moving_time', models.DurationField(blank=True, null=True, verbose_name='moving time')),
                ('elapsed_time', models.DurationField(verbose_name='elapsed time')),
                ('elevation_gain', models.IntegerField(blank=True, null=True, verbose_name='elevation gain')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Run'), (2, 'Ride'), (3, 'Hike'), (4, 'Nordic Ski'), (5, 'Roller Ski'), (6, 'Alpine Ski'), (7, 'Swim'), (8, 'Walk'), (9, 'Canoeing'), (10, 'Rock Climbing'), (11, 'Ice Skate'), (12, 'Workout'), (13, 'Other')], verbose_name='type')),
                ('kudos', models.IntegerField(blank=True, null=True, verbose_name='kudos count')),
                ('achievements', models.IntegerField(blank=True, null=True, verbose_name='achievements count')),
                ('comments', models.IntegerField(blank=True, null=True, verbose_name='comments count')),
                ('race', models.BooleanField(default=False, verbose_name='is race')),
                ('commute', models.BooleanField(default=False, verbose_name='is commute')),
                ('athlete_count', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='strava athletes count')),
            ],
            options={
                'verbose_name': 'activity',
                'verbose_name_plural': 'activities',
                'ordering': ('-start',),
            },
        ),
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('changed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='changed at')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
            ],
            options={
                'verbose_name': 'athlete',
                'verbose_name_plural': 'athletes',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Gear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('changed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='changed at')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Shoe'), (2, 'Bike'), (3, 'Ski'), (4, 'Other')], verbose_name='gear type')),
                ('strava_id', models.CharField(blank=True, max_length=10, null=True, verbose_name='strava ID')),
            ],
            options={
                'verbose_name': 'gear',
                'verbose_name_plural': 'gears',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('changed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='changed at')),
                ('name', models.SlugField(max_length=30, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='activity',
            name='athletes',
            field=models.ManyToManyField(blank=True, related_name='activities', to='activities.Athlete', verbose_name='athletes'),
        ),
        migrations.AddField(
            model_name='activity',
            name='gear',
            field=models.ManyToManyField(blank=True, related_name='activities', to='activities.Gear', verbose_name='gear'),
        ),
        migrations.AddField(
            model_name='activity',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='activities', to='activities.Tag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='activities',
            field=models.ManyToManyField(blank=True, related_name='accessories', to='activities.Activity', verbose_name='activities'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='gear',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessories', to='activities.Gear', verbose_name='gear'),
        ),
    ]

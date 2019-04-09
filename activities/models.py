from chamber.models.fields import SubchoicesPositiveIntegerField
from chamber.utils.datastructures import ChoicesEnum, ChoicesNumEnum, SubstatesChoicesNumEnum
from django.db import models


class Activity(models.Model):

    SPORT = (
        (1, 'RUN'),
        (2, 'RIDE'),
        (3, 'HIKE'),
        (4, 'XC_SKI'),
        (5, 'ROLLER_SKI'),
        (6, 'ALPINE_SKI'),
        (7, 'SWIM'),
        (8, 'WALK'),
        (9, 'CANOENING'),
        (10, 'CLIMBING'),
        (11, 'ICE_SKATE'),
        (12, 'WORKOUT'),
        (13, 'OTHER'),
    )

    name = models.CharField(verbose_name='name', max_length=255, null=False, blank=False)
    strava_id = models.PositiveIntegerField(verbose_name='strava ID', null=True, blank=True)
    distance = models.DecimalField(verbose_name='distance (m)', decimal_places=2, max_digits=9, null=True, blank=True)
    average_speed = models.DecimalField(verbose_name='average speed (m/s)', decimal_places=2, max_digits=7, null=True,
                                        blank=True)
    start = models.DateTimeField(verbose_name='start', null=False, blank=False)
    moving_time = models.DurationField(verbose_name='moving time', null=True, blank=True)
    elapsed_time = models.DurationField(verbose_name='elapsed time', null=False, blank=False)
    elevation_gain = models.IntegerField(verbose_name='elevation gain', null=True, blank=True)
    sport = models.PositiveSmallIntegerField(verbose_name='sport', choices=SPORT, null=False, blank=False)
    # sport_type = SubchoicesPositiveIntegerField(verbose_name='sport type', null=True, blank=False, enum=SPORT_TYPE,
    #                                             supchoices_field_name='sport')
    gear = models.ManyToManyField('Gear', verbose_name='gear', related_name='activities', blank=True)
    kudos = models.IntegerField(verbose_name='kudos count', null=True, blank=True)
    achievements = models.IntegerField(verbose_name='achievements count', null=True, blank=True)
    comments = models.IntegerField(verbose_name='comments count', null=True, blank=True)
    race = models.BooleanField(verbose_name='is race', default=False)
    commute = models.BooleanField(verbose_name='is commute', default=False)
    # Strava does not enable to get related athletes, just the count. Therefore athletes has to be connected
    # manually with activity and the count of connected athletes and athlete count may differ
    athlete_count = models.PositiveSmallIntegerField(verbose_name='athlete count', null=True, blank=True)
    athletes = models.ManyToManyField('Athlete', verbose_name='athletes', related_name='activities', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name='tags', related_name='activities', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start']


class Athlete(models.Model):

    name = models.CharField(verbose_name='name', max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Gear(models.Model):

    TYPE = (
        (1, 'SHOE'),
        (2, 'BIKE'),
        (3, 'SKI'),
        (4, 'OTHER'),
    )

    name = models.CharField(verbose_name='name', max_length=50, null=False, blank=False)
    type = models.PositiveSmallIntegerField(verbose_name='gear type', choices=TYPE, null=False, blank=False)
    strava_id = models.CharField(verbose_name='strava ID', max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Accessory(models.Model):

    name = models.CharField(verbose_name='name', max_length=50, null=False, blank=False)
    activities = models.ManyToManyField('Activity', verbose_name='activities', blank=True, related_name='accessories')
    gear = models.ForeignKey('Gear', verbose_name='gear', null=False, blank=False, on_delete=models.CASCADE,
                             related_name='accessories')
    is_active = models.BooleanField(verbose_name='is active', default=True)

    def __str__(self):
        return f'{self.name} ({self.gear})'


class Tag(models.Model):

    name = models.SlugField(verbose_name='slug', max_length=30, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name

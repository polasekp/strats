from chamber.models import SmartModel
from chamber.utils.datastructures import ChoicesNumEnum
from django.db import models


class Activity(SmartModel):

    TYPE = ChoicesNumEnum(
        ('RUN', 'Run', 1),
        ('RIDE', 'Ride', 2),
        ('HIKE', 'Hike', 3),
        ('XC_SKI', 'Nordic Ski', 4),
        ('ROLLER_SKI', 'Roller Ski', 5),
        ('ALPINE_SKI', 'Alpine Ski', 6),
        ('SWIM', 'Swim', 7),
        ('WALK', 'Walk', 8),
        ('CANOEING', 'Canoeing', 9),
        ('CLIMBING', 'Rock Climbing', 10),
        ('ICE_SKATE', 'Ice Skate', 11),
        ('WORKOUT', 'Workout', 12),
        ('OTHER', 'Other', 13),
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
    type = models.PositiveSmallIntegerField(verbose_name='type', choices=TYPE.choices, null=False, blank=False)
    gear = models.ManyToManyField('Gear', verbose_name='gear', related_name='activities', blank=True)
    kudos = models.IntegerField(verbose_name='kudos count', null=True, blank=True)
    achievements = models.IntegerField(verbose_name='achievements count', null=True, blank=True)
    comments = models.IntegerField(verbose_name='comments count', null=True, blank=True)
    race = models.BooleanField(verbose_name='is race', default=False)
    commute = models.BooleanField(verbose_name='is commute', default=False)
    # Strava does not enable to get related athletes, just the count. Therefore athletes has to be connected
    # manually with activity and the count of connected athletes and athlete count may differ
    athlete_count = models.PositiveSmallIntegerField(verbose_name='strava athletes count', null=True, blank=True)
    athletes = models.ManyToManyField('Athlete', verbose_name='athletes', related_name='activities', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name='tags', related_name='activities', blank=True)

    def __str__(self):
        return f'{self.name} #{self.tags.all()}'
        # return f'{map(lambda name: '#' + name, Tag.objects.all().values_list('name', flat=True))}'

    class Meta:
        ordering = ('-start',)
        verbose_name = 'activity'
        verbose_name_plural = 'activities'


class Athlete(SmartModel):

    first_name = models.CharField(verbose_name='first name', max_length=50, null=False, blank=False)
    last_name = models.CharField(verbose_name='last name', max_length=50, null=True, blank=True)
    nickname = models.CharField(verbose_name='nickname', max_length=50, null=True, blank=True)

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}' if not self.nickname else self.nickname

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'athlete'
        verbose_name_plural = 'athletes'


class Gear(SmartModel):

    TYPE = ChoicesNumEnum(
        ('SHOE', 'Shoe', 1),
        ('BIKE', 'Bike', 2),
        ('SKI', 'Ski', 3),
        ('OTHER', 'Other', 4),
    )

    name = models.CharField(verbose_name='name', max_length=50, null=False, blank=False)
    type = models.PositiveSmallIntegerField(verbose_name='gear type', choices=TYPE.choices, null=False, blank=False)
    strava_id = models.CharField(verbose_name='strava ID', max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'gear'
        verbose_name_plural = 'gears'


class Accessory(SmartModel):

    name = models.CharField(verbose_name='name', max_length=50, null=False, blank=False)
    activities = models.ManyToManyField('Activity', verbose_name='activities', blank=True, related_name='accessories')
    gear = models.ForeignKey('Gear', verbose_name='gear', null=False, blank=False, on_delete=models.CASCADE,
                             related_name='accessories')
    is_active = models.BooleanField(verbose_name='is active', default=True)

    def __str__(self):
        return f'{self.name} ({self.gear})'

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'accessory'
        verbose_name_plural = 'accessories'


class Tag(SmartModel):

    name = models.SlugField(verbose_name='slug', max_length=30, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

import logging
import math
import time

from chamber.models import SmartModel
from chamber.utils.datastructures import ChoicesNumEnum
from django.db import models

logger = logging.getLogger(__name__)


class StravaToken(SmartModel):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.PositiveIntegerField()

    @property
    def is_expired(self):
        return time.time() > self.expires_at


class Activity(SmartModel):

    _STRAVA_HELPER = None
    _GARMIN_HELPER = None

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
        ('VIRTUAL_RIDE', 'Virtual Ride', 14),
    )

    name = models.CharField(verbose_name='name', max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)
    strava_id = models.PositiveIntegerField(verbose_name='strava ID', null=True, blank=True, unique=True)
    athlete_id = models.PositiveIntegerField(verbose_name='athlete ID')
    external_id = models.CharField(verbose_name='external ID', max_length=255, null=True, blank=True)
    device_name = models.CharField(verbose_name='device name', max_length=255, blank=True)
    distance = models.DecimalField(verbose_name='distance (m)', decimal_places=2, max_digits=9, null=True, blank=True)
    average_speed = models.DecimalField(verbose_name='average speed (m/s)', decimal_places=2, max_digits=7, null=True,
                                        blank=True)
    max_speed = models.DecimalField(verbose_name='max speed (m/s)', decimal_places=2, max_digits=7, null=True,
                                    blank=True)
    average_heartrate = models.DecimalField(verbose_name='average heartrate', decimal_places=1, max_digits=7, null=True,
                                            blank=True)
    max_heartrate = models.PositiveIntegerField(verbose_name='elevation gain', null=True, blank=True)
    calories = models.PositiveIntegerField(verbose_name='calories', null=True, blank=True)
    average_temp = models.IntegerField(verbose_name='average temp', null=True, blank=True)
    average_cadence = models.DecimalField(verbose_name='average cadence', decimal_places=1, max_digits=5, null=True,
                                          blank=True)
    start = models.DateTimeField(verbose_name='start', null=False, blank=False)
    start_lat = models.DecimalField(verbose_name='start latitude', decimal_places=6, max_digits=8, null=True,
                                    blank=True)
    start_lon = models.DecimalField(verbose_name='start longitude', decimal_places=6, max_digits=9, null=True,
                                    blank=True)
    end_lat = models.DecimalField(verbose_name='end latitude', decimal_places=6, max_digits=8, null=True, blank=True)
    end_lon = models.DecimalField(verbose_name='end longitude', decimal_places=6, max_digits=9, null=True, blank=True)
    moving_time = models.DurationField(verbose_name='moving time', null=True, blank=True)
    elapsed_time = models.DurationField(verbose_name='elapsed time', null=False, blank=False)
    elevation_gain = models.PositiveIntegerField(verbose_name='elevation gain', null=True, blank=True)
    type = models.PositiveSmallIntegerField(verbose_name='type', choices=TYPE.choices, null=False, blank=False)
    gear = models.ManyToManyField('Gear', verbose_name='gear', related_name='activities', blank=True)
    kudos_count = models.PositiveIntegerField(verbose_name='kudos count', null=True, blank=True)
    photo_count = models.PositiveIntegerField(verbose_name='photo count', null=True, blank=True)
    achievement_count = models.PositiveIntegerField(verbose_name='achievement count', null=True, blank=True)
    comment_count = models.PositiveIntegerField(verbose_name='comment count', null=True, blank=True)
    pr_count = models.PositiveIntegerField(verbose_name='pr count', null=True, blank=True)
    race = models.BooleanField(verbose_name='is race', default=False)
    flagged = models.BooleanField(verbose_name='flagged', default=False)
    commute = models.BooleanField(verbose_name='is commute', default=False)
    manual = models.BooleanField(verbose_name='is manual', default=False)
    has_heartrate = models.BooleanField(verbose_name='has heartrate', default=False)
    visibility = models.CharField(verbose_name='visibility', max_length=100, blank=True)
    # Strava does not enable to get related athletes, just the count. Therefore athletes has to be connected
    # manually with activity and the count of connected athletes and athlete count may differ
    athlete_count = models.PositiveSmallIntegerField(verbose_name='strava athletes count', null=True, blank=True)
    athletes = models.ManyToManyField('Athlete', verbose_name='athletes', related_name='activities', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name='tags', related_name='activities', blank=True)

    def __str__(self):
        return f'{str.upper(self.TYPE.get_label(self.type))} ------- {self.name} ------ {self.tags_formatted}' if self.id else ""

    @property
    def strava_helper(self):
        if not self._STRAVA_HELPER:
            from utils.strava import StravaHelper
            # we want to set it as class attribute (so that not needed to create fot each instance)
            Activity._STRAVA_HELPER = StravaHelper()
        return self._STRAVA_HELPER

    @property
    def garmin_helper(self):
        if not self._GARMIN_HELPER:
            from utils.garmin import GarminHelper
            # we want to set it as class attribute (so that not needed to create fot each instance)
            Activity._GARMIN_HELPER = GarminHelper()
        return self._GARMIN_HELPER

    @property
    def start_date_formatted(self):
        return self.start.strftime("%d.%m.")

    @property
    def distance_km(self):
        return round(self.distance/1000, 1)

    @property
    def other_athletes_count(self):
        return self.athlete_count - 1

    @property
    def other_athletes_emoji(self):
        return " " + (self.athlete_count - 1) * f"👨" if self.athlete_count > 1 else ""

    @property
    def kudos_emoji(self):
        kudos_ceil = math.ceil(self.kudos_count/10)
        return " " + kudos_ceil * "👍" + f" {self.kudos_count}" if kudos_ceil > 0 else ""

    @property
    def kudos_emoji_floor(self):
        kudos_floor = math.floor(self.kudos_count/10)
        return " " + kudos_floor * "👍" if kudos_floor > 0 else ""

    @property
    def emoji_description(self):
        join_items = [f"{self.distance_km} km", self.other_athletes_emoji, self.kudos_emoji]
        return " | ".join(filter(None, join_items))

    @property
    def emoji_description_2(self):
        join_items = [f"{self.distance_km} km", self.other_athletes_emoji, self.kudos_emoji_floor]
        return " ".join(filter(None, join_items))

    @property
    def style_emoji(self):
        tag_names = self.tags.values_list("name", flat=True)
        if "classic" in tag_names:
            return "🎿"
        elif "skate" in tag_names:
            return "⛸️"
        else:
            return "❔"

    @property
    def tags_formatted(self):
        if self.tags.exists():
            return ', '.join([f'#{tag}' for tag in self.tags.all().values_list('name', flat=True)])
        else:
            return ''

    def get_garmin_id(self):
        """The external_id of a garmin activity is in format `garmin_push_4676669572`"""
        try:
            external_id = self.external_id.split("_")
        except AttributeError:
            return
        if external_id[0] != "garmin" or len(external_id) != 3:
            return
        return external_id[-1]

    def refresh_from_strava(self):
        self.strava_helper.refresh_activity(self)
        self.refresh_from_db()

    def download_garmin_fit(self):
        garmin_id = self.get_garmin_id()
        if not garmin_id:
            logger.warning(f"Requested to download not garmin activity. {self.strava_id}")
            return
        self.garmin_helper.download_activity(garmin_id)

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

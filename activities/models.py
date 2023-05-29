import logging
import math
import time
from datetime import datetime

from chamber.models import SmartModel
from chamber.utils.datastructures import ChoicesNumEnum
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, QuerySet

logger = logging.getLogger(__name__)

STRAVA_HELPER = settings.STRAVA_HELPER
GARMIN_HELPER = settings.GARMIN_HELPER


class StravaToken(SmartModel):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.PositiveIntegerField()

    @property
    def is_expired(self):
        return time.time() > self.expires_at


class Activity(SmartModel):

    TYPE = ChoicesNumEnum(
        ("RUN", "Run", 1),
        ("RIDE", "Ride", 2),
        ("HIKE", "Hike", 3),
        ("XC_SKI", "Nordic Ski", 4),
        ("ROLLER_SKI", "Roller Ski", 5),
        ("ALPINE_SKI", "Alpine Ski", 6),
        ("SWIM", "Swim", 7),
        ("WALK", "Walk", 8),
        ("CANOEING", "Canoeing", 9),
        ("CLIMBING", "Rock Climbing", 10),
        ("ICE_SKATE", "Ice Skate", 11),
        ("WORKOUT", "Workout", 12),
        ("OTHER", "Other", 13),
        ("VIRTUAL_RIDE", "Virtual Ride", 14),
        ("VIRTUAL_RUN", "Virtual Run", 15),
        ("BACKCOUNTRY_SKI", "Backcountry Ski", 16),
    )

    TYPE_EMOJI = {
        TYPE.RUN: "🏃",
        TYPE.RIDE: "🚴",
        TYPE.VIRTUAL_RIDE: "rouvy",
        TYPE.XC_SKI: "❄",
    }

    TYPES_RUN = [TYPE.RUN, TYPE.VIRTUAL_RUN]
    TYPES_RIDE = [TYPE.RIDE, TYPE.VIRTUAL_RIDE]

    name = models.CharField(verbose_name="name", max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)
    strava_id = models.PositiveIntegerField(verbose_name="strava ID", null=True, blank=True, unique=True)
    athlete_id = models.PositiveIntegerField(verbose_name="athlete ID")
    external_id = models.CharField(verbose_name="external ID", max_length=255, null=True, blank=True)
    device_name = models.CharField(verbose_name="device name", max_length=255, blank=True)
    distance = models.DecimalField(verbose_name="distance (m)", decimal_places=2, max_digits=9, null=True, blank=True)
    average_speed = models.DecimalField(
        verbose_name="average speed (m/s)", decimal_places=2, max_digits=7, null=True, blank=True
    )
    max_speed = models.DecimalField(
        verbose_name="max speed (m/s)", decimal_places=2, max_digits=7, null=True, blank=True
    )
    average_heartrate = models.DecimalField(
        verbose_name="average heartrate", decimal_places=1, max_digits=7, null=True, blank=True
    )
    max_heartrate = models.PositiveIntegerField(verbose_name="max heartrate", null=True, blank=True)
    calories = models.PositiveIntegerField(verbose_name="calories", null=True, blank=True)
    average_temp = models.IntegerField(verbose_name="average temp", null=True, blank=True)
    average_cadence = models.DecimalField(
        verbose_name="average cadence", decimal_places=1, max_digits=5, null=True, blank=True
    )
    average_power = models.IntegerField(verbose_name="average power", null=True, blank=True)
    max_power = models.IntegerField(verbose_name="max power", null=True, blank=True)
    weighted_average_power = models.IntegerField(verbose_name="weighted average power", null=True, blank=True)
    # True if the watts are from a power meter, false if estimated
    has_power_meter = models.BooleanField(verbose_name="has power meter", default=False)
    kcal = models.IntegerField(verbose_name="kCal", null=True, blank=True)
    suffer_score = models.IntegerField(verbose_name="suffer score", null=True, blank=True)

    start = models.DateTimeField(verbose_name="start", null=False, blank=False)
    start_lat = models.DecimalField(
        verbose_name="start latitude", decimal_places=6, max_digits=8, null=True, blank=True
    )
    start_lon = models.DecimalField(
        verbose_name="start longitude", decimal_places=6, max_digits=9, null=True, blank=True
    )
    end_lat = models.DecimalField(verbose_name="end latitude", decimal_places=6, max_digits=8, null=True, blank=True)
    end_lon = models.DecimalField(verbose_name="end longitude", decimal_places=6, max_digits=9, null=True, blank=True)
    moving_time = models.DurationField(verbose_name="moving time", null=True, blank=True)
    elapsed_time = models.DurationField(verbose_name="elapsed time", null=False, blank=False)
    elevation_gain = models.PositiveIntegerField(verbose_name="elevation gain", null=True, blank=True)
    type = models.PositiveSmallIntegerField(verbose_name="type", choices=TYPE.choices, null=False, blank=False)
    type_strava = models.CharField(verbose_name="type Strava", max_length=100, blank=True)
    gear = models.ManyToManyField("Gear", verbose_name="gear", related_name="activities", blank=True)
    kudos_count = models.PositiveIntegerField(verbose_name="kudos count", null=True, blank=True)
    photo_count = models.PositiveIntegerField(verbose_name="photo count", null=True, blank=True)
    achievement_count = models.PositiveIntegerField(verbose_name="achievement count", null=True, blank=True)
    comment_count = models.PositiveIntegerField(verbose_name="comment count", null=True, blank=True)
    punctures_count = models.PositiveSmallIntegerField(verbose_name="punctures count", null=True, blank=True, default=0)
    pr_count = models.PositiveIntegerField(verbose_name="pr count", null=True, blank=True)
    race = models.BooleanField(verbose_name="is race", default=False)
    flagged = models.BooleanField(verbose_name="flagged", default=False)
    commute = models.BooleanField(verbose_name="is commute", default=False)
    manual = models.BooleanField(verbose_name="is manual", default=False)
    has_heartrate = models.BooleanField(verbose_name="has heartrate", default=False)
    private = models.BooleanField(verbose_name="private", default=False)
    # may be removed?
    visibility = models.CharField(verbose_name="visibility", max_length=100, blank=True)
    # Strava does not enable to get related athletes, just the count. Therefore athletes has to be connected
    # manually with activity and the count of connected athletes and athlete count may differ
    athlete_count = models.PositiveSmallIntegerField(verbose_name="strava athletes count", null=True, blank=True)
    athletes = models.ManyToManyField("Athlete", verbose_name="athletes", related_name="activities", blank=True)
    tags = models.ManyToManyField("Tag", verbose_name="tags", related_name="activities", blank=True)

    def __str__(self):
        return f"{str.upper(self.TYPE.get_label(self.type))} -- {self.name} -- {self.tags_formatted}" if self.id else ""

    def __repr__(self):
        if self.id:
            return f"<<({self.start_date_formatted}) {str.upper(self.TYPE.get_label(self.type))} -- {self.name_short} -- {self.tags_formatted}({self.pk} - {self.strava_id})>>"
        else:
            return super().__repr__()

    @property
    def name_short(self):
        return self.name[:20]

    @property
    def start_date_formatted(self):
        return self.start.strftime("%d.%m.%y")

    @property
    def start_day_month(self):
        return self.start.strftime("%d.%m.")

    @property
    def distance_km(self):
        return round(self.distance / 1000, 1)

    @property
    def other_athletes_count(self):
        return self.athlete_count - 1

    @property
    def other_athletes_emoji(self):
        return " " + (self.athlete_count - 1) * f"👨" if self.athlete_count > 1 else ""

    @property
    def kudos_emoji(self):
        kudos_ceil = math.ceil(self.kudos_count / 10)
        return " " + kudos_ceil * "👍" + f" {self.kudos_count}" if kudos_ceil > 0 else ""

    @property
    def kudos_emoji_floor(self):
        kudos_floor = math.floor(self.kudos_count / 10)
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
            return ", ".join([f"#{tag}" for tag in self.tags.all().values_list("name", flat=True)])
        else:
            return ""

    @property
    def garmin_id(self):
        """The external_id of a garmin activity is in format `garmin_push_4676669572`"""
        try:
            external_id = self.external_id.split("_")
        except AttributeError:
            return
        if external_id[0] != "garmin" or len(external_id) != 3:
            return
        return external_id[-1]

    @property
    def strava_link(self):
        link = f"https://www.strava.com/activities/{self.strava_id}"
        print(link)
        return link

    @property
    def garmin_link(self):
        garmin_id = self.garmin_id
        if garmin_id:
            link = f"https://connect.garmin.com/activity/{garmin_id}"
            print(link)
            return link

    def refresh_from_strava(self):
        from utils.models import create_or_update_activity_from_strava

        logger.info(f"Refreshing activity {self.strava_id} from Strava")
        strava_activity = STRAVA_HELPER.client.get_activity(self.strava_id)
        create_or_update_activity_from_strava(strava_activity)
        self.refresh_from_db()

    def add_libka(self):
        self.gear.add(Gear.objects.get(name="libka"))

    def download_gpx_strava(self):
        STRAVA_HELPER.download_gpx(self.strava_id)

    def download_garmin_fit(self):
        garmin_id = self.garmin_id
        if not garmin_id:
            logger.warning(f"Requested to download not garmin activity. {self.strava_id}")
            return
        GARMIN_HELPER.download_activity(garmin_id)

    # def download_original(self):
    #     STRAVA_HELPER.download_activity(self.strava_id, self.name_short)

    class Meta:
        ordering = ("-start",)
        verbose_name = "activity"
        verbose_name_plural = "activities"


class Athlete(SmartModel):

    first_name = models.CharField(verbose_name="first name", max_length=50, null=False, blank=False)
    last_name = models.CharField(verbose_name="last name", max_length=50, null=True, blank=True)
    nickname = models.CharField(verbose_name="nickname", max_length=50, null=True, blank=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}" if not self.nickname else self.nickname

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "athlete"
        verbose_name_plural = "athletes"


class Gear(SmartModel):

    TYPE = ChoicesNumEnum(("SHOE", "Shoe", 1), ("BIKE", "Bike", 2), ("SKI", "Ski", 3), ("OTHER", "Other", 4))

    name = models.CharField(verbose_name="name", max_length=50, null=False, blank=False)
    type = models.PositiveSmallIntegerField(verbose_name="gear type", choices=TYPE.choices, null=False, blank=False)
    strava_id = models.CharField(verbose_name="strava ID", max_length=10, null=True, blank=True)
    active = models.BooleanField(verbose_name="active", null=False, blank=True, default=True)
    retired_at = models.DateTimeField(verbose_name="retired at", null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def distance_km(self) -> int:
        return round((self.activities.aggregate(Sum("distance"))["distance__sum"]) / 1000)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "gear"
        verbose_name_plural = "gears"


class Accessory(SmartModel):

    TYPE = ChoicesNumEnum(
        ("CHAIN", "chain", 1),
        ("TYRE", "tyre", 2),
        ("TUBE", "tube", 3),
        ("OTHER", "other", 4),
    )

    name = models.CharField(verbose_name="name", max_length=50, null=False, blank=False)
    description = models.TextField(verbose_name="description", null=True, blank=True)
    registered_at = models.DateTimeField(verbose_name="registered at", null=False, blank=False, default=datetime.now)
    deregistered_at = models.DateTimeField(verbose_name="deregistered at", null=True, blank=True)
    gear = models.ForeignKey(
        "Gear", verbose_name="gear", null=False, blank=False, on_delete=models.CASCADE, related_name="accessories"
    )
    is_active = models.BooleanField(verbose_name="is active", default=True)
    type = models.PositiveSmallIntegerField(verbose_name="type", choices=TYPE.choices, null=False, blank=False)

    def associate_activities(self) -> None:
        """Associate all activities with this accessory."""
        self.activities.add(*Activity.objects.filter(
            gear=self.gear,
            start__gte=self.registered_at,
            start__lte=self.deregistered_at if self.deregistered_at else datetime.now()
        ))

    @property
    def activities(self) -> QuerySet:
        """Return activities associated with this accessory."""
        return Activity.objects.filter(
            gear=self.gear,
            start__gte=self.registered_at,
            start__lte=self.deregistered_at if self.deregistered_at else datetime.now()
        )

    @property
    def distance_km(self) -> int:
        """Return total distance in km."""
        distance_m = self.activities.aggregate(Sum("distance"))["distance__sum"] or 0
        return round(distance_m / 1000)

    def __str__(self):
        return f"{self.name} ({self.gear})"

    def _post_save(self, changed, changed_fields, *args, **kwargs):
        if self.is_active and self.gear.accessories.filter(is_active=True, type=self.type).exclude(id=self.id).exists():
            raise ValidationError(f"Active accessory of type {self.type} already exists for {self.gear}")
        

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "accessory"
        verbose_name_plural = "accessories"


class Tag(SmartModel):

    name = models.SlugField(verbose_name="slug", max_length=30, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "tag"
        verbose_name_plural = "tags"

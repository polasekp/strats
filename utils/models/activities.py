from activities.models import Activity, Gear, Tag
from chamber.shortcuts import get_object_or_none
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import date


STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE = {
    'Run': Activity.TYPE.RUN,
    'Ride': Activity.TYPE.RIDE,
    'Hike': Activity.TYPE.HIKE,
    'NordicSki': Activity.TYPE.XC_SKI,
    'RollerSki': Activity.TYPE.ROLLER_SKI,
    'AlpineSki': Activity.TYPE.ALPINE_SKI,
    'Swim': Activity.TYPE.SWIM,
    'Walk': Activity.TYPE.WALK,
    'Workout': Activity.TYPE.WORKOUT,
    'Canoeing': Activity.TYPE.CANOEING,
    'RockClimbing': Activity.TYPE.CLIMBING,
    'IceSkate': Activity.TYPE.ICE_SKATE,
}


STRAVA_ACTIVITY_TYPE_TO_GEAR_TYPE = {
    'Ride': Gear.TYPE.BIKE,
    'Run': Gear.TYPE.SHOE,
    'Hike': Gear.TYPE.SHOE,
    'Walk': Gear.TYPE.SHOE,
}


TAG_NAMES = ["skate", "classic"]
TAG_NAME_TO_TAG = {}


def create_tags_if_needed():
    for tag_name in TAG_NAMES:
        tag = get_object_or_none(Tag, name=tag_name)
        if not tag:
            tag = Tag.objects.create(name=tag_name)
        TAG_NAME_TO_TAG[tag_name] = tag


def add_tag_to_activity_if_needed(activity):
    # teh input activity is the instance of Activity model
    for tag_name, tag in TAG_NAME_TO_TAG.items():
        if (activity.name + activity.description).find(f"#{tag_name}") != -1:
            activity.tags.add(tag)

    if date(2019, 12, 7) <= activity.start.date() <= date(2019, 12, 15):
        activity.tags.add(Tag.objects.get(name="MFF_misecky"))


def create_and_add_gear_to_activity_if_needed(activity, strava_client):
    if activity.gear_id:
        gear_created = False
        gear = get_object_or_none(Gear, strava_id=activity.gear_id)
        if not gear:
            strava_gear = strava_client.get_gear(activity.gear_id)
            gear = Gear.objects.create(
                strava_id=strava_gear.id,
                name=strava_gear.name,
                type=STRAVA_ACTIVITY_TYPE_TO_GEAR_TYPE[activity.type]
            )
            gear_created = True
        Activity.objects.get(strava_id=activity.id).gear.add(gear)
        return gear_created
    return False


def create_activity_from_strava(activity):
    try:
        activity = Activity.objects.create(
            name=activity.name,
            description=activity.description if activity.description else "",
            strava_id=activity.id,
            external_id=activity.external_id,
            distance=round(Decimal(activity.distance._num), 2),
            average_speed=round(Decimal(activity.average_speed._num), 2),
            max_speed=round(Decimal(activity.max_speed._num), 2),
            average_heartrate=round(Decimal(activity.average_heartrate), 1) if activity.average_heartrate else None,
            max_heartrate=activity.max_heartrate if activity.max_heartrate else None,
            calories=activity.calories,
            average_temp=activity.average_temp if activity.average_temp else None,
            start=activity.start_date,
            moving_time=activity.moving_time,
            elapsed_time=activity.elapsed_time,
            elevation_gain=activity.total_elevation_gain._num,
            type=STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE.get(activity.type, Activity.TYPE.OTHER),
            kudos_count=activity.kudos_count,
            photo_count=activity.total_photo_count,
            achievement_count=activity.achievement_count,
            comment_count=activity.comment_count,
            commute=activity.commute,
            athlete_count=activity.athlete_count,
            start_lat=round(Decimal(activity.start_latlng.lat), 6) if activity.start_latlng else None,
            start_lon=round(Decimal(activity.start_latlng.lon), 6) if activity.start_latlng else None,
            end_lat=round(Decimal(activity.end_latlng.lat), 6) if activity.end_latlng else None,
            end_lon=round(Decimal(activity.end_latlng.lon), 6) if activity.end_latlng else None,
            average_cadence=round(Decimal(activity.average_cadence), 1) if activity.average_cadence else None,
            flagged=activity.flagged,
            manual=activity.manual,
            visibility=getattr(activity, "visibility", ""),
            device_name=activity.device_name if activity.device_name else "",
            has_heartrate=activity.has_heartrate,
            pr_count=activity.pr_count,
        )
    except (IntegrityError, ValidationError) as e:
        print(f'Unable to import activity {activity.start_date} {activity.name}: {e}')
        return False
    return activity

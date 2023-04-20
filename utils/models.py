import json
from datetime import date
from decimal import Decimal

from chamber.shortcuts import get_object_or_none
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from activities.models import Activity, Gear, Tag

JSON_NAME = "strats_json"


STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE = {
    "Run": Activity.TYPE.RUN,
    "Ride": Activity.TYPE.RIDE,
    "VirtualRide": Activity.TYPE.VIRTUAL_RIDE,
    "VirtualRun": Activity.TYPE.VIRTUAL_RUN,
    "Hike": Activity.TYPE.HIKE,
    "NordicSki": Activity.TYPE.XC_SKI,
    "RollerSki": Activity.TYPE.ROLLER_SKI,
    "AlpineSki": Activity.TYPE.ALPINE_SKI,
    "Swim": Activity.TYPE.SWIM,
    "Walk": Activity.TYPE.WALK,
    "Workout": Activity.TYPE.WORKOUT,
    "Canoeing": Activity.TYPE.CANOEING,
    "RockClimbing": Activity.TYPE.CLIMBING,
    "IceSkate": Activity.TYPE.ICE_SKATE,
    "BackcountrySki": Activity.TYPE.BACKCOUNTRY_SKI,
}


STRAVA_ACTIVITY_TYPE_TO_GEAR_TYPE = {
    "Ride": Gear.TYPE.BIKE,
    "VirtualRide": Gear.TYPE.BIKE,
    "Run": Gear.TYPE.SHOE,
    "Hike": Gear.TYPE.SHOE,
    "Walk": Gear.TYPE.SHOE,
}


TAG_NAMES = ["skate", "classic"]
TAG_NAME_TO_TAG = {}


skate_tag = Tag.objects.get(name="skate")
classic_tag = Tag.objects.get(name="classic")
# tag activity name means how the tag is indicated in activity description / name
TAG_ACTIVITY_NAME_TO_TAG = {
    "skate": skate_tag,
    "ft": skate_tag,
    "classic": classic_tag,
    "cl": classic_tag,
}


def count_activity_punctures_from_description(description: str) -> int:
    desc_words = description.lower().split(" ")
    puncture = [word for word in desc_words if word.find("#puncture") != -1]
    if not puncture:
        return 0
    puncture = puncture[0]
    puncture_list = puncture.split("_")
    try:
        return int(puncture_list[1])
    except IndexError:
        return 1


def create_tags_if_needed():
    for tag_name in TAG_NAMES:
        tag = get_object_or_none(Tag, name=tag_name)
        if not tag:
            tag = Tag.objects.create(name=tag_name)
        TAG_NAME_TO_TAG[tag_name] = tag


def add_tag_to_activity_if_needed(activity: Activity):
    for tag_name, tag in TAG_ACTIVITY_NAME_TO_TAG.items():
        if (activity.name + activity.description).lower().find(f"#{tag_name}") != -1:
            activity.tags.add(tag)

    if date(2022, 12, 11) <= activity.start.date() <= date(2022, 12, 15):
        activity.tags.add(Tag.objects.get(name="MFF_misecky"))


def create_and_add_gear_to_activity_if_needed(activity, strava_client):
    if activity.gear_id:
        gear_created = False
        gear = get_object_or_none(Gear, strava_id=activity.gear_id)
        if not gear:
            strava_gear = strava_client.get_gear(activity.gear_id)
            gear = Gear.objects.create(
                strava_id=strava_gear.id, name=strava_gear.name, type=STRAVA_ACTIVITY_TYPE_TO_GEAR_TYPE[activity.type]
            )
            gear_created = True
        Activity.objects.get(strava_id=activity.id).gear.add(gear)
        return gear_created
    return False


def get_json_from_activity_description(description):
    json_start = description.find(JSON_NAME)
    if json_start != -1:
        json_start = json_start + len(JSON_NAME)
        json_start = description.find("{", json_start)
        json_end = description.find("}", json_start)
        json_substring = description[json_start : json_end + 1]
        return json.loads(json_substring)
    return None


def get_activity_num_field(activity, field, strats_json):
    if strats_json and strats_json.get(field):
        return strats_json.get(field)
    return getattr(activity, field)._num


def create_or_update_activity_from_strava(activity):
    # first check description if there are is json with corrected data
    description = activity.description or ""
    strats_json = None
    if description:
        strats_json = get_json_from_activity_description(description)

    try:
        activity_instance, created = Activity.objects.update_or_create(
            strava_id=activity.id,
            defaults={
                "name": activity.name,
                "description": description,
                "athlete_id": activity.athlete.id,
                "external_id": activity.external_id,
                "distance": round(Decimal(activity.distance._num), 2),
                "average_speed": round(Decimal(activity.average_speed._num), 2),
                "max_speed": round(Decimal(activity.max_speed._num), 2),
                "average_heartrate": round(Decimal(activity.average_heartrate), 1)
                if activity.average_heartrate
                else None,
                "max_heartrate": activity.max_heartrate if activity.max_heartrate else None,
                "calories": activity.calories,
                "average_temp": activity.average_temp if activity.average_temp else None,
                "start": activity.start_date,
                "moving_time": activity.moving_time,
                "elapsed_time": activity.elapsed_time,
                "elevation_gain": get_activity_num_field(activity, "total_elevation_gain", strats_json),
                "type": STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE.get(activity.type, Activity.TYPE.OTHER),
                "type_strava": activity.type,
                "kudos_count": activity.kudos_count,
                "photo_count": activity.total_photo_count,
                "achievement_count": activity.achievement_count,
                "comment_count": activity.comment_count,
                "punctures_count": count_activity_punctures_from_description(description),
                "commute": activity.commute,
                "athlete_count": activity.athlete_count,
                "start_lat": round(Decimal(activity.start_latlng.lat), 6) if activity.start_latlng else None,
                "start_lon": round(Decimal(activity.start_latlng.lon), 6) if activity.start_latlng else None,
                "end_lat": round(Decimal(activity.end_latlng.lat), 6) if activity.end_latlng else None,
                "end_lon": round(Decimal(activity.end_latlng.lon), 6) if activity.end_latlng else None,
                "average_cadence": round(Decimal(activity.average_cadence), 1) if activity.average_cadence else None,
                "average_power": int(activity.average_watts) if activity.average_watts else None,
                "max_power": int(activity.max_watts) if activity.max_watts else None,
                "weighted_average_power": int(activity.weighted_average_watts) if activity.weighted_average_watts else None,
                "has_power_meter": activity.device_watts if activity.device_watts else False,
                "kcal": int(activity.kilojoules) if activity.kilojoules else None,
                "suffer_score": int(activity.suffer_score) if activity.suffer_score else None,
                "flagged": activity.flagged,
                "manual": activity.manual,
                "visibility": getattr(activity, "visibility", ""),
                "private": activity.private,
                "device_name": activity.device_name if activity.device_name else "",
                "has_heartrate": activity.has_heartrate,
                "pr_count": activity.pr_count,
            },
        )
    except (IntegrityError, ValidationError) as e:
        print(f"Unable to import activity {activity.start_date} {activity.name}: {e}")
        return False
    return activity_instance

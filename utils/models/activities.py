from activities.models import Activity, Gear
from chamber.shortcuts import get_object_or_none
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


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
}


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
        Activity.objects.create(
            name=activity.name,
            strava_id=activity.id,
            distance=str(round(activity.distance._num, 2)),
            average_speed=str(round(activity.average_speed._num, 2)),
            start=activity.start_date,
            moving_time=activity.moving_time,
            elapsed_time=activity.elapsed_time,
            elevation_gain=activity.total_elevation_gain._num,
            type=STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE.get(activity.type, Activity.TYPE.OTHER),
            kudos=activity.kudos_count,
            achievements=activity.achievement_count,
            comments=activity.comment_count,
            commute=activity.commute,
            athlete_count=activity.athlete_count,
        )
    except (IntegrityError, ValidationError) as e:
        print(f'Unable to import activity {activity.start_date} {activity.name}: {e}')
        return False
    return True

from activities.models import Activity, Gear
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE = {
    'Run': 1,
    'Ride': 2,
    'Hike': 3,
    'NordicSki': 4,
    'RollerSki': 5,
    'AlpineSki': 6,
    'Swim': 7,
    'Walk': 8,
    'Workout': 9,
    'Canoeing': 10,
    'RockClimbing': 11,
    'IceSkate': 12,
}


def handle_exception(exception, activity):
    print(f'Unable to import activity {activity.start_date} {activity.name}: {exception}')


def create_activity_from_strava(activity):
    try:
        new_activity = Activity.objects.create(
            name=activity.name,
            strava_id=activity.id,
            distance=activity.distance._num,
            average_speed=activity.average_speed._num,
            start=activity.start_date,
            moving_time=activity.moving_time,
            elapsed_time=activity.elapsed_time,
            elevation_gain=activity.total_elevation_gain._num,
            sport=STRAVA_ACTIVITY_TYPE_TO_ACTIVITY_TYPE.get(activity.type, 13),  # default is set to Other
            kudos=activity.kudos_count,
            achievements=activity.achievement_count,
            comments=activity.comment_count,
            commute=activity.commute,
            athlete_count=activity.athlete_count,
        )
        # new_activity.gear.add(Gear.objects.get(strava_id=activity.gear_id))
    except IntegrityError as e:
        handle_exception(e, activity)
        return False
    except ValidationError as e:
        handle_exception(e, activity)
        return False
    return True

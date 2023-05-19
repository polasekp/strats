import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

from activities.models import Activity, Tag
from utils.models import (
    create_or_update_activity_from_strava,
    get_gear_by_strava_activity,
    add_tag_to_activity_if_needed,
    create_tags_if_needed,
)

from stravalib.model import Activity as StravaActivity
STRAVA_HELPER = settings.STRAVA_HELPER


def set_style_tags():
    cl_tag = Tag.objects.get(name="classic")
    ft_tag = Tag.objects.get(name="skate")

    # ac = Activity.objects.get(strava_id=2016811474)
    # ac.tags.add(cl_tag)

    # for activity in Activity.objects.filter(tags__name="MFF_misecky").exclude(tags__in=[ft_tag, cl_tag]):
    #     if activity.name.lower().find("zasypal jim") != -1:
    #         print(f"{activity.name}: {activity.strava_id}")
    # activity.tags.add(ft_tag)

    # for activity in Activity.objects.filter(tags__name="MFF_misecky").exclude(tags__in=[cl_tag, ft_tag]):
    #     if activity.name.lower().find("na rovinka") != -1:
    #         print(f"{activity.name}: {activity.strava_id}")
    #         activity.tags.add(cl_tag)


def refresh_mff_activities():
    mff_tag = Tag.objects.get(name="MFF_misecky")
    for activity in Activity.objects.filter(start__year=2019, tags__in=[mff_tag]):
        print(f"Refreshing activity ID {activity.strava_id}")
        activity_strava = STRAVA_HELPER.get_activity(activity.strava_id)
        # activity.pr_count = activity_strava.pr_count
        # activity.average_cadence = round(Decimal(activity_strava.average_cadence), 1) if activity_strava.average_cadence else None
        # activity.device_name = activity_strava.device_name if activity_strava.device_name else "",
        # activity.external_id = activity_strava.external_id
        # activity.flagged = activity_strava.flagged
        # activity.has_heartrate = activity_strava.has_heartrate
        # activity.manual = activity_strava.manual
        # activity.visibility = getattr(activity_strava, "visibility", "")
        activity.kudos_count = activity_strava.kudos_count
        activity.comment_count = activity_strava.comment_count
        activity.athlete_count = activity_strava.athlete_count
        activity.photo_count = activity_strava.total_photo_count
        activity.save()


def import_activities(before=None, after=None, limit=settings.DEFAULT_IMPORT_LIMIT, fast=True, perform_update=False):
    create_tags_if_needed()
    activities_count = 0

    activities = STRAVA_HELPER.get_activities(after=after, before=before, limit=limit)
    for e, strava_activity in enumerate(activities, start=1):
        if Activity.objects.filter(strava_id=strava_activity.id).exists() and not perform_update:
            continue
        else:
            print(f"Creating or updating activity ID {strava_activity.id}  ({e}/{limit})")
        # If not fast, lets get detailed information
        if not fast:
            strava_activity = STRAVA_HELPER.get_activity(strava_activity.id)
        created_activity = create_or_update_activity_from_strava(strava_activity)
        print(created_activity)
        activities_count += 1

        gear = get_gear_by_strava_activity(strava_activity, STRAVA_HELPER.client)
        if gear:
            created_activity.gear.add(gear)
        add_tag_to_activity_if_needed(created_activity)

    print(f"Successfully imported {activities_count} activities.")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--limit", type=str)
        parser.add_argument("--fast", default=False, type=bool)
        parser.add_argument("--perform_update", default=False, type=bool)

    def handle(self, **options):
        after = None
        before = None
        if Activity.objects.count() > 0:
            after = localtime(Activity.objects.first().start)
            # after = "2020-01-01"
            # after = datetime.datetime.now() - datetime.timedelta(weeks=10)
        else:
            before = datetime.datetime.now()

        limit = int(options["limit"]) if options["limit"] else settings.DEFAULT_IMPORT_LIMIT
        fast = options["fast"]
        perform_update = bool(options["perform_update"])

        print(f"Importing activities -- after: {after}, before: {before}, limit: {limit}, fast: {fast}, perform_update: {perform_update}")
        import_activities(after=after, before=before, limit=limit, fast=fast, perform_update=perform_update)

import datetime
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

from activities.models import Activity, Tag
from utils.models.activities import create_activity_from_strava, create_and_add_gear_to_activity_if_needed, \
    create_tags_if_needed, add_tag_to_activity_if_needed
from utils.stravalib import get_strava_client


client = get_strava_client()


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
        print(f"Updating activity ID {activity.strava_id}")
        activity_strava = client.get_activity(activity.strava_id)
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
        activity.save()


def import_activities(before=None, after=None, limit=settings.DEFAULT_DOWNLOAD_LIMIT, fast=True):
    create_tags_if_needed()
    activities_count = 0
    new_gear_count = 0
    activities = client.get_activities(after=after, before=before, limit=limit)
    for e, activity in enumerate(activities, start=1):
        if Activity.objects.filter(strava_id=activity.id).exists():
            continue
        # If not fast, lets get detailed information
        if not fast:
            activity = client.get_activity(activity.id)
        print(f"Creating activity ID {activity.id}   ({e}/{limit})")
        created_activity = create_activity_from_strava(activity)
        activities_count += 1
        if create_and_add_gear_to_activity_if_needed(activity, client):
            new_gear_count += 1
        add_tag_to_activity_if_needed(created_activity)

    print(f'Successfully imported {activities_count} activities.')
    print(f'Created {new_gear_count} new gear.')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--limit')
        parser.add_argument('--fast')

    def handle(self, **options):
        after = None
        before = None
        if Activity.objects.count() > 0:
            # before = (datetime.datetime.now() - datetime.timedelta(days=200))
            after = localtime(Activity.objects.first().start)
            # before = localtime(Activity.objects.last().start)
        else:
            # after = (datetime.datetime.now() - datetime.timedelta(days=2))
            before = datetime.datetime.now()

        limit = int(options["limit"]) if options["limit"] else settings.DEFAULT_DOWNLOAD_LIMIT
        if options["fast"] != "":
            if options["fast"].lower() in ["true", "1"]:
                fast = True
            else:
                fast = False
        else:
            fast = True

        # after = datetime.datetime(2019, 12, 10)
        # after = None
        # before = datetime.datetime(2014, 7, 20)
        # limit = 1000

        fast = False
        print(f"Importing activities -- after: {after}, before: {before}, limit: {limit}, fast: {fast}")
        import_activities(after=after, before=before, limit=limit, fast=fast)

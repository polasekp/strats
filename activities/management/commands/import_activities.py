import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

from activities.models import Activity
from utils.models.activities import create_activity_from_strava, create_and_add_gear_to_activity_if_needed, \
    create_tags_if_needed, add_tag_to_activity_if_needed
from utils.stravalib import get_strava_client


def import_activities(before=None, after=None, limit=settings.DEFAULT_DOWNLOAD_LIMIT, fast=True):
    create_tags_if_needed()
    client = get_strava_client()
    activities_count = 0
    new_gear_count = 0
    activities = client.get_activities(after=after, before=before, limit=limit)
    for e, activity in enumerate(activities, start=1):
        if Activity.objects.filter(start=activity.start_date).exists():
            continue
        # If not fast, lets get detailed information
        if not fast:
            activity = client.get_activity(activity.id)
        print(f"Creating activity ID {activity.id}...   ({e}/{limit})")
        # created_activity = create_activity_from_strava(activity_detail)
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
            # after = localtime(Activity.objects.first().start)
            before = localtime(Activity.objects.last().start)
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
        print(f"Importing activities -- after: {after}, before: {before}, limit: {limit}, fast: {fast}")

        after = datetime.datetime(2019, 12, 7)
        before = datetime.datetime(2019, 12, 23)
        import_activities(after=after, before=before, limit=limit, fast=fast)

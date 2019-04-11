from datetime import datetime

from activities.models import Activity
from django.core.management.base import BaseCommand
from utils.models.activities import create_activity_from_strava, create_and_add_gear_to_activity_if_needed
from utils.stravalib import create_strava_client


def import_all_activities():
    client = create_strava_client()
    activities_count = 0
    new_gear_count = 0
    for activity in client.get_activities(before=datetime.now()):
        if not Activity.objects.filter(start=activity.start_date).exists():
            if create_activity_from_strava(activity):
                activities_count += 1
            if create_and_add_gear_to_activity_if_needed(activity, client):
                new_gear_count += 1

    print(f'Successfully imported {activities_count} activities.')
    print(f'Created {new_gear_count} new gear.')


class Command(BaseCommand):

    def handle(self, **options):
        import_all_activities()

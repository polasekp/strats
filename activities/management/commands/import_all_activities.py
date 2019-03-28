from datetime import datetime

from django.core.management.base import BaseCommand

from activities.models import Activity
from utils.models.activities import create_activity_from_strava
from utils.stravalib import create_strava_client


def import_all_activities():
    client = create_strava_client()
    activities_count = 0
    for activity in client.get_activities(before=datetime.now()):
        if not Activity.objects.filter(start=activity.start_date).exists():
            if create_activity_from_strava(activity):
                activities_count += 1
    print(f'Successfully imported {activities_count} activities.')


class Command(BaseCommand):

    def handle(self, **options):
        import_all_activities()

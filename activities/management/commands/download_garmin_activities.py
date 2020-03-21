from django.core.management.base import BaseCommand

from activities.models import Activity
from utils.garmin import GarminHelper


class Command(BaseCommand):
    def handle(self, **options):
        activities = Activity.objects.filter(type=Activity.TYPE.RUN, start__year__gte=2018)
        garmin = GarminHelper()
        for activity in activities:
            activity.download_garmin_fit(garmin)

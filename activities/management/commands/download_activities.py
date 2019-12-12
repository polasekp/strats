import webbrowser

from django.core.management.base import BaseCommand

from activities.models import Activity


YEAR = 2019


class Command(BaseCommand):
    def handle(self, **options):
        for activity in Activity.objects.filter(start__year=YEAR, tags__name__contains="misecky"):
            webbrowser.open(f"https://www.strava.com/activities/{activity.strava_id}/export_gpx")

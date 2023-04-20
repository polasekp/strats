from datetime import datetime
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.db.models import Sum
from pytz import timezone
from tabulate import tabulate

from activities.models import Activity


class Command(BaseCommand):
    @property
    def today(self):
        today = date.today()
        return datetime(today.year, today.month, today.day, tzinfo=timezone("Europe/Berlin"))

    def add_arguments(self, parser):
        pass
        # parser.add_argument("--", default=settings.DEFAULT_IMPORT_LIMIT)

    def get_queryset_km_sum(self, queryset):
        distance_sum = queryset.aggregate(Sum("distance"))["distance__sum"]
        return round((distance_sum / 1000), 1) if distance_sum else 0

    def get_queryset_hours_sum(self, queryset):
        time_sum = queryset.aggregate(Sum("moving_time"))["moving_time__sum"]
        return round(time_sum.total_seconds() / 3600, 1) if time_sum else 0

    def get_queryset_elevation_sum(self, queryset):
        elevation_sum = queryset.aggregate(Sum("elevation_gain"))["elevation_gain__sum"]
        return round(elevation_sum / 1000, 1) if elevation_sum else 0

    # def get_formatted_line_for_queryset(self, queryset):
    #     km_sum = self.get_queryset_km_sum(queryset)
    #     white_space = " " * (8 - len(str(km_sum)))
    #
    #     time_seconds = self.get_queryset_time_sum_seconds(queryset)
    #     time_hours = round(time_seconds / 3600, 1)
    #
    #     return f"  {km_sum} km {white_space} |    {time_hours} h"

    def get_stats_row_values_for_queryset(self, queryset, activity_type) -> list:
        km = self.get_queryset_km_sum(queryset)
        hours = self.get_queryset_hours_sum(queryset)
        elevation = self.get_queryset_elevation_sum(queryset)
        return [Activity.TYPE_EMOJI.get(activity_type), km, hours, elevation]

    def stats_from_date(self, start_date, stats_name, activity_types, sum_only_selected=False):
        activities = Activity.objects.filter(start__gte=start_date)
        if sum_only_selected:
            activities = activities.filter(type__in=activity_types)

        print(stats_name)
        rows = []
        headers = ["km", "hours", "elevation [km]"]

        for activity_type in activity_types:
            activities_filtered = activities.filter(type=activity_type)
            rows.append(self.get_stats_row_values_for_queryset(activities_filtered, activity_type))

            if activity_type == Activity.TYPE.XC_SKI:
                classic = activities_filtered.filter(tags__name="classic")
                skate = activities_filtered.filter(tags__name="skate")
                rows.append(["⛸", self.get_queryset_km_sum(skate), self.get_queryset_hours_sum(skate)])
                rows.append(["🎿", self.get_queryset_km_sum(classic), self.get_queryset_hours_sum(classic)])


        if Activity.TYPE.RIDE in activity_types:
            activities_filtered = activities.filter(type__in=[Activity.TYPE.RIDE, Activity.TYPE.VIRTUAL_RIDE])
            km = self.get_queryset_km_sum(activities_filtered)
            hours = self.get_queryset_hours_sum(activities_filtered)
            elevation = self.get_queryset_elevation_sum(activities_filtered)
            rows.append(["bike sum", km, hours, elevation])

        rows.append([
            "SUM",
            self.get_queryset_km_sum(activities),
            self.get_queryset_hours_sum(activities),
            self.get_queryset_elevation_sum(activities),
        ])
        print(tabulate(rows, headers=headers, tablefmt="grid", numalign="right", floatfmt=".1f"))
        print()
        print()

    def week_stats(self):
        name = "LAST WEEK"
        activity_types = [
            Activity.TYPE.VIRTUAL_RIDE,
            Activity.TYPE.RIDE,
            Activity.TYPE.RUN,
        ]
        self.stats_from_date(self.today - timedelta(days=self.today.weekday()), name, activity_types)

    def year_stats(self):
        name = "LAST YEAR"
        activity_types = [
            Activity.TYPE.VIRTUAL_RIDE,
            Activity.TYPE.RIDE,
            Activity.TYPE.RUN,
            # Activity.TYPE.XC_SKI,
        ]
        self.stats_from_date(self.today.replace(month=1, day=1), name, activity_types)

    def season_stats(self):
        season_start_date = self.today.replace(year=self.today.year-1, month=10, day=1)
        # season_start_date = self.today.replace(month=1, day=1)
        season_start_date_formatted = season_start_date.strftime("%Y-%m-%d")
        name = f"SKIING SEASON (from {season_start_date_formatted})"
        activity_types = [Activity.TYPE.XC_SKI]
        self.stats_from_date(season_start_date, name, activity_types, True)

    def handle(self, **options):
        self.week_stats()
        self.year_stats()
        # self.season_stats()

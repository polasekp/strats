from decimal import Decimal

from django.db.models import Sum, Avg, Max
from django.http import HttpResponse
from django.views.generic import TemplateView

from activities.models import Activity, Tag


def index(request):
    return HttpResponse("Hello, world. You're at the activities index.")


def sum_distance(queryset):
    meters = queryset.aggregate(total_m=Sum("distance"))["total_m"]
    return round(meters / 1000) if meters else None


def sum_field(queryset, field):
    return queryset.aggregate(result=Sum(field))["result"]


def avg_field(queryset, field, decimal_places=1):
    result = queryset.aggregate(result=Avg(field))["result"]
    return round(result, decimal_places) if result else None


def max_field(queryset, field):
    return queryset.aggregate(result=Max(field))["result"]


class ActivitiesView(TemplateView):
    template_name = "activities.html"
    mff_tag = Tag.objects.get(name="MFF_misecky")
    queryset = Activity.objects.filter(tags__in=[mff_tag], type=Activity.TYPE.XC_SKI)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        years = [year for year in reversed(range(2013, 2020))]
        context["years"] = years
        context["activities"] = {}
        context["activities_stats"] = {}

        for year in years:
            year_activities = self.queryset.filter(start__year=year)
            total_km = sum_distance(year_activities)
            longest_activity = year_activities.order_by("-distance")[0]
            most_kudos_activity = year_activities.order_by("-kudos_count")[0]
            elapsed_time = sum_field(year_activities, "elapsed_time")
            moving_time = sum_field(year_activities, "moving_time")
            waiting_time = elapsed_time - moving_time
            avg_speed = round(total_km / Decimal(moving_time.total_seconds() / 3600), 1)

            context["activities_stats"][year] = [
                ("", "km", total_km),
                ("", "skate", sum_distance(year_activities.filter(tags__name="skate"))),
                ("", "klasika", sum_distance(year_activities.filter(tags__name="classic"))),
                ("", "čas", sum_field(year_activities, "moving_time")),
                ("", "elevation gain", sum_field(year_activities, "elevation_gain")),
                ("", "avg speed", avg_speed),
                ("", "km/aktivita", round(total_km / year_activities.count(), 1)),
                ("", "celkem fází", year_activities.count()),
                ("", "avg cadence", avg_field(year_activities, "average_cadence")),
                ("", "avg tep", avg_field(year_activities, "average_heartrate")),
                ("", "avg teplota", avg_field(year_activities, "average_temp")),
                ("strava_link", "nejdelší", (round(longest_activity.distance / 1000, 1), longest_activity.strava_id)),
                ("", "kudos", sum_field(year_activities, "kudos_count")),
                ("strava_link", "kudos max", (most_kudos_activity.kudos_count, most_kudos_activity.strava_id)),
                ("", "fotek", sum_field(year_activities, "photo_count")),
                ("", "proflákáno", waiting_time),
                ("", "proflákáno (%)", round(waiting_time / elapsed_time * 100)),
            ]

            context["activities"][year] = self.queryset.filter(start__year=year).order_by("start")
            context["dict"] = {"key": "test value"}
            context["column_names"] = [item[1] for item in context["activities_stats"][years[0]]]

        # last_day = datetime(2019, 12, 15).day
        # today = datetime.now().day
        # remaining_phases = last_day - today

        return context


class ZaznamView(TemplateView):
    template_name = "zaznam.html"

    # queryset = Activity.objects.filter(type__in=[Activity.TYPE.BACKCOUNTRY_SKI])
    queryset = Activity.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["points"] = []
        context["links"] = []

        for e, activity in enumerate(self.queryset):
            try:
                context["points"].append([float(activity.start_lon), float(activity.start_lat)])
                context["links"].append(f"{activity.strava_id} {activity.name} <a href={activity.strava_link}>strava link</a>")
            except Exception:
                continue
        return context

from decimal import Decimal

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.db.models import Sum, Avg, Max
from activities.models import Activity, Tag


def index(request):
    return HttpResponse("Hello, world. You're at the activities index.")


def sum_distance(queryset):
    meters = queryset.aggregate(total_m=Sum("distance"))["total_m"]
    return round(meters/1000)


def sum_field(queryset, field):
    return queryset.aggregate(result=Sum(field))["result"]


def avg_field(queryset, field, decimal_places=1):
    result = queryset.aggregate(result=Avg(field))["result"]
    return round(result, decimal_places) if result else None


def max_field(queryset, field):
    return queryset.aggregate(result=Max(field))["result"]


class ActivitiesView(TemplateView):
    template_name = 'activities.html'
    mff_tag = Tag.objects.get(name="MFF_misecky")
    queryset = Activity.objects.filter(tags__in=[mff_tag])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        years = reversed(range(2013, 2020))
        context["years"] = years
        context["col_names"] = [
            "km", "čas", "elevation gian", "avg km/h", "km/aktivita ", "celkem aktivit", "avg cadence",
            "avg tep", "avg teplota", "nejdelsi", "kudos", "nej kudos", "fotek"
        ]
        context['activities'] = {}
        context['activities_stats'] = {}

        for year in years:
            year_activities = self.queryset.filter(start__year=year)
            total_km = sum_distance(year_activities)
            longest_activity = year_activities.order_by("-distance")[0]
            most_kudos_activity = year_activities.order_by("-kudos_count")[0]

            context['activities_stats'][year] = {
                "total_km": total_km,
                "sum_hod": sum_field(year_activities, "moving_time"),
                "elevation_gain": sum_field(year_activities, "elevation_gain"),
                "avg_speed": round(avg_field(year_activities, "average_speed") * Decimal(3.6), 1),
                "avg_per_activity": round(total_km / year_activities.count(), 1),
                "activities_count": year_activities.count(),
                "avg_cadence": avg_field(year_activities, "average_cadence"),
                "avg_heartrate": avg_field(year_activities, "average_heartrate"),
                "avg_temperature": avg_field(year_activities, "average_temp"),
                "longest_distance": (round(longest_activity.distance/1000, 1), longest_activity.strava_id),
                "sum_kudos": sum_field(year_activities, "kudos_count"),
                "kudos_max": (most_kudos_activity.kudos_count, most_kudos_activity.strava_id),
                "sum_photos": sum_field(year_activities, "photo_count"),
            }

            context['activities'][year] = self.queryset.filter(start__year=year).order_by("start")

        return context

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.db.models.functions import Round
from .models import Accessory, Activity, Athlete, Gear, Tag


class ActivityAdmin(admin.ModelAdmin):
    def start_formatted(self, obj):
        return obj.start.strftime("%d %b %Y %H:%M")

    start_formatted.admin_order_field = 'start'
    start_formatted.short_description = 'start'

    def strava_link_admin(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.strava_link)
    strava_link_admin.allow_tags = True
    strava_link_admin.short_description = 'strava'

    def main_gear(self, obj):
        return obj.gear.first()
    main_gear.short_description = 'gear'

    list_filter = ("tags", "type", "gear")
    list_display = ('start_formatted', 'type',  'main_gear', 'name', 'distance_km', 'strava_link_admin')


class AccessoryAdmin(admin.ModelAdmin):
    # to set default filter (should enable to see only active accessories), check this link:
    # https://stackoverflow.com/a/16556771

    def registered_at_formatted(self, obj):
        return obj.registered_at.strftime("%d %b %Y")

    ordering = ('-registered_at',)

    registered_at_formatted.admin_order_field = 'registered_at'
    registered_at_formatted.short_description = 'registered_at'

    list_filter = ("is_active", "type", "gear")
    list_display = ('registered_at_formatted', 'type', 'name', 'distance_km', "is_active")


class GearAdmin(admin.ModelAdmin):
    list_filter = ("type", "active",)
    list_display = ('name', 'type', 'calculated_distance_km', 'active', 'retired_at')

    def calculated_distance_km(self, obj):
        return obj._distance_km

    calculated_distance_km.admin_order_field = '-_distance_km'
    calculated_distance_km.short_description = 'distance km'

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .annotate(
                _distance=Sum('activities__distance')
            ).annotate(
                _distance_km=Round(F('_distance') / 1000)
            )
        )

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(Gear, GearAdmin)
admin.site.register([Athlete, Tag])

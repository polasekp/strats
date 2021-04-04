from django.contrib import admin
from django.utils.html import format_html

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

    list_filter = ("tags", "type")
    list_display = ('start_formatted', 'type', 'name', 'distance_km', 'strava_link_admin')


admin.site.register(Activity, ActivityAdmin)
admin.site.register([Athlete, Gear, Accessory, Tag])

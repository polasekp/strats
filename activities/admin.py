from django.contrib import admin

from .models import Accessory, Activity, Athlete, Gear, Tag


admin.site.register([Activity, Athlete, Gear, Tag, Accessory])

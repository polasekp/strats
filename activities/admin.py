from django.contrib import admin

from .models import Activity, Athlete, Gear, Tag


admin.site.register([Activity, Athlete, Gear, Tag])

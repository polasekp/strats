from django.contrib import admin

from .models import Activity, Athlete, Gear


admin.site.register([Activity, Athlete, Gear])

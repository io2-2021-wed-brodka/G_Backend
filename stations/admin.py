from django.contrib import admin

from stations.models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    pass

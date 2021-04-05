from django.contrib import admin

from bikes.models import Bike


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    pass

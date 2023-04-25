import os

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["id", "mentor", "time_for_humans", "duration", "capacity","is_bookable", "is_canceled"]
    search_fields = ('id',)


class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "appointment", "attendee", "topic", "is_canceled"]
    search_fields = ('id',)


admin.site.register(User, UserAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Booking, BookingAdmin)

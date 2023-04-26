from django import template
from django.conf import settings
from django.utils import timezone

from apps.termintool.models import Booking

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
def day_name(day):
    return dict(settings.DAYS)[day]


@register.simple_tag
def has_booked(user, availability):
    if Booking.objects.filter(canceled=None,
                              appointment=availability,
                              attendee=user,
                              appointment_time__gt=timezone.localtime()).exists():
        return Booking.objects.get(canceled=None,
                                   appointment=availability,
                                   attendee=user,
                                   appointment_time__gt=timezone.localtime())
    return False

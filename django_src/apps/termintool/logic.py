from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone


def get_next_possible_date(availability):
    now = timezone.localtime()
    day_delta = (availability.start_time[0] - now.weekday()) % 7
    hour_delta = availability.start_time[1] - now.hour
    if day_delta == 0 and hour_delta <= 0:
        day_delta += 7
    delta = relativedelta(days=day_delta,
                          hours=hour_delta,
                          minute=0,
                          second=0,
                          microsecond=0)
    if (now + delta) - now < settings.MIN_BOOKING_THRESHOLD:
        delta.weeks += 1
    return now + delta


def cancel_availability(availibility):
    pass


def send_booking_notifications(booking):
    pass


def send_booking_cancel_notification(booking):
    pass


def send_availability_cancel_notification(availability):
    pass


def send_appointment_reminder(booking):
    pass

import math

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

from django.utils import timezone
from .fields import WeekdayTimeField
from django.conf import settings
from model_utils.models import TimeStampedModel


class User(AbstractUser):
    @property
    def is_tutor(self):
        return self.groups.filter(name=settings.MENTOR_GROUP_NAME).exists()


class Availability(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    start_time = WeekdayTimeField()
    duration = models.DurationField(default=datetime.timedelta(hours=1))
    preferred_location = models.CharField(max_length=50)
    # canceled is None by defauld, when it is not None the Appointment is Canceled and this fields shows when it was
    canceled = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.mentor} : {self.start_time}"

    def book(self, user, topic):
        next_date = self.get_next_possible_date()
        # Check if user has already booked this appointment
        Booking.objects.get_or_create(appointment=self,
                                      appointment_time=next_date,
                                      attendee=user,
                                      topic=topic
                                      )

    def get_next_possible_date(self):
        now = timezone.localtime()
        day_delta = (self.start_time[0] - now.weekday()) % 7
        hour_delta = self.start_time[1] - now.hour
        if day_delta == 0 and hour_delta <= 0:
            delta.weeks += 1
        delta = relativedelta(days=day_delta,
                              hours=hour_delta,
                              minute=0,
                              second=0,
                              microsecond=0)
        if (now + delta) - now < settings.MIN_BOOKING_THRESHOLD:
            delta.weeks += 1
        return now + delta

    @property
    def capacity(self):
        """A Appointment has a fiexed duration, defined in the settings. So a Availibility can be booked multible times.
        This funktion returns two values: how often this has been booked and how often it can be booked"""

        possible = math.floor(self.duration / settings.TIME_SLOT_DURATION)
        booked = self.booking_set.filter(appointment_time__gt=timezone.now()).count()
        return (possible - booked, possible)

    @property
    def is_bookable(self):
        return self.capacity[0] > 0 and self.canceled is not None

    @property
    def is_canceled(self):
        return self.canceled is not None

    def time_for_humans(self):
        return f"{dict(settings.DAYS)[self.start_time[0]]}  : {self.start_time[1]} O'Clock"

    @classmethod
    def get_availability_for(cls, mentor):
        return cls.objects.filter(mentor=mentor, canceled=None).order_by("id")


class Booking(TimeStampedModel):
    appointment = models.ForeignKey(Availability, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    attendee = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(default="", max_length=100)
    canceled = models.DateTimeField(null=True, blank=True, default=None)

    @property
    def is_canceled(self):
        return self.canceled is not None

import math

from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

from django.utils import timezone
from .fields import WeekdayTimeField
from django.conf import settings
from model_utils.models import TimeStampedModel

from .logic import get_next_possible_date, send_booking_cancel_notification


class User(AbstractUser):
    @property
    def is_tutor(self):
        return self.groups.filter(name=settings.MENTOR_GROUP_NAME).exists()


class Availability(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    day = models.IntegerField(choices=settings.DAYS)
    hour = models.IntegerField(choices=[(i, '{0:02d}:00'.format(i)) for i in range(24)])
    duration = models.DurationField(default=datetime.timedelta(hours=1))
    preferred_location = models.CharField(max_length=50)
    # canceled is None by defauld, when it is not None the Appointment is Canceled and this fields shows when it was
    canceled = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.mentor} : {self.time_for_humans()}"

    def book(self, user, topic):
        # Check if user has already booked this appointment
        if Booking.objects.filter(appointment=self,
                                  appointment_time__gt=timezone.localtime(),
                                  attendee=user,
                                  topic=topic,
                                  canceled=None
                                  ).exists():
            return False
        next_timeslot = self.get_next_timeslot()
        Booking.objects.create(appointment=self,
                               appointment_time=next_timeslot,
                               attendee=user,
                               topic=topic
                               )
        return True

    def get_next_timeslot(self):
        next_date = get_next_possible_date(self)
        booked, possible = self.capacity
        return next_date + (possible-booked) * settings.TIME_SLOT_DURATION

    @property
    def capacity(self):
        """An Appointment has a fixed duration, defined in the settings. So an Availability can be booked multiple times.
        This funktion returns two values: how often this has been booked and how often it can be booked"""

        possible = math.floor(self.duration / settings.TIME_SLOT_DURATION)
        booked = self.booking_set.filter(appointment_time__gt=timezone.localtime(),
                                         canceled=None).count()
        return possible - booked, possible

    @property
    def is_bookable(self):
        return self.capacity[0] > 0 and self.canceled is None

    @property
    def is_canceled(self):
        return self.canceled is not None

    def time_for_humans(self):
        return f"{self.get_day_display()} : {self.get_hour_display()}"

    @classmethod
    def get_availability_for(cls, mentor):
        return cls.objects.filter(mentor=mentor, canceled=None).order_by("id")


class Booking(TimeStampedModel):
    appointment = models.ForeignKey(Availability, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    attendee = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(default="", max_length=100)
    canceled = models.DateTimeField(null=True, blank=True, default=None)

    def cancel(self):
        self.canceled = timezone.localtime()
        send_booking_cancel_notification(self)
        self.save()

    @property
    def is_canceled(self):
        return self.canceled is not None

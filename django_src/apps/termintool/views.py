import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import *


@login_required
def index(request):
    mentors = User.objects.filter(groups__name=settings.MENTOR_GROUP_NAME)
    context = {"availabilitys": []}
    for mentor in mentors:
        context["availabilitys"].append((mentor, Availability.get_availability_for(mentor)))

    return render(request, "index.html", context)


@login_required
def create_booking(request):
    if request.method == "POST":
        post_json = json.loads(request.body.decode('utf-8'))

        # Does the post request have correct content?
        if "availability_id" not in post_json:
            return HttpResponse("Avalability id not providet", status=400)
        if "topic" not in post_json:
            return HttpResponse("Topic id not providet", status=400)
        # Does this availability even exist?
        try:
            availability = Availability.objects.get(id=post_json['availability_id'])
        except Availability.DoesNotExist:
            return HttpResponse("Availability does not exist",status=404)
        # Does this availability still have free time slots?
        if not availability.is_bookable:
            return HttpResponse("No free time slots", status=410)
        # Does this booking already exist?
        if not availability.book(request.user, post_json['topic']):
            return HttpResponse("Appointment already booked", status=406)
        return HttpResponse(f"Booked Appointment with {availability.mentor.full_name}", status=200)
    return HttpResponse("Only open for post requests", status=405)


@login_required
def cancel_booking(request):
    if request.method == "POST":
        post_json = json.loads(request.body.decode('utf-8'))

        # Does the post request have correct content?
        if "availability_id" not in post_json:
            return HttpResponse("Availability id not providet", status=400)
        # Does this availability even exist?
        try:
            availability = Availability.objects.get(id=post_json['availability_id'])
        except Availability.DoesNotExist:
            return HttpResponse("Availability does not exist", status=404)
        # Does a booking from this user exist?
        if not Booking.objects.filter(attendee=request.user,
                                      appointment_time__gt=timezone.localtime(),
                                      appointment=availability,
                                      canceled=None).exists():
            return HttpResponse("Booking does not exist", status=404)

        booking = Booking.objects.get(attendee=request.user,
                            appointment_time__gt=timezone.localtime(),
                            appointment=availability,
                            canceled=None)
        booking.cancel()
        return HttpResponse(f"Appointment with {booking.appointment.mentor.full_name} canceled", status=200)
    return HttpResponse("Only open for post requests", status=400)

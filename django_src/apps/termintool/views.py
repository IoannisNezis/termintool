import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import *


@login_required
def index(request):
    mentors = User.objects.filter(groups__name=settings.MENTOR_GROUP_NAME)
    context = {"availabilitys": []}
    for mentor in mentors:
        context["availabilitys"].append((f"{mentor.first_name} {mentor.last_name}", Availability.get_availability_for(mentor)))

    return render(request, "index.html", context)


@login_required
def create_booking(request):
    if request.method == "POST":
        post_json = json.loads(request.body.decode('utf-8'))

        # Does the post request have correct content?
        if "availability_id" not in post_json:
            return HttpResponse("avalability id not providet", status=400)
        if "topic" not in post_json:
            return HttpResponse("avalability id not providet", status=400)
        # Does this availability even exist?
        try:
            availability = Availability.objects.get(id=post_json['availability_id'])
        except Availability.DoesNotExist:
            return HttpResponse(status=404)
        # Does this availability still have free time slots?
        if not availability.is_bookable:
            return HttpResponse("No free time slots", status=400)

        if availability.book(request.user, post_json['topic']):
            return HttpResponse(status=200)
        else:
            return HttpResponse("Already booked", status=400)
        return HttpResponse(status=200)
    return HttpResponse("Only open for post requests", status=400)


@login_required
def cancel_booking(request):
    if request.method == "POST":
        post_json = json.loads(request.body.decode('utf-8'))

        # Does the post request have correct content?
        if "availability_id" not in post_json:
            return HttpResponse("avalability id not providet", status=400)
        # Does this availability even exist?
        try:
            availability = Availability.objects.get(id=post_json['availability_id'])
        except Availability.DoesNotExist:
            return HttpResponse(status=404)
        # Does a booking from this user exist?
        if not Booking.objects.filter(attendee=request.user,
                                      appointment_time__gt=timezone.localtime(),
                                      appointment=availability,
                                      canceled=None).exists():
            return HttpResponse("No such booking found", status=400)

        Booking.objects.get(attendee=request.user,
                            appointment_time__gt=timezone.localtime(),
                            appointment=availability,
                            canceled=None).cancel()

        return HttpResponse(status=200)
    return HttpResponse("Only open for post requests", status=400)

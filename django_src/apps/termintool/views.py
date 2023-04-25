import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import *


@login_required
def index(request):
    mentors = User.objects.filter(groups__name=settings.MENTOR_GROUP_NAME)
    context={}
    context["availabilitys"] = []
    for mentor in mentors:
        context["availabilitys"].append((mentor, Availability.get_availability_for(mentor)))

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
            return HttpResponse("No free time slots",status=400)

        availability.book(request.user, post_json['topic'])
        return HttpResponse(status=200)

    return HttpResponse("Only open for post requests", status=400)

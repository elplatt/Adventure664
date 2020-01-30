from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from .models import Activity

def room(request, room_id=None):
    activities = Activity.objects.order_by('created_at')
    context = {
       'activities': activities
    }
    return render(request, 'explore/room.html', context)


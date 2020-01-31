from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from .models import Activity
from .forms import CommandForm

@login_required
def room(request, room_id=None):

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            # Create a new activity
            activity = Activity(activity_text=form.cleaned_data['command_text'])
            activity.save()

    # Get a list of activities
    activities = Activity.objects.order_by('created_at')
    context = {
       'activities': activities,
       'command_form': CommandForm()
    }

    # Render the template
    return render(request, 'explore/room.html', context)


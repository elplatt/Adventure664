from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse

from .models import Activity, Area
from .forms import CommandForm, SelectAreaForm, AreaForm

@login_required
def index(request):

    # If data has been posted, redirect to room
    if request.method == 'POST':
        try:
            area = Area.objects.get(title=request.POST['area_title'])
        except ObjectDoesNotExist:
            area = Area(title=request.POST['area_title'], creator=request.user)
            area.save()
        return HttpResponseRedirect(reverse('explore:area', kwargs={'area_id': area.id}))

    context = {
        'select_area_form': SelectAreaForm,
    }
    return render(request, 'explore/index.html', context)

@login_required
def area(request, area_id):

    # Get area object
    area = get_object_or_404(Area, id=area_id)

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            # Create a new activity
            activity_text = f'{request.user.username}: {form.cleaned_data["command_text"]}'
            activity = Activity(
                creator=request.user,
                area=area,
                activity_text=activity_text)
            activity.save()

    # Get a list of activities
    activities = Activity.objects.filter(area=area).order_by('created_at')

    # Build context and render the template
    context = {
       'area': area,
       'activities': activities,
       'command_form': CommandForm(label_suffix='')
    }
    return render(request, 'explore/room.html', context)

@login_required
def area_description(request, area_id):

    # Look up area object
    area = get_object_or_404(Area, id=area_id)

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = AreaForm(request.POST)
        if form.is_valid():
            area.description = request.POST.get('description', '')
            area.save()

    # Render edit form
    context = {
        'area': area,
        'area_form': AreaForm(initial={'description': area.description}),
    }
    return render(request, 'explore/area_detail.html', context)

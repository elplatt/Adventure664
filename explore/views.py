from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.urls import reverse

from .models import Activity, Area, Connection, News
from player.models import Player

from .forms import (
        AreaForm,
        CommandForm,
        ConnectionForm,
        DeleteForm,
        SelectAreaForm,
)
from .interpreter import Interpreter

def index(request):

    # Get lobby area
    try:
        lobby = Area.objects.get(title="Lobby")
    except ObjectDoesNotExist:
        lobby = Area(title="Lobby")
        lobby.save()

    # Check if user has a current location
    try:
        player = request.user.player
        location = player.location
        if location != lobby:
            return redirect('explore:area', area_id=location.id)
    except AttributeError:
        pass

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            # Create the interpreter
            i = Interpreter(
                {'user': request.user, 'area': lobby},
                request,
            )
            path = i.execute(form.cleaned_data["command_text"])
            if path is not None:
                return HttpResponseRedirect(path)

    # Get a list of activities
    if request.user.is_authenticated:
        for_user = Q(creator_only=False) | Q(creator=request.user)
    else:
        for_user = Q(creator_only=False)
    activities = Activity.objects.filter(area=lobby).filter(for_user).order_by('-created_at')

    # Construct context variables and render template
    top_users = User.objects.exclude(username='admin').order_by('-score__total')[:5]
    players = lobby.player_set.all()
    if request.user.is_authenticated:
        players = players.exclude(user=request.user)
    context = {
        'user': request.user,
        'area': lobby,
        'areas': Area.objects.filter(published=True).order_by('-created_at'),
        'players': players,
        'activities': activities,
        'items': lobby.item_set.all(),
        'top_users': top_users,
        'news': News.objects.order_by('created_at').last(),
        'command_form': CommandForm(label_suffix=''),
    }
    return render(request, 'explore/index.html', context)

def lobby(request):

    # Get lobby area
    try:
        lobby = Area.objects.get(title="Lobby")
    except ObjectDoesNotExist:
        lobby = Area(title="Lobby")
        lobby.save()

    # Set player's current location to lobby
    try:
        player = request.user.player
        player.location = lobby
        player.save()
    except AttributeError:
        pass

    return redirect('explore:index')

def area(request, area_id):

    # Get area object
    area = get_object_or_404(Area, id=area_id)
    if request.user.is_authenticated:
        # Clear activities from other areas
        Activity.tidy(request.user, area)
        # Update player location
        request.user.player.location = area
        request.user.player.save()

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            # Create the interpreter
            i = Interpreter({'user': request.user, 'area': area}, request)
            path = i.execute(form.cleaned_data["command_text"])
            if path is not None:
                return HttpResponseRedirect(path)

    # Get a list of activities
    if request.user.is_authenticated:
        for_user = Q(creator_only=False) | Q(creator=request.user)
    else:
        for_user = Q(creator_only=False)
    activities = Activity.objects.filter(area=area).filter(for_user).order_by('-created_at')

    # Build context and render the template
    players = area.player_set.all()
    if request.user.is_authenticated:
        players = players.exclude(user=request.user)
    context = {
       'user': request.user,
       'area': area,
       'activities': activities,
       'players': players,
       'items': area.item_set.all(),
       'subtitle': area.title,
       'command_form': CommandForm(label_suffix='')
    }
    return render(request, 'explore/room.html', context)

@login_required
def create_area(request, area_title=''):

    # Look up area object
    try:
        area = Area.objects.get(title__iexact=area_title.strip())
        messages.add_message(request, messages.ERROR, f'Area "{area_title}" already exists.')
        if request.POST['next']:
            url = request.POST['next']
        elif request.GET['next']:
            url = request.GET['next']
        else:
            url = request.path
        return HttpResponseRedirect(url)
    except ObjectDoesNotExist:
        pass

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = AreaForm(request.POST)
        if form.is_valid():
            new_title = request.POST.get('title', '').strip()
            new_description = request.POST.get('description' '').strip()
            area = Area(title=new_title, description=new_description, creator=request.user)
            area.save()
            url = request.POST.get('next', reverse('explore:area', args=[area.id]))
            return HttpResponseRedirect(url)

    # Render edit form
    initial =  {
        'title': area_title,
    }
    context = {
        'area_form': AreaForm(initial=initial),
        'user': request.user,
    }
    return render(request, 'explore/area_detail.html', context)

@login_required
def edit_area(request, area_id):

    # Look up area object
    area = get_object_or_404(Area, id=area_id)

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = AreaForm(request.POST)
        if form.is_valid():
            new_title = request.POST.get('title', '').strip()
            # Check whether title is already taken
            other_area = Area.objects.filter(title__iexact=new_title).exclude(id=area_id).count()
            if other_area == 0:
                area.title = new_title
            else:
                messages.add_message(request, messages.ERROR, f'Couldn\'t change area name, "{new_title}" already exists.') 
            area.description = request.POST.get('description', '')
            area.save()
            # Update scores
            if area.creator and request.user.id != area.creator.id:
                score = area.creator.score
                score.total += 10
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_id]))

    # Render edit form
    initial =  {
        'description': area.description,
        'title': area.title,
    }
    context = {
        'area': area,
        'area_form': AreaForm(initial=initial),
        'user': request.user,
    }
    return render(request, 'explore/area_detail.html', context)

@login_required
def new_connection(request, source_id, title):

    # Look up source area object
    area_from = get_object_or_404(Area, id=source_id)

    # Check whether connection exists
    try:
        connection = Connection.objects.get(area_from=area_from, title=title)
        messages.add_message(request, messages.ERROR, f'Unable to create connection "{title}": already exists')
        if request.GET['next']:
            url = request.GET['next']
        else:
            url = reverse('explore:area', args=[area_from.id])
        return HttpResponseRedirect(url)
    except ObjectDoesNotExist:
        pass

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = ConnectionForm(request.POST)
        if form.is_valid():
            area_to, created = Area.objects.get_or_create(
                title=form.cleaned_data['destination_title'],
                defaults={ 'creator': request.user })
            connection, created = Connection.objects.get_or_create(
                title=title,
                area_from=area_from,
                defaults={ 'area_to': area_to, 'creator': request.user }
            )
            if created:
                connection.save()
                # Update scores
                if area_from.creator and area_from.creator != request.user:
                    score = area_from.creator.score
                    score.total += 10
                    score.save()
                if area_to.creator and area_to.creator != request.user:
                    score = area_to.creator.score
                    score.total += 10
                    score.save()
            if request.POST['next']:
                url = request.POST['next']
            else:
                url = reverse('explore:area', args=[area_from.id])
            return HttpResponseRedirect(url)

    # Render edit form
    context = {
        'title': title,
        'area_from': area_from,
        'connection_form': ConnectionForm(),
        'user': request.user,
    }
    return render(request, 'explore/connection_detail.html', context)

@login_required
def delete_connection(request, source_id, title):

    # Look up source area object and connection
    area_from = get_object_or_404(Area, id=source_id)
    
    # Check whether connection exists
    try:
        connection = Connection.objects.get(area_from=area_from, title=title)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, f'Unable to delete connection "{title}": does not exist')
        if request.GET['next']:
            url = request.GET['next']
        else:
            url = reverse('explore:area', args=[area_from.id])
        return HttpResponseRedirect(url)

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = DeleteForm(request.POST)
        if form.is_valid():
            area_to = connection.area_to
            connection.delete()
            # Update scores
            if area_from.creator and area_from.creator != request.user:
                score = area_from.creator.score
                score.total += 5
                score.save()
            if area_to.creator and area_to.creator != request.user:
                score = area_to.creator.score
                score.total += 5
                score.save()
            if request.POST['next']:
                url = request.POST['next']
            else:
                url = reverse('explore:area', args=[area_from.id])
            return HttpResponseRedirect(url)

    # Render delete form
    context = {
        'type': 'Connection',
        'title': f'{area_from.title} : {connection.title} : {connection.area_to}',
        'form': DeleteForm(),
        'user': request.user,
    }
    return render(request, 'explore/delete.html', context)

@login_required
def delete_activity(request, area_id, activity_id):

    # Look up area object and activity
    area = get_object_or_404(Area, id=area_id)
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = DeleteForm(request.POST)
        if form.is_valid():
            activity.delete()
            if request.POST['next']:
                url = request.POST['next']
            else:
                url = reverse('explore:area', args=[area.id])
            return HttpResponseRedirect(url)

    # Render delete form
    context = {
        'type': 'Activity',
        'title': f'{activity.activity_text}',
        'form': DeleteForm(),
        'user': request.user,
    }
    return render(request, 'explore/delete.html', context)

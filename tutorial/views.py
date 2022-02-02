from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from explore.models import Area, Connection
from explore.forms import AreaForm, CommandForm, ConnectionForm

# Create your views here.

tutorial_templates = [
    "area",
    "area",
    "connection",
    "area",
    "edit_area",
    "area",
]

tutorial_titles = [
    "Another White Room",
    "Another White Room",
    "",
    "",
    "",
    "",
]

tutorial_descriptions = [
"""\
After you walk through the door, it disappears behind you. You'll have to create a new one.

Type "create connection <name>" but replace "<name>" with a name like "north".
""",
"""\
There's a door again! Type the name of the connection to go through it.
""",
"",
"""\
A brand new room! But it needs a description.

Type "edit area" to add a description.
""",
"",
"",
]

def index (request):

    # Get area object
    area = Area(
        title="Beginning Your Adventure",
        description="""\
You are in a plain white room. You look around and a door appears on the north wall.

Type "north" to go through the door.
""")

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["command_text"] == "north":
                return HttpResponseRedirect(reverse("tutorial:tutorial", args=[0]))
        messages.add_message(request, messages.INFO, "Huh? I don't understand.")


    # Build context and render the template
    context = {
       'user': request.user,
       'area': area,
       'activities': [],
       'players': [],
       'items': [],
       'subtitle': area.title,
       'command_form': CommandForm(label_suffix=''),
       'show_how_to_play': False,
       'connections': ["north"],
    }
    return render(request, 'explore/room.html', context)

def tutorial (request, tutorial_stage):
    if tutorial_templates[tutorial_stage] == "area" or tutorial_templates[tutorial_stage] == "edit_area":
        # Get area object
        area = Area(
            title=tutorial_titles[tutorial_stage],
            description=tutorial_descriptions[tutorial_stage])

    # Set up data structures and session
    if tutorial_stage == 0:
        request.session["connections"] = []
    elif tutorial_stage == 2:
        area_from = Area(title=tutorial_titles[1])
        connection = Connection(
            title=request.session["connections"][0],
            area_from=area_from)
    elif tutorial_stage == 3:
        area.title = request.session["title"]
        request.session["connections"] = []
    elif tutorial_stage == 4:
        area.title = request.session["title"]
        area.description = "";
    elif tutorial_stage == 5:
        area.title = request.session["title"]
        area.description = request.session["description"]

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        if tutorial_stage in [0, 1, 3]:
            form = CommandForm(request.POST)
            if form.is_valid():
                if tutorial_stage == 0:
                    if form.cleaned_data["command_text"].startswith("create connection"):
                        c = form.cleaned_data["command_text"][18:]
                        request.session["connections"] = [c]
                        return HttpResponseRedirect(reverse("tutorial:tutorial", args=[1]))
                    else:
                        messages.add_message(request, messages.INFO, "Huh? I don't understand.")
                elif tutorial_stage == 1:
                    if form.cleaned_data["command_text"] == request.session.get("connections")[0]:
                        return HttpResponseRedirect(reverse("tutorial:tutorial", args=[2]))
                    else:
                        messages.add_message(request, messages.INFO, "Huh? I don't understand.")
                elif tutorial_stage == 3:
                    if form.cleaned_data["command_text"] == "edit area":
                        return HttpResponseRedirect(reverse("tutorial:tutorial", args=[4]))
                    else:
                        messages.add_message(request, messages.INFO, "Huh? I don't understand.")                    
        elif tutorial_stage in [2]:
            form = ConnectionForm(request.POST)
            if form.is_valid():
                request.session["title"] = form.cleaned_data["destination_title"]
                return HttpResponseRedirect(reverse("tutorial:tutorial", args=[3]))
        elif tutorial_stage in [4]:
            form = AreaForm(request.POST)
            if form.is_valid():
                request.session["description"] = form.cleaned_data["description"]
                return HttpResponseRedirect(reverse("tutorial:tutorial", args=[5]))


    # Build context and render the template
    if tutorial_templates[tutorial_stage] == "area":
        context = {
           'user': request.user,
           'area': area,
           'activities': [],
           'players': [],
           'items': [],
           'subtitle': area.title,
           'command_form': CommandForm(label_suffix=''),
           'show_how_to_play': False,
           'connections': request.session.get("connections", []),
        }
        return render(request, 'explore/room.html', context)
    elif tutorial_templates[tutorial_stage] == "edit_area":
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
    elif tutorial_templates[tutorial_stage] == "connection":
        context = {
            'title': connection.title,
            'area_from': connection.area_from,
            'connection_form': ConnectionForm(),
            'user': request.user,
            'messages': ["Where should this door take you? Enter any name for the destination."]
        }
        return render(request, 'explore/connection_detail.html', context)


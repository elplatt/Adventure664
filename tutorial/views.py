from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from explore.models import Area, Connection
from explore.forms import CommandForm

# Create your views here.

tutorial_titles = [
	"Another White Room",
]

tutorial_descriptions = [
"""\
After you walk through the door, it disappears behind you. You'll have to create a new one.

Type "create connection <name>" but replace "<name>" with a name like "north".
""",
]

def index (request):

    # Get area object
    area = Area(
    	title="Tutorial Start",
    	description="""\
You are in a plain white room. After you look around, a door appears on the north wall.

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

    # Get area object
    area = Area(
    	title=tutorial_titles[tutorial_stage],
    	description=tutorial_descriptions[tutorial_stage])

    # Initialize a fake connection list
    connections = []

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
        	if tutorial_stage == 0:
	        	if form.cleaned_data["command_text"].startswith("create connection"):
	        		c = form.cleaned_data["command_text"][18:]
	        		connections.append(c)
	        	else:
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
       'connections': connections,
    }
    return render(request, 'explore/room.html', context)


from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse

from explore.forms import DeleteForm
from explore.models import Area

from .forms import ItemForm
from .models import Item

@login_required
def create(request, area_id):

    # Get area
    area = get_object_or_404(Area, id=area_id)

    # Check for submitted data
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            title = request.POST.get('item_title', '')
            item = Item(
                title = title,
                short_description = request.POST.get('short_description', ''),
                long_description = request.POST.get('long_description', ''),
                location = area,
                creator = request.user,
            )
            item.save()
            messages.add_message(request, messages.INFO, f'Created item "{title}".')
            # Update scores
            if area.creator and area.creator != request.user:
                score = area.creator.score
                score.total += 10
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_id]))

    form = ItemForm()
    return render(request, 'item/item_detail.html', { 'title': 'Create Item', 'form': form })

@login_required
def delete(request, item_id):

    # Look up item and item location
    item = get_object_or_404(Item, id=item_id)
    area = item.location
    title = item.title
    
    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = DeleteForm(request.POST)
        if form.is_valid():
            item.delete()
            messages.add_message(request, messages.INFO, f'Item "{title}" deleted.')
            # Update scores
            if area.creator.id != request.user.id:
                score = area.creator.score
                score.total += 1
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area.id]))

    # Render delete form
    context = {
        'type': 'Item',
        'title': f'{item.title}',
        'form': DeleteForm(),
        'user': request.user,
    }
    return render(request, 'explore/delete.html', context)

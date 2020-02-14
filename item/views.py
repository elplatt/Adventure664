from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse

from explore.models import Area

from .forms import ItemForm
from .models import Item

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
            if area.creator != request.user:
                score = area.creator.score
                score.total += 10
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_id]))

    form = ItemForm()
    return render(request, 'item/item_detail.html', { 'title': 'Create Item', 'form': form })

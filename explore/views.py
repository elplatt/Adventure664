from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.template import loader

def index(request):
    context = {
    }
    return HttpResponse('Hello, world!')
#    return render(request, 'polls/index.html', context)


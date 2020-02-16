from django.contrib.auth.models import User
from django.shortcuts import render


# Create your views here.

def all(request):
    return render(request, 'player/all.html', { 'user_list': User.objects.order_by('username') })
    

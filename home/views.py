from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, label_suffix='')
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            url = request.POST.get('next', reverse('explore:index'))
            return HttpResponseRedirect(url)
    else:
        form = UserCreationForm(label_suffix='')
    return render(request, 'registration/register.html', {'form': form})

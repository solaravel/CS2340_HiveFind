from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import JobSeeker


def signup(request):
    if request.user.is_authenticated:
        return redirect('home.index')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home.index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('home.index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home.index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout(request):
    auth_logout(request)
    return redirect('home.index')


def view_profile(request, id):
    profile = get_object_or_404(JobSeeker, id=id)
    template_data = {}
    template_data['title'] = profile.name
    template_data['headline'] = profile.headline
    template_data['skills'] = profile.skills.all()
    template_data['education'] = profile.education
    return render(request, 'accounts/view_profile.html', {'template_data': template_data})

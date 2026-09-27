from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .forms import JobSeekerForm
from .models import JobSeeker, Skill


def signup(request):
    if request.user.is_authenticated:
        return redirect('home.index')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = JobSeeker.objects.create(user=user)
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

@login_required
def my_profile(request):
    profile = get_object_or_404(JobSeeker, user=request.user)
    return redirect('accounts.view_profile', id=profile.id)


def view_profile(request, id):
    profile = get_object_or_404(JobSeeker, id=id)
    template_data = {}
    template_data['title'] = profile.name
    template_data['headline'] = profile.headline
    template_data['skills'] = profile.skills.all()
    template_data['education'] = profile.education
    template_data['work_exp'] = profile.work_exp
    template_data['links'] = profile.links
    return render(request, 'accounts/view_profile.html', {'template_data': template_data})


@login_required
def edit_profile(request):
    profile = get_object_or_404(JobSeeker, user=request.user)
    if request.method == 'POST':
        form = JobSeekerForm(request.POST, instance=profile)
        if form.is_valid():
            jobseeker = form.save()
            new_skills_raw = form.cleaned_data.get('new_skills', '')
            if new_skills_raw:
                skill_names = []
                for s in new_skills_raw.split(','):
                    stripped = s.strip()
                    if stripped:
                        skill_names.append(stripped)
                for name in skill_names:
                    skill_obj, created = Skill.objects.get_or_create(name__iexact=name, defaults={'name': name})
                    jobseeker.skills.add(skill_obj)
            return redirect('accounts.view_profile', id=profile.id)
    else:
        form = JobSeekerForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


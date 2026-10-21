from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.core.exceptions import PermissionDenied #throws error if job seeker tries to access candidates page
from .forms import JobSeekerForm, SignUpForm
from .models import JobSeeker, Skill


def signup(request):
    if request.user.is_authenticated:
        return redirect('home.index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data['role'] == 'recruiter':
                group, _ = Group.objects.get_or_create(name='Recruiters')
                group.permissions.add(Permission.objects.get(codename='add_job'))
                user.groups.add(group)
            else:
                seeker_group, _ = Group.objects.get_or_create(name='Seeker')
                user.groups.add(seeker_group)
                JobSeeker.objects.create(user=user)
            auth_login(request, user)
            return redirect('home.index')
    else:
        form = SignUpForm()
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
    profile, _ = JobSeeker.objects.get_or_create(
        user=request.user, defaults={'name': request.user.username},
    )
    return redirect('accounts.view_profile', id=profile.id)


def view_profile(request, id):
    profile = get_object_or_404(JobSeeker, id=id)
    can_view = profile.is_public or profile.user == request.user
    template_data = {}
    template_data['title'] = profile.name
    template_data['headline'] = profile.headline
    template_data['skills'] = profile.skills.all()
    template_data['education'] = profile.education
    template_data['work_exp'] = profile.work_exp
    template_data['links'] = profile.links
    template_data['profile_user'] = profile.user
    template_data['can_view'] = can_view
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

@login_required
def candidate_search(request):
    if not request.user.groups.filter(name="Recruiters").exists():
        raise PermissionDenied
    name = request.GET.get('name', '')
    skill = request.GET.get('skill', '')
    education = request.GET.get('education', '')
    experience = request.GET.get('experience', '')
    candidates = JobSeeker.objects.filter(user__groups__name='Seeker', is_public=True)
    if name:
        candidates = candidates.filter(Q(name__icontains=name) | Q(headline__icontains=name))
    if skill:
        candidates = candidates.filter(skills__name__icontains=skill)
    if education:
        candidates = candidates.filter(education__icontains=education)
    if experience:
        candidates = candidates.filter(work_exp__icontains=experience)
    template_data = {}
    template_data['title'] = 'Search Candidates'
    template_data['candidates'] = candidates.distinct().prefetch_related('skills')
    template_data['filters'] = request.GET
    return render(
        request, 'accounts/search.html', {'template_data': template_data})
        
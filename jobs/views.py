from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count

from .forms import JobForm, ReportForm
from .models import Job, Report
from applications.models import Application
from accounts.models import CandidateMatchNotification, JobSeeker, SavedCandidateSearch




def job_map(request):
    return render(request, 'jobs/map.html')


def jobs_api(request):
    jobs = Job.objects.filter(is_active=True).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return JsonResponse({'jobs': [job.as_dict() for job in jobs]})

def index(request):
    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = Job.objects.filter(is_active=True)
    template_data['recommendations'] = Job.objects.none()
    if request.user.is_authenticated:
        profile = JobSeeker.objects.filter(user=request.user).first()
        if profile:
            template_data['recommendations'] = Job.objects.filter(
                is_active=True,
                skills__in=profile.skills.all(),
            ).exclude(applications__user=request.user).distinct()
    return render(request, 'jobs/index.html', {'template_data': template_data})
def show(request, id):
    job = get_object_or_404(Job, id=id, is_active=True)
    template_data = {}
    template_data['title'] = job.title
    template_data['job'] = job
    return render(request, 'jobs/show.html', {'template_data': template_data})

@login_required
@permission_required('jobs.add_job', raise_exception=True)
def create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            form.save_m2m()
            return redirect('jobs.show', id=job.id)
    else:
        form = JobForm()
    return render(request, 'jobs/create.html', {'form': form})

def job_search(request):
    jobs = Job.objects.filter(is_active=True)
    title = request.GET.get('title', '')
    skill = request.GET.get('skill', '')
    location = request.GET.get('location', '')
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    job_type = request.GET.get('job_type', '')
    visa = request.GET.get('visa', '')

    if title:
        jobs = jobs.filter(Q(title__icontains=title) | Q(company__icontains=title))
    if skill:
        jobs = jobs.filter(skills__name__icontains=skill)
    if location:
        jobs = jobs.filter(Q(city__icontains=location) | Q(state__icontains=location) | Q(address__icontains=location))
    if salary_min:
        jobs = jobs.filter(salary_max__gte=salary_min)
    if salary_max:
        jobs = jobs.filter(salary_min__lte=salary_max)
    if job_type == 'remote':
        jobs = jobs.filter(is_remote=True)
    elif job_type == 'onsite':
        jobs = jobs.filter(is_remote=False)
    if visa == 'yes':
        jobs = jobs.filter(visa_sponsorship=True)

    template_data = {}
    template_data['title'] = 'Search Jobs'
    template_data['jobs'] = jobs.distinct()
    template_data['filters'] = request.GET
    return render(request, 'jobs/search.html', {'template_data': template_data})


@login_required
@permission_required('jobs.add_job', raise_exception=True)
def candidate_search(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            SavedCandidateSearch.objects.get_or_create(user=request.user, query=query)
            messages.success(request, 'Candidate search saved.')
            return redirect('jobs.candidates')
        messages.error(request, 'Enter a search term to save a candidate search.')

    query = request.GET.get('query', '').strip()
    candidates = JobSeeker.objects.none()
    if query:
        candidates = JobSeeker.objects.filter(
            Q(name__icontains=query) | Q(headline__icontains=query) | Q(skills__name__icontains=query)
        ).distinct()
    template_data = {
        'query': query,
        'candidates': candidates,
        'saved_searches': SavedCandidateSearch.objects.filter(user=request.user).annotate(
            match_count=Count('notifications')
        ),
        'notifications': CandidateMatchNotification.objects.filter(search__user=request.user).select_related(
            'candidate', 'search'
        ),
    }
    return render(request, 'jobs/candidates.html', {'template_data': template_data})
@login_required
def create_application(request, id):
    if request.method == 'POST' and request.POST['note'] != '':
        job = get_object_or_404(Job, id=id, is_active=True)
        application = Application()
        application.note = request.POST['note']
        application.job = job
        application.user = request.user
        application.save()
        return redirect('jobs.show', id=id)
    else:
        return redirect('jobs.show', id=id)


@login_required
def report_posting(request, id):
    posting = get_object_or_404(Job, pk=id)
    report = Report(reporter=request.user, reported_posting=posting)

    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Your report ticket has been submitted and our moderators will review it shortly. Thanks for your patience!")
            return redirect('jobs.show', id=id)
    else:
        form = ReportForm(instance=report)
    return render(request, "jobs/report_form.html", {"form": form, "target": posting})

@login_required
def report_user(request, id):
    User = get_user_model()
    reported_user = get_object_or_404(User, pk=id)
    profile = get_object_or_404(JobSeeker, user=reported_user)
    report = Report(reporter=request.user, reported_user=reported_user)
    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Your report ticket has been submitted and our moderators will review it shortly. Thanks for your patience!")
            return redirect('accounts.view_profile', id=profile.id)
    else:
        form = ReportForm(instance=report)
    return render(request, "jobs/report_form.html", {"form": form, "target": reported_user})
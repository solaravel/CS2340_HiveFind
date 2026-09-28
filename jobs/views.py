from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from .forms import JobForm
from .models import Job
from applications.models import Application


def job_map(request):
    return render(request, 'jobs/map.html')


def jobs_api(request):
    jobs = Job.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return JsonResponse({'jobs': [job.as_dict() for job in jobs]})

def index(request):
    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = Job.objects.all()
    return render(request, 'jobs/index.html', {'template_data': template_data})
def show(request, id):
    job = Job.objects.get(id=id)
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
    jobs = Job.objects.all()
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
def create_application(request, id):
    if request.method == 'POST' and request.POST['note'] != '':
        job = Job.objects.get(id=id)
        application = Application()
        application.note = request.POST['note']
        application.job = job
        application.user = request.user
        application.save()
        return redirect('jobs.show', id=id)
    else:
        return redirect('jobs.show', id=id)
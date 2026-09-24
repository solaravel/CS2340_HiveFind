from django.http import JsonResponse
from django.shortcuts import render

from .models import Job


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
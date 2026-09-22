from django.http import JsonResponse
from django.shortcuts import render

from .models import Job


def job_map(request):
    return render(request, 'jobs/map.html')


def jobs_api(request):
    jobs = Job.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return JsonResponse({'jobs': [job.as_dict() for job in jobs]})

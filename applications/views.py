from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from jobs.models import Job
from .models import Application


@login_required
def index(request):
    applications = Application.objects.filter(user=request.user)
    template_data = {}
    template_data['title'] = 'My Applications'
    template_data['applications'] = applications
    template_data['stages'] = Application.STATUS_CHOICES
    return render(request, 'applications/index.html', {'template_data': template_data})


@login_required
@require_POST
def apply(request, id):
    job = get_object_or_404(Job, id=id)
    Application.objects.get_or_create(user=request.user, job=job)
    return redirect('applications.index')

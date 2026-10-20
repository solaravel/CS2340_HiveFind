from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from jobs.models import Job
from .models import Application
from accounts.models import JobSeeker

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


@login_required
@permission_required('jobs.add_job', raise_exception=True)
def pipeline(request):
    applications = Application.objects.filter(job__posted_by=request.user).select_related('user', 'job')
    return render(request, 'applications/pipeline.html', {
        'stages': [
            {
                'value': value,
                'label': label,
                'applications': applications.filter(status=value),
                'choices': Application.STATUS_CHOICES,
            }
            for value, label in Application.STATUS_CHOICES
        ],
    })


@login_required
@permission_required('jobs.add_job', raise_exception=True)
@require_POST
def update_status(request, id):
    application = get_object_or_404(Application, id=id, job__posted_by=request.user)
    status = request.POST.get('status')
    if status not in dict(Application.STATUS_CHOICES):
        messages.error(request, 'Choose a valid application stage.')
    else:
        application.status = status
        application.save(update_fields=['status'])
    return redirect('applications.pipeline')

@login_required
@permission_required('jobs.add_job', raise_exception=True)
def view_app(request, id):
    application = get_object_or_404(Application.objects.select_related('user', 'job'), id=id, job__posted_by=request.user,)
    candidate = (JobSeeker.objects.filter(user=application.user).prefetch_related('skills').first())
    template_data = {}
    template_data['title'] = f'{application.user.username} - {application.job.title}'
    template_data['application'] = application
    template_data['candidate'] = candidate
    template_data['stages'] = Application.STATUS_CHOICES
    template_data['note'] = application.note
    return render(request, 'applications/view_app.html', {'template_data': template_data})
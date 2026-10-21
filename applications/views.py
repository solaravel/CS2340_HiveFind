from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.core.mail import send_mail
from jobs.models import Job
from .models import Application
from accounts.models import JobSeeker

STAGE_ORDER = ['applied', 'review', 'interview', 'offer', 'closed']

@login_required
def index(request):
    applications = Application.objects.filter(user=request.user)
    labels = dict(Application.STATUS_CHOICES)
    items = []
    for app in applications:
        current = STAGE_ORDER.index(app.status) if app.status in STAGE_ORDER else 0
        stages = []
        for i, key in enumerate(STAGE_ORDER):
            state = 'done' if i < current else ('active' if i == current else 'todo')
            stages.append({'label': labels.get(key, key.title()), 'state': state})
        progress = int(current / (len(STAGE_ORDER) - 1) * 100)
        items.append({'app': app, 'stages': stages, 'progress': progress,
                      'current_label': labels.get(app.status, app.status)})
    template_data = {}
    template_data['title'] = 'My Applications'
    template_data['applications'] = items
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


@login_required
@permission_required('jobs.add_job', raise_exception=True)
@require_POST
def email_candidate(request, id):
    application = get_object_or_404(
        Application.objects.select_related('user', 'job'), id=id, job__posted_by=request.user,
    )
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    recipient = application.user.email
    if not subject or not message:
        messages.error(request, 'Enter a subject and a message.')
    elif not recipient:
        messages.error(request, 'This candidate has no email on file.')
    else:
        send_mail(subject, message, None, [recipient])
        messages.success(request, f'Email sent to {recipient}.')
    return redirect('applications.view_app', id=application.id)


@login_required
@permission_required('jobs.add_job', raise_exception=True)
def applicant_map(request):
    return render(request, 'applications/applicant_map.html')


@login_required
@permission_required('jobs.add_job', raise_exception=True)
def applicant_map_data(request):
    applications = Application.objects.filter(job__posted_by=request.user).select_related('user', 'job')
    profiles = {
        js.user_id: js
        for js in JobSeeker.objects.filter(user__in=[a.user_id for a in applications])
    }
    points = []
    for application in applications:
        profile = profiles.get(application.user_id)
        if profile and profile.latitude is not None and profile.longitude is not None:
            points.append({
                'name': profile.name or application.user.username,
                'lat': profile.latitude,
                'lng': profile.longitude,
                'job': application.job.title,
            })
    return JsonResponse({'applicants': points})
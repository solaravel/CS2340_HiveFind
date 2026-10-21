from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse
from accounts.models import JobSeeker
from jobs.models import Job
from .models import Application


class ApplicationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'x', 'pass1234')
        self.job = Job.objects.create(title='Dev', company='Acme', latitude=33.7, longitude=-84.3)

        add_job = Permission.objects.get(codename='add_job')
        self.recruiter = User.objects.create_user('recruiter_a', password='pass1234')
        self.recruiter.user_permissions.add(add_job)
        self.other_recruiter = User.objects.create_user('recruiter_b', password='pass1234')
        self.other_recruiter.user_permissions.add(add_job)

        seeker_user = User.objects.create_user('seeker', 'seeker@example.com', 'pass1234')
        self.job_seeker = JobSeeker.objects.create(
            user=seeker_user, name='Jordan Seeker', education='Georgia Tech, BS CS',
        )
        self.recruiter_job = Job.objects.create(
            title='Backend Engineer', company='Acme', latitude=33.7, longitude=-84.3,
            posted_by=self.recruiter,
        )
        self.application = Application.objects.create(user=seeker_user, job=self.recruiter_job)

    def test_apply_creates_application(self):
        self.client.login(username='tester', password='pass1234')
        self.client.post(f'/applications/{self.job.id}/apply')
        self.assertEqual(Application.objects.filter(user=self.user, job=self.job).count(), 1)

    def test_index_requires_login(self):
        response = self.client.get('/applications/')
        self.assertEqual(response.status_code, 302)

    def test_recruiter_can_update_application_stage(self):
        self.job.posted_by = self.recruiter
        self.job.save()
        application = Application.objects.create(user=self.user, job=self.job)
        self.client.force_login(self.recruiter)

        response = self.client.post(
            reverse('applications.update_status', args=[application.id]),
            {'status': 'interview'},
        )

        application.refresh_from_db()
        self.assertRedirects(response, reverse('applications.pipeline'))
        self.assertEqual(application.status, 'interview')

    def test_recruiter_pipeline_only_shows_own_applicants(self):
        self.job.posted_by = self.recruiter
        self.job.save()
        Application.objects.create(user=self.user, job=self.job)
        self.client.force_login(self.recruiter)

        response = self.client.get(reverse('applications.pipeline'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tester')

    def test_applicant_cannot_update_application_stage(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('applications.update_status', args=[self.application.id]),
            {'status': 'interview'},
        )
        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_view_candidate_and_application(self):
        self.client.force_login(self.recruiter)
        resp = self.client.get(reverse('applications.view_app', args=[self.application.id]))
        self.assertContains(resp, self.job_seeker.name)
        self.assertContains(resp, self.job_seeker.education)
        self.assertContains(resp, self.application.job.title)

    def test_other_recruiter_gets_404(self):
        self.client.force_login(self.other_recruiter)
        resp = self.client.get(reverse('applications.view_app', args=[self.application.id]))
        self.assertEqual(resp.status_code, 404)

    def test_job_seeker_gets_403(self):
        self.client.force_login(self.job_seeker.user)
        resp = self.client.get(reverse('applications.view_app', args=[self.application.id]))
        self.assertEqual(resp.status_code, 403)

    def test_recruiter_can_email_candidate(self):
        self.client.force_login(self.recruiter)
        response = self.client.post(
            reverse('applications.email_candidate', args=[self.application.id]),
            {'subject': 'Interview invite', 'message': 'Please schedule a call.'},
        )
        self.assertRedirects(response, reverse('applications.view_app', args=[self.application.id]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['seeker@example.com'])

    def test_email_candidate_requires_ownership(self):
        self.client.force_login(self.other_recruiter)
        response = self.client.post(
            reverse('applications.email_candidate', args=[self.application.id]),
            {'subject': 'Hi', 'message': 'Hello'},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(mail.outbox), 0)

    def test_applicant_map_data_returns_located_applicants(self):
        self.job_seeker.latitude = 33.77
        self.job_seeker.longitude = -84.39
        self.job_seeker.save()
        self.client.force_login(self.recruiter)
        response = self.client.get(reverse('applications.applicant_map_data'))
        data = response.json()
        self.assertEqual(len(data['applicants']), 1)
        self.assertEqual(data['applicants'][0]['name'], 'Jordan Seeker')

    def test_applicant_map_requires_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('applications.applicant_map'))
        self.assertEqual(response.status_code, 403)

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.urls import reverse
from accounts.models import JobSeeker
from jobs.models import Job
from .models import Application


class ApplicationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'x', 'pass1234')
        self.job = Job.objects.create(title='Dev', company='Acme', latitude=33.7, longitude=-84.3)

    def test_apply_creates_application(self):
        self.client.login(username='tester', password='pass1234')
        self.client.post(f'/applications/{self.job.id}/apply')
        self.assertEqual(Application.objects.filter(user=self.user, job=self.job).count(), 1)

    def test_index_requires_login(self):
        response = self.client.get('/applications/')
        self.assertEqual(response.status_code, 302)

    def test_recruiter_can_update_application_stage(self):
        recruiter = User.objects.create_user('recruiter', password='pass1234')
        recruiter.user_permissions.add(Permission.objects.get(codename='add_job'))
        self.job.posted_by = recruiter
        self.job.save()
        application = Application.objects.create(user=self.user, job=self.job)
        self.client.force_login(recruiter)

        response = self.client.post(
            reverse('applications.update_status', args=[application.id]),
            {'status': 'interview'},
        )

        application.refresh_from_db()
        self.assertRedirects(response, reverse('applications.pipeline'))
        self.assertEqual(application.status, 'interview')

    def test_recruiter_pipeline_only_shows_own_applicants(self):
        recruiter = User.objects.create_user('recruiter', password='pass1234')
        recruiter.user_permissions.add(Permission.objects.get(codename='add_job'))
        self.job.posted_by = recruiter
        self.job.save()
        Application.objects.create(user=self.user, job=self.job)
        self.client.force_login(recruiter)

        response = self.client.get(reverse('applications.pipeline'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tester')

    def test_applicant_cannot_update_application_stage(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('applications.update_status', args=[1]),
            {'status': 'interview'},
        )
        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_view_candidate_and_application(self):
        self.client.force_login(self.recruiter)
        resp = self.client.get(reverse('applications.detail', args=[self.application.id]))
        self.assertContains(resp, self.job_seeker.name)
        self.assertContains(resp, self.job_seeker.education)
        self.assertContains(resp, self.application.job.title)

    def test_other_recruiter_gets_404(self):
        self.client.force_login(self.other_recruiter)
        resp = self.client.get(reverse('applications.detail', args=[self.application.id]))
        self.assertEqual(resp.status_code, 404)

    def test_job_seeker_gets_403(self):
        self.client.force_login(self.job_seeker.user)
        resp = self.client.get(reverse('applications.detail', args=[self.application.id]))
        self.assertEqual(resp.status_code, 403)

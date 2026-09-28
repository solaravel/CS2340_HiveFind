from django.test import TestCase
from django.contrib.auth.models import User
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

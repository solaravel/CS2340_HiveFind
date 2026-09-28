from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission, User

from .models import Job


class JobMapTests(TestCase):
    def setUp(self):
        Job.objects.create(
            title='Software Engineer',
            company='Acme',
            latitude=33.7756,
            longitude=-84.3963,
            city='Atlanta',
            state='GA',
        )

    def test_map_page_loads(self):
        response = self.client.get(reverse('jobs.map'))
        self.assertEqual(response.status_code, 200)

    def test_api_returns_jobs(self):
        response = self.client.get(reverse('jobs.api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['jobs']), 1)
        self.assertEqual(data['jobs'][0]['title'], 'Software Engineer')
        self.assertIn('latitude', data['jobs'][0])

    def test_job_creation_requires_login(self):
        response = self.client.get(reverse('jobs.create'))
        self.assertEqual(response.status_code, 302)

    def test_job_creation_requires_permission(self):
        user = User.objects.create_user(username='applicant', password='pass1234')
        self.client.force_login(user)
        response = self.client.get(reverse('jobs.create'))
        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_create_job(self):
        user = User.objects.create_user(username='recruiter', password='pass1234')
        permission = Permission.objects.get(codename='add_job')
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.post(reverse('jobs.create'), {
            'title': 'Product Designer',
            'company': 'Acme',
            'description': 'Design product experiences.',
            'city': 'Atlanta',
            'state': 'GA',
            'latitude': '33.7756',
            'longitude': '-84.3963',
            'salary_min': '80000',
            'salary_max': '110000',
            'is_remote': 'on',
            'visa_sponsorship': 'on',
        })

        job = Job.objects.get(title='Product Designer')
        self.assertRedirects(response, reverse('jobs.show', args=[job.id]))
        self.assertEqual(job.posted_by, user)

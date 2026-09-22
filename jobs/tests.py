from django.test import TestCase
from django.urls import reverse

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

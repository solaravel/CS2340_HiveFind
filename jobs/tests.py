from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission, User
from accounts.models import JobSeeker, SavedCandidateSearch, Skill

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

    def test_jobs_page_recommends_matching_skills(self):
        user = User.objects.create_user(username='applicant', password='pass1234')
        profile = JobSeeker.objects.create(user=user, name='Applicant')
        skill = Skill.objects.create(name='Python')
        profile.skills.add(skill)
        job = Job.objects.create(
            title='Python Developer',
            company='Acme',
            latitude=33.7,
            longitude=-84.3,
        )
        job.skills.add(skill)
        self.client.force_login(user)

        response = self.client.get(reverse('jobs.index'))

        self.assertContains(response, 'Recommended for You')
        self.assertContains(response, job.title)
        self.assertIn(job, response.context['template_data']['recommendations'])

    def test_saved_candidate_search_shows_matching_candidates(self):
        recruiter = User.objects.create_user(username='recruiter', password='pass1234')
        recruiter.user_permissions.add(Permission.objects.get(codename='add_job'))
        self.client.force_login(recruiter)
        self.client.post(reverse('jobs.candidates'), {'query': 'Python'})
        search = SavedCandidateSearch.objects.get(user=recruiter, query='Python')
        candidate_user = User.objects.create_user(username='candidate', password='pass1234')
        candidate = JobSeeker.objects.create(user=candidate_user, name='Candidate')

        candidate.skills.add(Skill.objects.create(name='Python'))

        response = self.client.get(reverse('jobs.candidates'))
        self.assertContains(response, search.query)
        self.assertContains(response, 'Candidate')

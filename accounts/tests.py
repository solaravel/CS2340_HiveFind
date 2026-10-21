from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import JobSeeker


class ProfilePrivacyTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='pass1234')
        self.profile = JobSeeker.objects.create(
            user=self.owner, name='Private Pat', education='Georgia Tech', is_public=False,
        )
        self.viewer = User.objects.create_user('viewer', password='pass1234')

    def test_private_profile_hidden_from_others(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('accounts.view_profile', args=[self.profile.id]))
        self.assertContains(response, 'This profile is private')
        self.assertNotContains(response, 'Georgia Tech')

    def test_owner_can_view_own_private_profile(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('accounts.view_profile', args=[self.profile.id]))
        self.assertContains(response, 'Georgia Tech')


class SignupRoleTests(TestCase):
    def test_recruiter_signup_gets_job_permission(self):
        response = self.client.post(reverse('accounts.signup'), {
            'username': 'rec_new', 'password1': 'BuzzyBee!2340',
            'password2': 'BuzzyBee!2340', 'role': 'recruiter',
        })
        self.assertRedirects(response, reverse('home.index'))
        user = User.objects.get(username='rec_new')
        self.assertTrue(user.has_perm('jobs.add_job'))
        self.assertFalse(JobSeeker.objects.filter(user=user).exists())
        self.assertEqual(self.client.get(reverse('jobs.create')).status_code, 200)

    def test_seeker_signup_creates_profile_without_permission(self):
        response = self.client.post(reverse('accounts.signup'), {
            'username': 'seeker_new', 'password1': 'BuzzyBee!2340',
            'password2': 'BuzzyBee!2340', 'role': 'seeker',
        })
        self.assertRedirects(response, reverse('home.index'))
        user = User.objects.get(username='seeker_new')
        self.assertTrue(JobSeeker.objects.filter(user=user).exists())
        self.assertFalse(user.has_perm('jobs.add_job'))

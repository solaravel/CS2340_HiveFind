import random

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import JobSeeker, Skill
from applications.models import Application
from jobs.models import Job

PASSWORD = 'hivedemo123'
PREFIX = 'demo_'

SKILLS = [
    'Python', 'Django', 'Flask', 'JavaScript', 'TypeScript', 'React', 'Vue',
    'Node.js', 'SQL', 'PostgreSQL', 'Java', 'Spring', 'Go', 'Rust', 'C++',
    'Swift', 'Kotlin', 'AWS', 'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch',
    'Pandas', 'GraphQL', 'HTML/CSS', 'Figma', 'Linux', 'Selenium', 'Git',
]

# (city, state, lat, lng) around metro Atlanta; longitudes are negative (USA).
LOCATIONS = [
    ('Atlanta', 'GA', 33.7772, -84.3894),
    ('Atlanta', 'GA', 33.7859, -84.3830),
    ('Atlanta', 'GA', 33.7590, -84.3874),
    ('Atlanta', 'GA', 33.7490, -84.3880),
    ('Buckhead', 'GA', 33.8484, -84.3630),
    ('Decatur', 'GA', 33.7748, -84.2963),
    ('Sandy Springs', 'GA', 33.9304, -84.3733),
    ('Marietta', 'GA', 33.9526, -84.5499),
    ('Alpharetta', 'GA', 34.0754, -84.2941),
    ('Smyrna', 'GA', 33.8840, -84.5144),
    ('Roswell', 'GA', 34.0232, -84.3616),
    ('Duluth', 'GA', 34.0029, -84.1446),
    ('Kennesaw', 'GA', 34.0234, -84.6155),
    ('East Point', 'GA', 33.6795, -84.4394),
]

COMPANIES = [
    'Peachtree Labs', 'Midtown Apps', 'Downtown Data Co', 'Buckhead Systems',
    'Decatur Tech', 'Sandy Springs Cloud', 'Marietta Mobile', 'Alpharetta AI',
    'Piedmont Software', 'Ponce Digital', 'Beltline Robotics', 'Stone Mountain Games',
    'Chattahoochee Analytics', 'Centennial Cyber', 'Fox Theatre Media',
]

TITLES = [
    'Software Engineer', 'Frontend Developer', 'Backend Engineer', 'Full Stack Developer',
    'Data Analyst', 'Data Engineer', 'Machine Learning Engineer', 'DevOps Engineer',
    'QA Engineer', 'Mobile Developer', 'Site Reliability Engineer', 'Platform Engineer',
    'Security Engineer', 'Cloud Engineer', 'Junior Software Engineer', 'Product Engineer',
]

FIRST = [
    'Maya', 'Liam', 'Aisha', 'Noah', 'Priya', 'Diego', 'Chloe', 'Omar', 'Sofia',
    'Ethan', 'Nia', 'Jonah', 'Grace', 'Ravi', 'Zoe', 'Marcus', 'Hana', 'Leo',
    'Ivy', 'Tariq', 'Elena', 'Sam',
]
LAST = [
    'Nguyen', 'Patel', 'Johnson', 'Garcia', 'Kim', 'Okafor', 'Brooks', 'Rossi',
    'Hassan', 'Clark', 'Mehta', 'Flores', 'Walsh', 'Diallo', 'Reyes', 'Cohen',
]

HEADLINES = [
    'Backend developer who likes clean APIs',
    'Frontend engineer focused on accessible UI',
    'Recent CS grad looking for a first role',
    'Full stack developer, comfortable across the stack',
    'Data person who turns messy numbers into dashboards',
    'Mobile developer shipping iOS and Android apps',
    'Infrastructure engineer into automation',
    'Machine learning engineer with a research background',
]
EDUCATION = [
    'B.S. Computer Science, Georgia Tech, 2025',
    'B.S. Software Engineering, Georgia State, 2024',
    'B.S. Computer Science, Kennesaw State, 2026',
    'M.S. Computer Science, Georgia Tech, 2024',
]
WORK = [
    'Software intern at a local startup for two summers.',
    'Teaching assistant for an intro programming course.',
    'Freelance web projects for small businesses.',
    'Built a side project with a few hundred users.',
    'Contributed to an open source library.',
]


class Command(BaseCommand):
    help = 'Seed the database with demo recruiters, job seekers, jobs, and applications.'

    def add_arguments(self, parser):
        parser.add_argument('--jobs', type=int, default=30, help='Number of jobs to create.')
        parser.add_argument('--seekers', type=int, default=18, help='Number of job seekers to create.')
        parser.add_argument('--recruiters', type=int, default=6, help='Number of recruiters to create.')
        parser.add_argument('--fresh', action='store_true', help='Remove demo data before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        if options['fresh']:
            jobs = Job.objects.filter(posted_by__username__startswith=PREFIX)
            Application.objects.filter(job__in=jobs).delete()
            Application.objects.filter(user__username__startswith=PREFIX).delete()
            jobs.delete()
            removed, _ = User.objects.filter(username__startswith=PREFIX).delete()
            self.stdout.write(self.style.WARNING(f'Removed demo data ({removed} records).'))

        skills = {name: Skill.objects.get_or_create(name=name)[0] for name in SKILLS}

        recruiter_group, _ = Group.objects.get_or_create(name='Recruiters')
        recruiter_group.permissions.add(Permission.objects.get(codename='add_job'))
        seeker_group, _ = Group.objects.get_or_create(name='Seeker')

        recruiters = self._make_recruiters(options['recruiters'], recruiter_group)
        jobs = self._make_jobs(options['jobs'], recruiters, skills)
        seekers = self._make_seekers(options['seekers'], seeker_group, skills)
        self._make_applications(seekers, jobs)
        self._make_hero_accounts(recruiter_group, seeker_group, skills, jobs)

        self._report()

    def _make_recruiters(self, count, group):
        recruiters = []
        for i in range(count):
            company = COMPANIES[i % len(COMPANIES)]
            username = PREFIX + 'rec' + str(i + 1)
            user = self._user(username, company.split()[0], 'Recruiter')
            user.groups.add(group)
            recruiters.append(user)
        return recruiters

    def _make_jobs(self, count, recruiters, skills):
        jobs = []
        seen = set()
        attempts = 0
        while len(jobs) < count and attempts < count * 5:
            attempts += 1
            title = random.choice(TITLES)
            company = random.choice(COMPANIES)
            if (title, company) in seen:
                continue
            seen.add((title, company))
            city, state, lat, lng = random.choice(LOCATIONS)
            lo = random.choice([60, 70, 80, 90, 100]) * 1000
            hi = lo + random.choice([20, 30, 40]) * 1000
            remote = random.random() < 0.2
            job = Job.objects.create(
                title=title,
                company=company,
                description=f'{title} role at {company} in the Atlanta area.',
                city=city, state=state,
                latitude=lat + random.uniform(-0.01, 0.01),
                longitude=lng + random.uniform(-0.01, 0.01),
                salary_min=lo, salary_max=hi,
                is_remote=remote,
                visa_sponsorship=random.random() < 0.3,
                posted_by=random.choice(recruiters),
            )
            job.skills.set(random.sample(list(skills.values()), random.randint(2, 4)))
            jobs.append(job)
        return jobs

    def _make_seekers(self, count, group, skills):
        seekers = []
        for i in range(count):
            username = PREFIX + 'seeker' + str(i + 1)
            name = f'{random.choice(FIRST)} {random.choice(LAST)}'
            user = self._user(username, *name.split(' ', 1))
            user.groups.add(group)
            city, state, lat, lng = random.choice(LOCATIONS)
            profile, _ = JobSeeker.objects.get_or_create(user=user, defaults={'name': name})
            profile.name = name
            profile.headline = random.choice(HEADLINES)
            profile.education = random.choice(EDUCATION)
            profile.work_exp = random.choice(WORK)
            profile.links = 'https://github.com/' + username
            profile.is_public = random.random() < 0.85
            profile.latitude = lat + random.uniform(-0.02, 0.02)
            profile.longitude = lng + random.uniform(-0.02, 0.02)
            profile.save()
            profile.skills.set(random.sample(list(skills.values()), random.randint(3, 6)))
            seekers.append(user)
        return seekers

    def _make_applications(self, seekers, jobs):
        statuses = ['applied', 'applied', 'review', 'review', 'interview', 'offer', 'closed']
        for user in seekers:
            for job in random.sample(jobs, random.randint(2, 5)):
                Application.objects.get_or_create(
                    user=user, job=job,
                    defaults={'status': random.choice(statuses)},
                )

    def _make_hero_accounts(self, recruiter_group, seeker_group, skills, jobs):
        # An easy-to-remember recruiter who owns a few jobs with applicants.
        recruiter = self._user(PREFIX + 'recruiter', 'Riley', 'Recruiter')
        recruiter.groups.add(recruiter_group)
        owned = random.sample(jobs, min(4, len(jobs)))
        for job in owned:
            job.posted_by = recruiter
            job.save(update_fields=['posted_by'])

        # An easy-to-remember seeker with one offer and one rejection ready to reveal.
        seeker = self._user(PREFIX + 'seeker', 'Jordan', 'Seeker')
        seeker.groups.add(seeker_group)
        profile, _ = JobSeeker.objects.get_or_create(user=seeker, defaults={'name': 'Jordan Seeker'})
        profile.name = 'Jordan Seeker'
        profile.headline = 'Full stack developer looking for a first role'
        profile.education = 'B.S. Computer Science, Georgia Tech, 2026'
        profile.work_exp = 'Two internships and a handful of side projects.'
        profile.links = 'https://github.com/demo_seeker'
        profile.is_public = True
        city, state, lat, lng = LOCATIONS[0]
        profile.latitude, profile.longitude = lat, lng
        profile.save()
        profile.skills.set(random.sample(list(skills.values()), 5))

        for job, status in zip(owned, ['offer', 'closed', 'interview', 'review']):
            app, _ = Application.objects.get_or_create(user=seeker, job=job)
            app.status = status
            app.save(update_fields=['status'])

    def _user(self, username, first, last):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': username + '@example.com'},
        )
        user.set_password(PASSWORD)
        user.save()
        return user

    def _report(self):
        self.stdout.write(self.style.SUCCESS(
            'Demo data ready: '
            f'{User.objects.filter(username__startswith=PREFIX).count()} accounts, '
            f'{Job.objects.count()} jobs, {Application.objects.count()} applications.'
        ))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Log in with these (all passwords are the same):'))
        self.stdout.write(f'  Recruiter:  demo_recruiter  /  {PASSWORD}')
        self.stdout.write(f'  Job seeker: demo_seeker     /  {PASSWORD}')
        self.stdout.write(f'  Bulk accounts: demo_rec1..N and demo_seeker1..N  /  {PASSWORD}')
        self.stdout.write('')
        self.stdout.write('demo_seeker already has an offer and a rejection waiting in the honey jar.')

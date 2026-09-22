from django.core.management.base import BaseCommand

from jobs.models import Job

SAMPLE_JOBS = [
    {
        'title': 'Junior Software Engineer', 'company': 'Peachtree Labs',
        'address': '75 5th St NW', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.7772, 'longitude': -84.3894,
        'salary_min': 80000, 'salary_max': 100000,
        'description': 'Entry-level role near Georgia Tech.',
    },
    {
        'title': 'Frontend Developer', 'company': 'Midtown Apps',
        'address': '1100 Peachtree St NE', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.7859, 'longitude': -84.3830,
        'salary_min': 85000, 'salary_max': 110000,
        'description': 'React-focused frontend position in Midtown.',
    },
    {
        'title': 'Data Analyst', 'company': 'Downtown Data Co',
        'address': '191 Peachtree St NE', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.7590, 'longitude': -84.3874,
        'salary_min': 70000, 'salary_max': 90000,
        'description': 'SQL and dashboards for a downtown analytics team.',
    },
    {
        'title': 'Backend Engineer', 'company': 'Buckhead Systems',
        'address': '3344 Peachtree Rd NE', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.8484, 'longitude': -84.3630,
        'salary_min': 95000, 'salary_max': 125000,
        'description': 'Python/Django backend role in Buckhead.',
    },
    {
        'title': 'QA Engineer', 'company': 'Decatur Tech',
        'address': '101 E Court Sq', 'city': 'Decatur', 'state': 'GA',
        'latitude': 33.7748, 'longitude': -84.2963,
        'salary_min': 65000, 'salary_max': 85000,
        'description': 'Manual and automated testing in Decatur.',
    },
    {
        'title': 'DevOps Engineer', 'company': 'Sandy Springs Cloud',
        'address': '6100 Lake Forrest Dr', 'city': 'Sandy Springs', 'state': 'GA',
        'latitude': 33.9304, 'longitude': -84.3733,
        'salary_min': 100000, 'salary_max': 130000,
        'description': 'CI/CD and infrastructure north of the city.',
    },
    {
        'title': 'Mobile Developer', 'company': 'Marietta Mobile',
        'address': '100 Cherokee St', 'city': 'Marietta', 'state': 'GA',
        'latitude': 33.9526, 'longitude': -84.5499,
        'salary_min': 90000, 'salary_max': 115000,
        'description': 'iOS/Android development in Marietta.',
    },
    {
        'title': 'ML Engineer', 'company': 'Alpharetta AI',
        'address': '2 S Main St', 'city': 'Alpharetta', 'state': 'GA',
        'latitude': 34.0754, 'longitude': -84.2941,
        'salary_min': 110000, 'salary_max': 145000,
        'description': 'Machine learning role in the Alpharetta tech corridor.',
    },
    {
        'title': 'Support Engineer (Remote)', 'company': 'Remote First Inc',
        'address': '', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.7490, 'longitude': -84.3880,
        'salary_min': 60000, 'salary_max': 75000, 'is_remote': True,
        'description': 'Fully remote support role, HQ pinned in Atlanta.',
    },
    {
        'title': 'Full Stack Developer', 'company': 'Airport Logistics',
        'address': '6000 N Terminal Pkwy', 'city': 'Atlanta', 'state': 'GA',
        'latitude': 33.6407, 'longitude': -84.4277,
        'salary_min': 85000, 'salary_max': 120000,
        'description': 'Full stack role near Hartsfield-Jackson airport.',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample job postings for the map.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh',
            action='store_true',
            help='Delete existing jobs before seeding.',
        )

    def handle(self, *args, **options):
        if options['fresh']:
            deleted, _ = Job.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing job(s).'))

        created = 0
        for data in SAMPLE_JOBS:
            _, was_created = Job.objects.get_or_create(
                title=data['title'], company=data['company'], defaults=data,
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {created} new job(s), {Job.objects.count()} total.'
        ))

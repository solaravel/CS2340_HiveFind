from django.conf import settings
from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_remote = models.BooleanField(default=False)

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company}'

    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f'${self.salary_min:,} - ${self.salary_max:,}'
        if self.salary_min:
            return f'From ${self.salary_min:,}'
        if self.salary_max:
            return f'Up to ${self.salary_max:,}'
        return 'Not specified'

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'salary': self.salary_display(),
            'is_remote': self.is_remote,
        }

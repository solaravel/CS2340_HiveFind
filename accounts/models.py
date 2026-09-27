from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class JobSeeker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    headline = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    education = models.TextField(blank=True)
    work_exp = models.TextField(blank=True)
    links = models.URLField(blank=True)

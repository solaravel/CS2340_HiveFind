from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class JobSeeker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    headline = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True)
    education = models.TextField()

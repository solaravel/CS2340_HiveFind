from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import CandidateMatchNotification, JobSeeker, SavedCandidateSearch


def notify_saved_searches(candidate):
    for search in SavedCandidateSearch.objects.all():
        matches = Q(name__icontains=search.query) | Q(headline__icontains=search.query) | Q(skills__name__icontains=search.query)
        if JobSeeker.objects.filter(pk=candidate.pk).filter(matches).exists():
            CandidateMatchNotification.objects.get_or_create(search=search, candidate=candidate)


@receiver(post_save, sender=JobSeeker)
def notify_on_candidate_save(sender, instance, **kwargs):
    notify_saved_searches(instance)


@receiver(m2m_changed, sender=JobSeeker.skills.through)
def notify_on_candidate_skills_change(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        notify_saved_searches(instance)

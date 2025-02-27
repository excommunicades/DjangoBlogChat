from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from authify.models import Clerbie
from profile.models import Clerbie_reviews

@receiver(post_save, sender=Clerbie_reviews)
def update_behavior_points_on_review_create(sender, instance, created, **kwargs):

    if created:

        profile = instance.profile
        user = instance.user

        if instance.reaction == 'like':
            profile.behavior_points += 5
        elif instance.reaction == 'dislike':
            profile.behavior_points -= 5

        profile.save()

@receiver(post_delete, sender=Clerbie_reviews)
def update_behavior_points_on_review_delete(sender, instance, **kwargs):

    profile = instance.profile

    if instance.reaction == 'like':
        profile.behavior_points -= 5
    elif instance.reaction == 'dislike':
        profile.behavior_points += 5

    profile.save()
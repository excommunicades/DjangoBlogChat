import uuid
import os
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models

from authify.models import Clerbie
from profile.choices import (
    REACTIONS,
    STATUS_CHOICES,
)

def image_upload_certification_function(instance, filename):

    model_name = instance.__class__.__name__.lower()
    print(model_name == 'clerbie_certificates')
    if model_name == "clerbie_certificates":
        folder_name = "certificates"

    else:
        folder_name = "other_images"

    safe_title = instance.title.replace(" ", "_").replace("/", "_")

    return os.path.join(folder_name, safe_title, filename)

class Clerbie_reactions(models.Model):

    user = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name='user_reactions')
    profile = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name='profile_reactions')
    reaction = models.CharField(choices=REACTIONS)
    review = models.TextField(max_length=7000, blank=True, null=True)

    class Meta:
        db_table = 'UserReactions'
class Clerbie_friends(models.Model):

    user1 = models.ForeignKey(Clerbie, related_name='friends', on_delete=models.CASCADE)
    user2 = models.ForeignKey(Clerbie, related_name='friends_with', on_delete=models.CASCADE)
    offer_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=7000, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('blocked', 'Blocked')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship')
        ]

    class Meta:
        db_table = 'UserFriends'
class Hobby(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Hobbies'

class Clerbie_hobbies(models.Model):
    user = models.ForeignKey(Clerbie, related_name='hobbies', on_delete=models.CASCADE)
    hobby = models.ForeignKey(Hobby, related_name='users', on_delete=models.CASCADE)
    description = models.TextField(max_length=7000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nickname}'s hobby: {self.hobby.name}"

    class Meta:
        db_table = 'UserHobbies'

class University(models.Model):

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Educations'
class Clerbie_education(models.Model):
    user = models.ForeignKey(Clerbie ,related_name='education_users', on_delete=models.CASCADE)
    university = models.ForeignKey(University, related_name='universities',max_length=50, blank=False, null=True, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=50, blank=False, null=True)
    started_at = models.DateField(blank=False, null=True)
    ended_at = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'UserEducations'
# class Certificates(models.Model):

#     name = models.CharField(max_length=100)
#     description = models.TextField(max_length=7000, blank=True, null=True)

#     def __str__(self):
#         return self.name
#     class Meta:
#         db_table = 'Certificates'
# class Clerbie_certificates(models.Model):

#     user = models.ForeignKey(Clerbie, related_name='certificates', on_delete=models.CASCADE)
#     certificates = models.ManyToManyField(Certificates, related_name='users')
#     description = models.TextField(max_length=7000,  blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.nickname}'s hobby: {self.hobby.name}"

#     class Meta:
#         db_table = 'UserCertificates'

class Clerbie_certificates(models.Model):

    user = models.ForeignKey('authify.Clerbie', related_name='certificates_users', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=True)
    photo = models.ImageField(upload_to=image_upload_certification_function, null=True, blank=False)
    organization = models.CharField(max_length=100, blank=False, null=True)
    issued_at = models.DateField(blank=False, null=True)
    description = models.TextField(max_length=2500,  blank=True, null=True)

    class Meta:
        db_table = 'UserCertificates'

class Technologies(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=7000, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Technologies'

class Projects(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=7000, blank=True, null=True)
    technologies = models.ManyToManyField(Technologies, blank=True)
    users = models.ManyToManyField(Clerbie, related_name='projects')
    creator = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name="created_project")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Projects'

class Work(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=7000, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Works'


class UserWorkExperience(models.Model):
    user = models.ForeignKey(Clerbie, related_name='work_experience', on_delete=models.CASCADE)
    work = models.ForeignKey(Work, related_name='users', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=7000, blank=True, null=True)

    def duration(self):
        if self.end_date:
            return (self.end_date - self.start_date).days
        return "Current job"

    class Meta:
        db_table = 'UserWorks'

class Offers(models.Model):

    offer_type = models.CharField(max_length=7, choices=[('request', 'Request'), ('invite', 'Invite')], default='request')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    sender = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name="sent_offers")
    receiver = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name="received_offers")
    offer_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=2000, blank=True, null=True)


    def __str__(self):
        return f"Offer from {self.sender.nickname} to {self.receiver.nickname} for {self.project.name}"

    class Meta:
        db_table = 'ProjectOffers'


class InboxMessage(models.Model):
    user = models.ForeignKey(Clerbie, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.user.nickname}"
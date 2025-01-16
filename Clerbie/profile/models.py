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

class Clerbie_reactions(models.Model):

    user = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name='user_reactions')
    profile = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name='profile_reactions')
    reaction = models.CharField(choices=REACTIONS)
    review = models.TextField(max_length=7000, blank=True, null=True)

    class Meta:
        db_table = 'UserReactions'
class Clerbie_friends(models.Model):

    user = models.ForeignKey(Clerbie, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(Clerbie, related_name='friends_with', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('blocked', 'Blocked')],
        default='pending'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'friend'], name='unique_friendship')
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
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nickname}'s hobby: {self.hobby.name}"

    class Meta:
        db_table = 'UserHobbies'

class Education(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Educations'
class Clerbie_education(models.Model):
    user = models.ForeignKey(Clerbie, related_name='education', on_delete=models.CASCADE)
    education = models.ManyToManyField(Education, related_name='users')
    description = models.TextField(max_length=7000)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nickname}'s hobby: {self.hobby.name}"

    class Meta:
        db_table = 'UserEducations'
class Certificates(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=7000, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Certificates'
class Clerbie_certificates(models.Model):

    user = models.ForeignKey(Clerbie, related_name='certificates', on_delete=models.CASCADE)
    certificates = models.ManyToManyField(Certificates, related_name='users')
    description = models.TextField(max_length=7000,  blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nickname}'s hobby: {self.hobby.name}"

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

class Invitation(models.Model):

    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    sender = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name="sent_invitations")
    receiver = models.ForeignKey(Clerbie, on_delete=models.CASCADE, related_name="received_invitations")
    invite_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Invitation from {self.sender.nickname} to {self.receiver.nickname} for {self.project.name}"

    class Meta:
        db_table = 'ProjectInvitations'


class InboxMessage(models.Model):
    user = models.ForeignKey(Clerbie, on_delete=models.CASCADE)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.user.nickname}"
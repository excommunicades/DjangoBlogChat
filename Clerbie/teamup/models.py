from django.db import models

# Create your models here.

from authify.models import Clerbie
from profile.models import (
    Projects,
    Technologies,
    JobTitles,
)


class Announcement(models.Model):

    owner = models.ForeignKey(Clerbie, on_delete=models.CASCADE, blank=False, null=False)
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(max_length=10000, null=True, blank=True)
    job_titles = models.ManyToManyField(JobTitles, blank=False, related_name='hiring_positions')
    technologies = models.ManyToManyField(Technologies, blank=True, related_name='technologies')
    project = models.ForeignKey(Projects, null=False, blank=False, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Announcement'


class AnnouncementRequests(models.Model):

    employee = models.ForeignKey(Clerbie, on_delete=models.CASCADE, blank=False, null=False)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, blank=False, null=False)
    job_title = models.CharField(default='employee', blank=False, null=False)
    cover_list = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'AnnouncementRequests'
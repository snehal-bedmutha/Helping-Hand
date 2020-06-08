from django.contrib.auth.models import AbstractUser
from django.db import models
from course.models import *
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.db import models

# Create your models here.
class job(models.Model):
    job_name = models.CharField(max_length=200)
    job_description = models.TextField(default='')
    job_type = models.TextField(default='', blank=True)
    skills_needed = models.CharField(max_length=100, default='', blank=True)
    hourly_pay = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.job_name

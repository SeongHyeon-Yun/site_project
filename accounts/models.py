from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bank = models.CharField(max_length=20, blank=True)
    account_holder = models.CharField(max_length=50, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    recommender_code = models.CharField(max_length=50, blank=True, null=True)

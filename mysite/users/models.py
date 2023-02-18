from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

class GenderChoice():   # A subclass of Enum
    Male = "Male"
    Female = "Female"

class ShowNameChoice(Enum):   # A subclass of Enum
    username = "username"
    nickname = "nickname"

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    register_year = models.DateField()
    birthday = models.DateField()
    nickname = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=[("Male", "Male"), ("Female", "Female")])
    shown_name = models.CharField(max_length=8, choices=[("username", "username"), ("nickname", "nickname")])
    verification_code = models.CharField(max_length=10, null=True)
    is_verified = models.BooleanField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
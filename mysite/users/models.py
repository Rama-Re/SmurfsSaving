from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from enum import Enum


class GenderChoice():  # A subclass of Enum
    Male = "Male"
    Female = "Female"


class ShowNameChoice(Enum):  # A subclass of Enum
    username = "username"
    nickname = "nickname"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password,
                                **{'is_staff': True, 'is_superuser': True, 'username': extra_fields.get('username')})


class User(AbstractUser):
    name = models.CharField(max_length=255)
    # email = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    register_year = models.DateField()
    birthday = models.DateField()
    nickname = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=[("M", "Male"), ("F", "Female")])
    shown_name = models.CharField(max_length=8, choices=[("username", "username"), ("nickname", "nickname")])
    verification_code = models.CharField(max_length=10, null=True)
    is_verified = models.BooleanField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

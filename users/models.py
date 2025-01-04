from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is unique
    username = models.CharField(max_length=150, null=True, blank=True)  # Allow duplicate usernames

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    



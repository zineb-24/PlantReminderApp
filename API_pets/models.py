from django.db import models
from users.models import User
from datetime import date
from django.core.exceptions import ValidationError


# The pets species stored in the database
class Pet(models.Model):
    species_name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255)
    breed_name = models.CharField(max_length=255)
    lifespan = models.CharField(max_length=255)
    daily_sleep = models.CharField(max_length=255)
    gestation = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    diet = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pets/', null=True, blank=True)  

    def __str__(self):
        return self.breed_name


# Pets of the user
class UserPet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pet')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='user_pet')
    nickname = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='user_pets/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Default the UserPet's image to the Pet's image if not explicitly set
        if not self.image and self.pet.image:
            self.image = self.pet.image
        super().save(*args, **kwargs)

    def clean(self):
        # Ensure the birth_date is not in the future
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")

    @property
    def age(self):
        """Calculate the pet's age in years."""
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None

    def __str__(self):
        return f"{self.nickname or self.pet.species_name} ({self.user.username})"

from django.db import models
from users.models import User
from datetime import timedelta
from datetime import datetime
from django.core.exceptions import ValidationError


# The plant species stored in the database
class Plant(models.Model):
    species_name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255)
    preferred_light = models.CharField(max_length=255)
    ideal_temp = models.CharField(max_length=255)
    bloom_time = models.CharField(max_length=255, null=True, blank=True)
    toxicity = models.CharField(max_length=255)
    ideal_water = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='plants/', null=True, blank=True)  

    def __str__(self):
        return self.species_name


# Sites the user can add to organize their plants
class Site(models.Model):
    LIGHT_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    LOCATION_CHOICES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sites'
    )
    name = models.CharField(max_length=255)
    light = models.CharField(max_length=20, choices=LIGHT_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


# Plants of the user
class UserPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_plants')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='user_plants')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='site')
    nickname = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='user_plants/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Default the UserPlant's image to the Plant's image if not explicitly set
        if not self.image and self.plant.image:
            self.image = self.plant.image
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nickname or self.plant.species_name} ({self.user.username})"


# Tasks the user defines for their UserPlant
class UserPlantTask(models.Model):
    TASK_CHOICES = [
        ('misting', 'Misting'),
        ('watering', 'Watering'),
        ('pruning', 'Pruning'),
        ('fertilizing', 'Fertilizing'),
    ]

    user_plant = models.ForeignKey(UserPlant, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=50, choices=TASK_CHOICES)
    description = models.TextField(blank=True, null=True)  # Optional custom description

    # Last time the task was completed (updated to match the last TaskToCheck completion date)
    last_completed_at = models.DateTimeField(null=True, blank=True)
    interval = models.PositiveIntegerField(default=1)  # Number of units for custom frequency (e.g., every 2 weeks)
    unit = models.CharField(
        max_length=50,
        choices=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)')],
        default='day'
    )

    def __str__(self):
        return f"{self.get_name_display()} (User: {self.user_plant.user.username})"

    def clean(self):
        """Ensure interval is positive"""
        if self.interval <= 0:
            raise ValidationError("Interval must be greater than zero.")

    def calculate_next_due_date(self):
        """Calculate the next due date based on the last completed date."""
        if not self.last_completed_at:
            # If no last completed date, use the current time
            return datetime.now()

        if self.unit == 'day':
            return self.last_completed_at + timedelta(days=self.interval)
        elif self.unit == 'week':
            return self.last_completed_at + timedelta(weeks=self.interval)
        elif self.unit == 'month':
            return self.last_completed_at + timedelta(weeks=4 * self.interval)  # Approx. 4 weeks for a month
        return self.last_completed_at


# The task instance the user checks related to a UserPlantTask
class TaskToCheck(models.Model):
    user_plant_task = models.ForeignKey(UserPlantTask, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_as_completed(self):
        """Mark the task as completed, update the parent task's last_completed_at, and create the next task."""
        self.is_completed = True
        self.completed_at = datetime.now()  # Set the completion date
        self.save()

        # Update the parent task's last_completed_at to the completed_at of this task
        if self.user_plant_task:
            self.user_plant_task.last_completed_at = self.completed_at
            self.user_plant_task.save()

        # Calculate the next task's due date using the UserPlantTask's calculate_next_due_date method
        next_due_date = self.user_plant_task.calculate_next_due_date()

        # Create a new task for the next cycle
        new_task = TaskToCheck.objects.create(
            user_plant_task=self.user_plant_task,
            due_date=next_due_date,
            is_completed=False  # New task is not completed
        )

        return new_task

    @classmethod
    def get_overdue_tasks(cls, user):
        """Retrieve all overdue tasks."""
        return cls.objects.filter(user_plant_task__user_plant__user=user, is_completed=False, due_date__lt=datetime.now())

    def __str__(self):
        return f"Task: {self.user_plant_task.name} for {self.user_plant_task.user_plant.nickname}"

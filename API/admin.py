from django.contrib import admin
from .models import Plant, UserPlant, Site, UserPlantTask, TaskToCheck

# Register your models here.

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'scientific_name')
    search_fields = ('species_name', 'scientific_name')


@admin.register(UserPlant)
class UserPlantAdmin(admin.ModelAdmin):
    list_display = ('user', 'plant', 'nickname', 'added_at')
    search_fields = ('nickname', 'plant__species_name', 'user__username')
    list_filter = ('added_at',)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'light', 'location')
    list_filter = ('light', 'location')
    search_fields = ('name', 'user__username')


@admin.register(UserPlantTask)
class UserPlantTaskAdmin(admin.ModelAdmin):
    list_display = ('user_plant', 'name', 'interval', 'unit', 'last_completed_at', 'description')  # Fields to display in list view
    search_fields = ('user_plant__nickname', 'name', 'user_plant__user__username')  # Searchable fields
    list_filter = ('name', 'unit', 'user_plant__user')  # Filter tasks by name, unit, and user
    list_editable = ('interval', 'unit', 'description')  # Allow editing interval, unit, and description from the list view


@admin.register(TaskToCheck)
class TaskToCheckAdmin(admin.ModelAdmin):
    list_display = ('user_plant_task', 'due_date', 'is_completed', 'completed_at')  # Display these fields in the list
    search_fields = ('user_plant_task__name', 'user_plant_task__user_plant__nickname', 'user_plant_task__user_plant__user__username')  # Searchable fields
    list_filter = ('is_completed', 'user_plant_task__user_plant__user')  # Filter tasks by completion status and user
    list_editable = ('is_completed',)  # Allow marking tasks as completed from the list view




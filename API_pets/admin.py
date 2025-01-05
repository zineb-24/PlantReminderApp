from django.contrib import admin
from .models import Pet, UserPet

# Register your models here.

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'breed_name', 'scientific_name', 'lifespan')
    search_fields = ('species_name', 'breed_name', 'scientific_name')
    list_filter = ('species_name',)


@admin.register(UserPet)
class UserPetAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'user', 'birth_date', 'pet')
    search_fields = ('nickname', 'user__email', 'pet__species_name')
    list_filter = ('pet__species_name',)
from django.urls import path
from .views import UserPetListView, UserPetSpeciesView

urlpatterns = [
    path('user-pets/', UserPetListView.as_view(), name='userPet-list'),
    path('user-pets/species/', UserPetSpeciesView.as_view(), name='user-pet-species'),
]
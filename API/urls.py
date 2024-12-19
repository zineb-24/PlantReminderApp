from django.urls import path
from .views import PlantListView, PlantDetailView, UserPlantListView, UserPlantDetailView, SiteDetailView, SiteListCreateView,AddUserPlantTaskView, UpdateTaskFrequencyView, DeleteUserPlantTaskView

urlpatterns = [
    path('plants/', PlantListView.as_view(), name='plant-list'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),

    path('user-plants/', UserPlantListView.as_view(), name='userPlant-list-create'),
    path('user-plants/<int:pk>/', UserPlantListView.as_view(), name='userPlant-update-delete'),
    path('userPlant-details/<int:pk>/', UserPlantDetailView.as_view(), name='userPlant-detail'),

    path('sites/', SiteListCreateView.as_view(), name='site-list-create'),
    path('sites/<int:pk>/', SiteDetailView.as_view(), name='site-detail'),


    path('plants/<int:plant_id>/tasks/', AddUserPlantTaskView.as_view(), name='add_task'),
    path('tasks/<int:task_id>/update/', UpdateTaskFrequencyView.as_view(), name='update_task_frequency'),
    path('tasks/<int:task_id>/delete/', DeleteUserPlantTaskView.as_view(), name='delete_task'),
]
]

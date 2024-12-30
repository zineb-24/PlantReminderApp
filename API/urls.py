from django.urls import path
from .views import (
    PlantListView,
    PlantDetailView,
    UserPlantListView,
    UserPlantDetailView,
    SiteDetailView,
    SiteListCreateView,
    AddUserPlantTaskView,
    UpdateTaskFrequencyView,
    DeleteUserPlantTaskView,
    CompletedTasksView,
    MarkTaskAsCompletedView,
    HomepageTasksView,
    UserPlantTasksView,
    RemovePlantFromSiteView,
)

urlpatterns = [
    # Plant-related URLs
    path('plants/', PlantListView.as_view(), name='plant-list'),
    path('plants/<int:plant_id>/', PlantDetailView.as_view(), name='plant-detail'),

    # UserPlant-related URLs
    path('user-plants/', UserPlantListView.as_view(), name='userPlant-list-create'),
    path('user-plants/<int:userPlant_id>/', UserPlantListView.as_view(), name='userPlant-update-delete'),
    path('userPlant-details/<int:userPlant_id>/', UserPlantDetailView.as_view(), name='userPlant-detail'),

    # Site-related URLs
    path('sites/', SiteListCreateView.as_view(), name='site-list-create'),
    path('sites/<int:pk>/', SiteDetailView.as_view(), name='site-detail'),
    path('sites/<int:site_id>/plants/<int:userPlant_id>/remove/', RemovePlantFromSiteView.as_view(), name='remove-plant-from-site'),

    # Task-related URLs
    path('plants/<int:userPlant_id>/tasks/', UserPlantTasksView.as_view(), name='plant-tasks'),
    path('plants/<int:userPlant_id>/tasks/', AddUserPlantTaskView.as_view(), name='add-task'),
    path('tasks/<int:task_id>/update/', UpdateTaskFrequencyView.as_view(), name='update-task-frequency'),
    path('tasks/<int:task_id>/delete/', DeleteUserPlantTaskView.as_view(), name='delete-task'),
    path('tasks/completed/', CompletedTasksView.as_view(), name='Tasks-history'),
    path('tasks/<int:task_id>/complete/', MarkTaskAsCompletedView.as_view(), name='mark-task-completed'),
    path('tasks/homepage-tasks/', HomepageTasksView.as_view(), name='homepage-tasks'),
]



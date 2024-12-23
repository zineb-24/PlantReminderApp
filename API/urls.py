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
    UserTasksView,
    CompletedTasksView,
    MarkTaskAsCompletedView,
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
    path('sites/<int:site_id>/', SiteDetailView.as_view(), name='site-detail'),

    # Task-related URLs
    path('plants/<int:userPlant_id>/tasks/', AddUserPlantTaskView.as_view(), name='add-task'),
    path('tasks/<int:task_id>/update/', UpdateTaskFrequencyView.as_view(), name='update-task-frequency'),
    path('tasks/<int:task_id>/delete/', DeleteUserPlantTaskView.as_view(), name='delete-task'),
    path('tasks/due/', UserTasksView.as_view(), name='due-tasks'),
    path('tasks/completed/', CompletedTasksView.as_view(), name='Tasks-history'),
    path('tasks/<int:task_id>/complete/', MarkTaskAsCompletedView.as_view(), name='mark-task-completed'),
]



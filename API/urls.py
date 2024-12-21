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
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),

    # UserPlant-related URLs
    path('user-plants/', UserPlantListView.as_view(), name='userPlant-list-create'),
    path('user-plants/<int:pk>/', UserPlantListView.as_view(), name='userPlant-update-delete'),
    path('userPlant-details/<int:pk>/', UserPlantDetailView.as_view(), name='userPlant-detail'),

    # Site-related URLs
    path('sites/', SiteListCreateView.as_view(), name='site-list-create'),
    path('sites/<int:pk>/', SiteDetailView.as_view(), name='site-detail'),

    # Task-related URLs
    path('plants/<int:plant_id>/tasks/', AddUserPlantTaskView.as_view(), name='add_task'),
    path('tasks/<int:task_id>/update/', UpdateTaskFrequencyView.as_view(), name='update_task_frequency'),
    path('tasks/<int:task_id>/delete/', DeleteUserPlantTaskView.as_view(), name='delete_task'),
    path('tasks/due/', UserTasksView.as_view(), name='due_tasks'),
    path('tasks/completed/', CompletedTasksView.as_view(), name='completed_tasks'),
    path('tasks/<int:task_id>/complete/', MarkTaskAsCompletedView.as_view(), name='mark_task_as_completed'),
]



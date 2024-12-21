from .models import UserPlant, Plant, Site, UserPlantTask, TaskToCheck
from .serializers import PlantSerializer, UserPlantSerializer, SiteSerializer, UserPlantTaskSerializer
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import models
from datetime import datetime
from django.utils.dateparse import parse_date


# List all plants that matches the search query
class PlantListView(APIView):
    def get(self, request):
        queryset = Plant.objects.all()

        # Get search query from the URL parameters (e.g., /plants/?search=rose)
        search = request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                models.Q(species_name__icontains=search) | 
                models.Q(scientific_name__icontains=search)
            )
        
        # Serialize the filtered queryset
        serializer = PlantSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


# Retreive a specific Plant details (When the user wants to add it)
class PlantDetailView(APIView):
    def get(self, request, pk):
        try:
            plant = Plant.objects.get(pk=pk)
        except Plant.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        serializer = PlantSerializer(plant)
        return JsonResponse(serializer.data)


class UserPlantListView(APIView):
    permission_classes = [IsAuthenticated]

    # List all the UserPlants
    def get(self, request):
        queryset = UserPlant.objects.filter(user=request.user)
        serializer = UserPlantSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    # Add a UserPlant
    def post(self, request):
        serializer = UserPlantSerializer(data=request.data, context={'request': request})  # Add context here
        if serializer.is_valid():
            serializer.save()  # This will use the create method in the serializer
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    # Update the nickname or other fields of a UserPlant
    def patch(self, request, pk):
        try:
            user_plant = UserPlant.objects.get(pk=pk, user=request.user)
        except UserPlant.DoesNotExist:
            return JsonResponse({"error": "UserPlant not found or not owned by user"}, status=404)

        # Allow partial updates (nickname and/or site)
        serializer = UserPlantSerializer(user_plant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    # Delete a UserPlant
    def delete(self, request, pk):
        try:
            plant = UserPlant.objects.get(id=pk, user=request.user)
            plant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserPlant.DoesNotExist:
            return JsonResponse({"error": "Plant not found"}, status=404)


class UserPlantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # Retrieve the UserPlant instance for the authenticated user
            user_plant = UserPlant.objects.get(pk=pk, user=request.user)
        except UserPlant.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        # Serialize the UserPlant instance
        user_plant_data = UserPlantSerializer(user_plant).data

        # Retrieve and serialize UserPlantTask instances related to the UserPlant
        tasks = UserPlantTask.objects.filter(user_plant=user_plant)
        task_data = [
            {
                'name': task.name,
                'frequency': f"{task.interval} {task.unit}(s)"
            }
            for task in tasks
        ]

        # Retrieve and serialize TaskToCheck instances related to the UserPlantTask
        task_checks = TaskToCheck.objects.filter(user_plant_task__user_plant=user_plant)
        task_check_data = [
            {
                'task_name': task_check.user_plant_task.name,
                'due_date': task_check.due_date
            }
            for task_check in task_checks
        ]

        # Combine all the data
        response_data = {
            'user_plant': user_plant_data,
            'tasks': task_data,
            'task_checks': task_check_data
        }

        return Response(response_data, status=200)


# List all sites for the authenticated user or create a new site
class SiteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SiteSerializer

    def get_queryset(self):
        # Return only the sites belonging to the authenticated user
        return Site.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the currently authenticated user
        serializer.save(user=self.request.user)


# Retrieve, update, or delete a specific site
class SiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SiteSerializer

    def get_queryset(self):
        # Ensure users can only access their own sites
        return Site.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure the site belongs to the user
        if self.get_object().user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this site.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure the site belongs to the user
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this site.")
        instance.delete()


#View due and overdue tasks
class UserTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all tasks that are due or overdue and not completed
        tasks = UserPlantTask.objects.filter(user=request.user, is_completed=False, due_date__lte=timezone.now())
        serializer = UserPlantTaskSerializer(tasks, many=True)
        return Response(serializer.data)


#View History of completed tasks
class CompletedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the date from query parameters
        date_param = request.query_params.get('date')

        if date_param:
            try:
                # Parse the date parameter
                date = parse_date(date_param)
                if not date:
                    raise ValueError
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
            
            # Filter tasks completed on the specified date
            completed_tasks = UserPlantTask.objects.filter(
                completed_at__date=date,
                user=request.user
            )
        else:
            # If no date is provided, return all completed tasks
            completed_tasks = UserPlantTask.objects.filter(
                completed_at__isnull=False,
                user=request.user
            )

        # Serialize the tasks
        serializer = UserPlantTaskSerializer(completed_tasks, many=True)

        # Return the serialized data
        return JsonResponse(serializer.data, safe=False)


#Add a UserPlantTask (predefined choices)
class AddUserPlantTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, plant_id):
        try:
            plant = UserPlant.objects.get(id=plant_id, user=request.user)
        except UserPlant.DoesNotExist:
            return Response({"error": "Plant not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        task_data = {
            'user': request.user.id,
            'plant': plant.id,
            'name': request.data.get('name'),
            'description': request.data.get('description', ''),
            'interval': request.data.get('interval'),
            'unit': request.data.get('unit'),
            'last_completed_at': request.data.get('last_completed_at')
        }

        # Parse last_completed_at if provided
        if task_data['last_completed_at']:
            task_data['last_completed_at'] = datetime.fromisoformat(task_data['last_completed_at'])

        serializer = UserPlantTaskSerializer(data=task_data)

        if serializer.is_valid():
            task = serializer.save()

            # Calculate the initial due date based on last_completed_at
            initial_due_date = task.calculate_next_due_date()

            # Create a TaskToCheck for this UserPlantTask
            TaskToCheck.objects.create(
                user_plant_task=task,
                due_date=initial_due_date,
                is_completed=False
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Update frequency of UserPlantTask (Doesn't affect current instance of TaskToCheck)
class UpdateTaskFrequencyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, task_id):
        try:
            # Retrieve the UserPlantTask to update
            task = UserPlantTask.objects.get(id=task_id, user_plant__user=request.user)
        except UserPlantTask.DoesNotExist:
            return Response({"error": "Task not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        # Get the new frequency values from the request
        new_interval = request.data.get('interval')
        new_unit = request.data.get('unit')

        # Validate input
        if new_interval is None or new_unit is None:
            return Response({"error": "Interval and unit must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_interval = int(new_interval)
            if new_interval <= 0:
                raise ValueError("Interval must be a positive integer.")
        except ValueError:
            return Response({"error": "Interval must be a valid positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the task with the new frequency values
        task.interval = new_interval
        task.unit = new_unit
        task.save()

        return Response(
            {"message": "Task frequency updated successfully."},
            status=status.HTTP_200_OK
        )


#Delete UserPlantTask and all related instances of TaskToCheck
class DeleteUserPlantTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        try:
            # Retrieve the task the user wants to delete
            task = UserPlantTask.objects.get(id=task_id, user=request.user)
        except UserPlantTask.DoesNotExist:
            return Response({"error": "Task not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        # Delete all related TaskToCheck instances
        TaskToCheck.objects.filter(user_plant_task=task).delete()

        # Delete the UserPlantTask itself
        task.delete()

        return Response({"message": "Task and its related check tasks have been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


# marking tasks as completed and creating the next cycle is encapsulated within the model 
# while the view simply triggers this process and handles the response
class MarkTaskAsCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            # Retrieve the task to be marked as completed
            task = TaskToCheck.objects.get(id=task_id, user_plant_task__user_plant__user=request.user)
        except TaskToCheck.DoesNotExist:
            return Response({"error": "Task not found or not owned by user."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the task is already completed
        if task.is_completed:
            return Response({"error": "Task is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the task as completed and create the next task
        new_task = task.mark_as_completed()

        return Response(
            {
                "message": "Task marked as completed successfully.",
                "new_task_id": new_task.id,
                "new_task_due_date": new_task.due_date,
            },
            status=status.HTTP_200_OK
        )
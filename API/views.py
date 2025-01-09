from .models import UserPlant, Plant, Site, UserPlantTask, TaskToCheck
from .serializers import PlantSerializer, UserPlantSerializer, SiteSerializer, UserPlantTaskSerializer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import models
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.timezone import now, localtime, timedelta
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
        
        # Serialize the filtered queryset with the request context
        serializer = PlantSerializer(queryset, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)


# Retreive a specific Plant details (When the user wants to add it)
class PlantDetailView(APIView):
    def get(self, request, plant_id):
        try:
            plant = Plant.objects.get(pk=plant_id)
        except Plant.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        serializer = PlantSerializer(plant)
        return JsonResponse(serializer.data)


class UserPlantListView(APIView):
    permission_classes = [IsAuthenticated]

    # List all the UserPlants
    def get(self, request):
        queryset = UserPlant.objects.filter(user=request.user)
        serializer = UserPlantSerializer(queryset, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)

    # Add a UserPlant
    def post(self, request):

        serializer = UserPlantSerializer(data=request.data, context={'request': request})  # Add context here
        if serializer.is_valid():
            serializer.save()  # This will use the create method in the serializer
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    # Update the nickname or other fields of a UserPlant
    def patch(self, request, userPlant_id):
        try:
            user_plant = UserPlant.objects.get(pk=userPlant_id, user=request.user)
        except UserPlant.DoesNotExist:
            return JsonResponse({"error": "UserPlant not found or not owned by user"}, status=404)

        # Allow partial updates (nickname and/or site)
        serializer = UserPlantSerializer(user_plant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    # Delete a UserPlant
    def delete(self, request, userPlant_id):
        try:
            plant = UserPlant.objects.get(pk=userPlant_id, user=request.user)
            plant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserPlant.DoesNotExist:
            return JsonResponse({"error": "Plant not found"}, status=404)


class UserPlantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userPlant_id):
        try:
            # Retrieve the UserPlant instance for the authenticated user
            user_plant = UserPlant.objects.get(pk=userPlant_id, user=request.user)
        except UserPlant.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        # Add request to serializer context
        user_plant_data = UserPlantSerializer(user_plant, context={'request': request}).data

        # Retrieve and serialize UserPlantTask instances related to the UserPlant
        tasks = UserPlantTask.objects.filter(user_plant=user_plant)
        task_data = [
            {
                'name': task.name,
                'frequency': f"every {task.interval} {task.unit}(s)",
                'interval': task.interval,
                'unit': task.unit
            }
            for task in tasks
        ]

        # Define today's time range
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = localtime(now()).replace(hour=23, minute=59, second=59, microsecond=999999)

        # Retrieve incomplete TaskToCheck instances related to the UserPlantTask
        incomplete_tasks = TaskToCheck.objects.filter(user_plant_task__user_plant=user_plant, is_completed=False)

        # Filter overdue tasks
        overdue_tasks = incomplete_tasks.filter(due_date__lt=today_start)
        overdue_task_data = [
            {
                'task_name': task.user_plant_task.name,
                'due_date': task.due_date,
                'interval': task.user_plant_task.interval,
                'unit': task.user_plant_task.unit
            }
            for task in overdue_tasks
        ]

        # Filter tasks due today
        due_today_tasks = incomplete_tasks.filter(due_date__gte=today_start, due_date__lte=today_end)
        due_today_data = [
            {
                'task_name': task.user_plant_task.name,
                'due_date': task.due_date,
                'interval': task.user_plant_task.interval,
                'unit': task.user_plant_task.unit
            }
            for task in due_today_tasks
        ]

        # Filter upcoming tasks (due after today)
        upcoming_tasks = incomplete_tasks.filter(due_date__gt=today_end)
        upcoming_task_data = [
            {
                'task_name': task.user_plant_task.name,
                'due_date': task.due_date,
                'interval': task.user_plant_task.interval,
                'unit': task.user_plant_task.unit
            }
            for task in upcoming_tasks
        ]

        # Combine all the data
        response_data = {
            'user_plant': user_plant_data,
            'tasks': task_data,
            'task_checks': {
                'overdue_tasks': overdue_task_data,
                'tasks_due_today': due_today_data,
                'upcoming_tasks': upcoming_task_data
            }
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


class RemovePlantFromSiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, userPlant_id, site_id):
        try:
            # Get the plant and verify it belongs to the user and the specified site
            plant = UserPlant.objects.get(
                pk=userPlant_id, 
                user=request.user,
                site_id=site_id
            )
            
            # Store site name for response message
            site_name = plant.site.name
            
            # Remove the plant from the site
            plant.site = None
            plant.save()
            
            return Response({
                'message': f'Plant removed from {site_name} successfully'
            }, status=status.HTTP_200_OK)
            
        except UserPlant.DoesNotExist:
            return Response({
                'error': 'Plant not found or not in this site'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class HomepageTasksView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get start date (today) and end date (30 days from now)
        today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=30)

        # Query all tasks due within 30 days or overdue tasks
        all_tasks = TaskToCheck.objects.filter(
            user_plant_task__user_plant__user=request.user,
            due_date__lte=end_date
        ).order_by('due_date')

        overdue_tasks = TaskToCheck.objects.filter(
            user_plant_task__user_plant__user=request.user,
            is_completed=False,
            due_date__lt=today
        ).order_by('due_date')

        # Initialize response dictionary with date as key
        tasks_by_date = {}

        # Process each task and organize by date
        for task in all_tasks:
            task_date = task.due_date.date().isoformat()
            
            task_data = {
                "id": task.id,
                "task_name": task.user_plant_task.name,
                "plant_nickname": task.user_plant_task.user_plant.nickname,
                "site_name": task.user_plant_task.user_plant.site.name if task.user_plant_task.user_plant.site else 'No location',
                "plant_image": task.user_plant_task.user_plant.image.url if task.user_plant_task.user_plant.image else None,
                "description": task.user_plant_task.description,
                "due_date": task.due_date,
                "interval": task.user_plant_task.interval,
                "unit": task.user_plant_task.unit,
                "is_completed": task.is_completed,
                "overdue_since": None,  # Default value for non-overdue tasks
            }

            if task_date not in tasks_by_date:
                tasks_by_date[task_date] = {
                    "due_tasks": [],
                    "overdue": False
                }

            # Mark as overdue if the task's date is before today
            if task.due_date.date() < today.date():
                tasks_by_date[task_date]["overdue"] = True
                task_data["overdue_since"] = task.due_date.date().isoformat()

            tasks_by_date[task_date]["due_tasks"].append(task_data)

        # Add overdue tasks to today's date
        overdue_task_data = []
        for task in overdue_tasks:
            overdue_task_data.append({
                "id": task.id,
                "task_name": task.user_plant_task.name,
                "plant_nickname": task.user_plant_task.user_plant.nickname,
                "site_name": task.user_plant_task.user_plant.site.name if task.user_plant_task.user_plant.site else 'No location',
                "plant_image": task.user_plant_task.user_plant.image.url if task.user_plant_task.user_plant.image else None,
                "description": task.user_plant_task.description,
                "due_date": task.due_date,
                "interval": task.user_plant_task.interval,
                "unit": task.user_plant_task.unit,
                "is_completed": task.is_completed,
                "overdue_since": task.due_date.date().isoformat(),  # Add overdue date
            })

        today_str = today.date().isoformat()
        if today_str not in tasks_by_date:
            tasks_by_date[today_str] = {"due_tasks": [], "overdue": False}
        tasks_by_date[today_str]["due_tasks"].extend(overdue_task_data)

        # Add empty entries for dates with no tasks
        current_date = today
        while current_date <= end_date:
            date_str = current_date.date().isoformat()
            if date_str not in tasks_by_date:
                tasks_by_date[date_str] = {
                    "due_tasks": [],
                    "overdue": False
                }
            current_date += timedelta(days=1)

        return Response({
            "tasks_by_date": tasks_by_date,
            "start_date": today.date().isoformat(),
            "end_date": end_date.date().isoformat()
        }, status=status.HTTP_200_OK)


#View History of completed tasks
class CompletedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            # Parse the date from URL parameter
            date = parse_date(date_str)
            if not date:
                raise ValueError
            
            # Convert to datetime range for the full day
            start_date = make_aware(datetime.combine(date, datetime.min.time()))
            end_date = make_aware(datetime.combine(date, datetime.max.time()))
            
            # Filter tasks completed on the specified date
            completed_tasks = TaskToCheck.objects.filter(
                completed_at__range=(start_date, end_date),
                is_completed=True,
                user_plant_task__user_plant__user=request.user
            ).select_related('user_plant_task__user_plant')  # Optimize database queries
            
            # Serialize the tasks
            task_data = [
                {
                    'id': task.id,
                    'task_name': task.user_plant_task.name,
                    'plant_name': task.user_plant_task.user_plant.nickname or task.user_plant_task.user_plant.plant.species_name,
                    'completed_at': task.completed_at,
                }
                for task in completed_tasks
            ]

            return Response(task_data, status=status.HTTP_200_OK)
                
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# Add a UserPlantTask (predefined choices)
class AddUserPlantTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, userPlant_id):
        try:
            plant = UserPlant.objects.get(pk=userPlant_id, user=request.user)
        except UserPlant.DoesNotExist:
            return Response({"error": "Plant not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        task_data = {
            'user': request.user.id,
            'user_plant': plant.id,  # Correct the field name
            'name': request.data.get('name'),
            'description': request.data.get('description', ''),
            'interval': request.data.get('interval'),
            'unit': request.data.get('unit'),
            'last_completed_at': request.data.get('last_completed_at')
        }

        # Parse and validate last_completed_at if provided
        if task_data['last_completed_at']:
            try:
                task_data['last_completed_at'] = datetime.fromisoformat(task_data['last_completed_at'])
                if task_data['last_completed_at'] > now():
                    raise ValueError("last_completed_at cannot be in the future.")
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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


class UserPlantTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userPlant_id):
        try:
            plant = UserPlant.objects.get(pk=userPlant_id, user=request.user)
            tasks = UserPlantTask.objects.filter(user_plant=plant)
            serializer = UserPlantTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except UserPlant.DoesNotExist:
            return Response(
                {"error": "Plant not found or not owned by user"},
                status=status.HTTP_404_NOT_FOUND
            )


#Update frequency of UserPlantTask (Doesn't affect current instance of TaskToCheck)
class UpdateTaskFrequencyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, task_id):
        try:
            # Retrieve the UserPlantTask to update
            task = UserPlantTask.objects.get(pk=task_id, user_plant__user=request.user)
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
            # Retrieve the task ensuring it belongs to the authenticated user's plant
            task = UserPlantTask.objects.get(
                pk=task_id,
                user_plant__user=request.user  # Ensure the task's plant belongs to the user
            )
        except UserPlantTask.DoesNotExist:
            return Response(
                {"error": "Task not found or not owned by user"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete all related TaskToCheck instances
        TaskToCheck.objects.filter(user_plant_task=task).delete()

        # Delete the UserPlantTask itself
        task.delete()

        return Response(
            {"message": "Task and its related check tasks have been successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )


# marking tasks as completed and creating the next cycle is encapsulated within the model 
# while the view simply triggers this process and handles the response
class MarkTaskAsCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            # Retrieve the task to be marked as completed
            task = TaskToCheck.objects.get(pk=task_id, user_plant_task__user_plant__user=request.user)
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


class UpdateLastCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        try:
            # Retrieve the UserPlantTask instance
            task = UserPlantTask.objects.get(pk=task_id, user_plant__user=request.user)
        except UserPlantTask.DoesNotExist:
            return Response({"error": "Task not found or not owned by user."}, status=status.HTTP_404_NOT_FOUND)

        # Partially update the task
        serializer = UserPlantTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            updated_task = serializer.save()

            # Recalculate due_date for the current TaskToCheck
            current_task = TaskToCheck.objects.filter(user_plant_task=updated_task, is_completed=False).first()
            if current_task:
                current_task.due_date = updated_task.calculate_next_due_date()
                current_task.save()

            return Response(
                {
                    "message": "Last completed date updated and current task due date recalculated successfully.",
                    "task": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
from .models import UserPlant, Plant, Site, UserPlantTask, TaskToCheck

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'species_name', 'scientific_name', 'description']


class UserPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlant
        fields = ['id', 'plant', 'nickname', 'site', 'added_at']

    def create(self, validated_data):
        user = self.context['request'].user  # Get the user from the request context
        # Create and return the new UserPlant instance
        return UserPlant.objects.create(user=user, **validated_data)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'light', 'location']


class UserPlantTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlantTask
        fields = ['id', 'name', 'plant', 'description', 'interval', 'unit']


class TaskToCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskToCheck
        fields = ['id', 'user_plant_task', 'due_date', 'is_completed', 'completed_at']
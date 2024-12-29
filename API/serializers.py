from rest_framework import serializers
from .models import UserPlant, Plant, Site, UserPlantTask, TaskToCheck

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'species_name', 'scientific_name', 'description']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'light', 'location']

class UserPlantSerializer(serializers.ModelSerializer):
    site = SiteSerializer()  # Serialize the site as a nested object
    plant = PlantSerializer()  # Serialize the plant as a nested object

    class Meta:
        model = UserPlant
        fields = ['id', 'plant', 'nickname', 'site', 'added_at', 'image']

    def create(self, validated_data):
        user = self.context['request'].user  # Get the user from the request context
        return UserPlant.objects.create(user=user, **validated_data)


class UserPlantTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlantTask
        fields = ['id', 'name', 'description', 'last_completed_at', 'interval', 'unit', 'user_plant']

    def update(self, instance, validated_data):
        # Update the UserPlantTask instance
        instance.last_completed_at = validated_data.get('last_completed_at', instance.last_completed_at)
        instance.save()

        # Recalculate the due date for the current TaskToCheck instance
        current_task = TaskToCheck.objects.filter(user_plant_task=instance, is_completed=False).first()
        if current_task:
            current_task.due_date = instance.calculate_next_due_date()
            current_task.save()

        return instance

class TaskToCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskToCheck
        fields = ['id', 'user_plant_task', 'due_date', 'is_completed', 'completed_at']
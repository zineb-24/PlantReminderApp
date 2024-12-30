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
    site = SiteSerializer(read_only=True)  # Use SiteSerializer for nested read-only
    plant = PlantSerializer(read_only=True)  # Use PlantSerializer for nested read-only
    site_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all(),
        write_only=True,
        source='site',  # Map `site_id` to `site`
    )

    class Meta:
        model = UserPlant
        fields = ['id', 'plant', 'nickname', 'site', 'site_id', 'added_at', 'image']

    def create(self, validated_data):
        user = self.context['request'].user  # Get the user from the request context
        return UserPlant.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # Handle `site` updates via `site_id`
        site_instance = validated_data.pop('site', None)
        if site_instance:
            instance.site = site_instance

        # Update the remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        print("Validated data:", validated_data)
        print("Instance site before save:", instance.site)

        # Save the instance
        instance.save()
        return instance

    
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
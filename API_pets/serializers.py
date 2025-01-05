from rest_framework import serializers
from .models import UserPet, Pet


class UserPetSerializer(serializers.ModelSerializer):

    pet_details = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()

    class Meta:
        model = UserPet
        fields = ['id', 'nickname', 'birth_date', 'age', 'image', 'pet_details']

    def get_pet_details(self, obj):
        return {
            'species_name': obj.pet.species_name,
            'breed_name': obj.pet.breed_name,
            'scientific_name': obj.pet.scientific_name,
            'lifespan': obj.pet.lifespan,
            'daily_sleep': obj.pet.daily_sleep,
            'gestation': obj.pet.gestation,
            'description': obj.pet.description,
            'diet': obj.pet.diet,
            'image': obj.pet.image.url if obj.pet.image else None,
        }


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = [
            'id', 'species_name', 'breed_name', 'scientific_name', 
            'lifespan', 'daily_sleep', 'gestation', 'description', 
            'diet', 'image'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .models import UserPet, Pet
from django.http import JsonResponse
from rest_framework.views import APIView
from .serializers import UserPetSerializer, PetSerializer


class UserPetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = UserPet.objects.filter(user=request.user)
        serializer = UserPetSerializer(queryset, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)


class UserPetSpeciesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get unique species from user's pets
        user_pets = UserPet.objects.filter(user=request.user)
        species_names = Pet.objects.filter(
            id__in=user_pets.values_list('pet', flat=True)
        ).values_list('species_name', flat=True).distinct()
        
        # Get one pet record for each unique species
        user_species = []
        for species_name in species_names:
            species = Pet.objects.filter(species_name=species_name).first()
            if species:
                user_species.append(species)
        
        serializer = PetSerializer(user_species, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
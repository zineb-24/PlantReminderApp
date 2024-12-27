from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # In Basic Auth, the credentials are passed directly in the request
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            raise AuthenticationFailed('Email and password are required!')

        user = authenticate(username=email, password=password)  # Authenticate user

        if user is None:
            raise AuthenticationFailed('Invalid credentials')

        # Return user data on successful authentication
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # With Basic Authentication, `request.user` will automatically be populated
        user = request.user  # Get the authenticated user

        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        # Clear the session for the user to log out
        request.user.auth_token.delete()  # Or clear the session cookie if using session authentication
        response = Response()
        response.data = {
            'message': 'Successfully logged out'
        }
        return response
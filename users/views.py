from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Received registration request with data:", request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("Registration successful:", serializer.data)
            return Response(serializer.data, status=201)
        else:
            print("Registration failed with errors:", serializer.errors)
            return Response(serializer.errors, status=400)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Log request details
        print("Login request received")
        print(f"Email: {request.data.get('email')}")
        print(f"Password length: {len(request.data.get('password', ''))}")  # Avoid printing actual password

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            print("Missing email or password")
            raise AuthenticationFailed('Email and password are required!')

        user = authenticate(username=email, password=password)

        if user is None:
            print(f"Authentication failed for email: {email}")
            raise AuthenticationFailed('Invalid credentials')

        # Log successful authentication
        print(f"User authenticated: {user.username}")

        serializer = UserSerializer(user)
        response_data = serializer.data
        print(f"Login response data: {response_data}")

        return Response(response_data)



class UserView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # With Basic Authentication, `request.user` will automatically be populated
        user = request.user  # Get the authenticated user

        serializer = UserSerializer(user)
        return Response(serializer.data)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"Logout request received from user: {request.user.username}")

        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
                print(f"Auth token deleted for user: {request.user.username}")
            else:
                print(f"No auth token found for user: {request.user.username}")
        except Exception as e:
            print(f"Error during logout: {e}")
            return Response({'error': str(e)}, status=500)

        return Response({'message': 'Successfully logged out'})


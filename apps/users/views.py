from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, CustomLoginSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User = get_user_model()

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'access': str(refresh.access_token),
            'refresh': str(refresh)

        }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User Registration successful",
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'access': str(refresh.access_token)

        }, status=status.HTTP_201_CREATED)

class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        response_data = serializer.data.copy()
        response_data["message"] = "User profile loaded successfully"
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        response_data = serializer.data.copy()
        response_data["message"] = "User profile updated successfully"
        return Response(response_data, status=status.HTTP_200_OK)
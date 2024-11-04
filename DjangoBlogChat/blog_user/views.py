from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from blog_user.serializers import (
    RegistrationSerializer,
    AuthorizationSerializer,
    )

class Register_User(generics.CreateAPIView):

    """Endpoint for user registration"""

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        """Check validation of form, create user"""

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Login_User(generics.GenericAPIView):

    """Endpoint for user authentication"""

    serializer_class = AuthorizationSerializer

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        })
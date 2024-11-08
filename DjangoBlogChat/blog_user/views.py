from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


from django.db import IntegrityError

from blog_user.serializers import (
    RegistrationSerializer,
    AuthorizationSerializer,
    )

from blog_user.models import BlogUser


class Register_User(generics.CreateAPIView):

    """Endpoint for user registration"""

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():

            errors = serializer.errors

            formatted_errors = {}

            for field, error_list in errors.items():

                for i, e in enumerate(error_list):
                    match e:
                        case 'blog user with this nickname already exists.':

                            error_list[i] = 'User with this nickname already exists.'

                        case 'blog user with this email already exists.':

                            error_list[i] = 'User with this email already exists.'

                formatted_errors[field] = " ".join(error_list)

            return Response(
                {"errors": formatted_errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Login_User(generics.GenericAPIView):

    """Endpoint for user authentication"""

    serializer_class = AuthorizationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():

            errors = serializer.errors

            nickname_error = errors.get('nickname', [])

            if nickname_error:

                nickname_error_msg = str(nickname_error[0])

                if nickname_error_msg in ['User does not exist.', 'This field is required.']:

                    return Response({'errors': {'nickname': nickname_error_msg}}, status=status.HTTP_404_NOT_FOUND)

            password_error = errors.get('password', [])

            if password_error and str(password_error[0]) == 'Wrong password.':

                return Response({'errors': {'password': 'Wrong password.'}}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        user_data = BlogUser.objects.get(nickname=str(user))

        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            "user": {
                "username": user_data.username,
                "nickname": user_data.nickname,
                "pk": user_data.pk,
                "email": user_data.email
            }
        })

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


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None and isinstance(exc, ValidationError):

        for field, messages in response.data.items():
            if isinstance(messages, list):
                response.data[field] = ' '.join(messages)

        response.data = {"errors": response.data}

    if isinstance(exc, ValidationError):
        print(response.data)
        errors = response.data.get('errors')
        print(errors)
        if errors.get('email') == "User with this email already exists":

            response = Response(response.data,
                status=status.HTTP_409_CONFLICT
            )

            return response

        if errors.get('nickname') == "User with this nickname already exists":

            response = Response(response.data,
                status=status.HTTP_409_CONFLICT
            )

            return response

        return response

class Register_User(generics.CreateAPIView):

    """Endpoint for user registration"""

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        """Check validation of form, create user"""

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            print(errors)

            if errors.get("password"):
                data = {"password": errors["password"][0]}
                return Response({"errors": data}, status=status.HTTP_400_BAD_REQUEST)

            if errors.get("nickname"):
                error = 'error'
                if errors['nickname'][0] == 'blog user with this nickname already exists.':
                    error = 'User with this nickname already exists'
                data = {"nickname": error}
                return Response({"errors": data}, status=status.HTTP_409_CONFLICT)

            if errors.get("email"):
                error = 'error'
                if errors['email'][0] == 'blog user with this email already exists.':
                    error = 'User with this email with this email already exists'
                if errors['email'][0] == 'This field is required.':
                    error = 'This field is required.'
                data = {"email": error}
                return Response({"errors": data}, status=status.HTTP_409_CONFLICT)

            if errors.get("username"):
                error = 'error'
                if errors['username'][0] == 'This field is required.':
                    error = 'This field is required.'
                data = {"username": error}
                return Response({"errors": data}, status=status.HTTP_409_CONFLICT)

            if errors.get("confirm_password"):
                data = {"confirm_password": errors["confirm_password"][0]}
                return Response({"errors": data}, status=status.HTTP_409_CONFLICT)

            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

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
            print(errors)
            if errors.get('nickname'):

                nickname_error = str(errors['nickname'][0])
                print(nickname_error)
                if nickname_error == 'User does not exist.':
                    return Response({'errors': {'nickname': 'User does not exist.'}}, status=status.HTTP_404_NOT_FOUND)
                if nickname_error == 'This field is required.':
                    return Response({'errors': {'nickname': 'This field is required.'}}, status=status.HTTP_404_NOT_FOUND)

            if errors.get('password'):

                password_error = str(errors['password'][0])
                if password_error == 'Wrong password.':
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
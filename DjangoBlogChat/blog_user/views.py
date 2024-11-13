import random

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


from django.db import IntegrityError
from django.core.cache import cache
from django.core.mail import send_mail

from blog_user.serializers import (
    RegistrationSerializer,
    AuthorizationSerializer,
    RegistrationConfirmSerializer,
    RequestPasswordRecoverySerializer,
    PasswordRecoverySerializer
    )

from blog_user.models import BlogUser


class Register_User(generics.CreateAPIView):

    """Endpoint for user registration"""

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            user_data = serializer.validated_data

            code = random.randint(100000,999999)

            cache.set(code, user_data, timeout=180)

            request.session['user_data'] = user_data

            send_mail(
                'Registration code',
                f"Here is the code for registration: {code} and here is the link for this action: http://localhost:4200/confirm",
                'plextaskmanager@gmail.com',
                [f'{user_data.get('email')}']
            )

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

        return Response({"message": "Please check your email for confirmation."}, status=status.HTTP_200_OK)


class Register_Confirm(generics.GenericAPIView):

    """Endpoint for code confirm"""

    serializer_class = RegistrationConfirmSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            code = serializer.data.get('code')

            user_data = cache.get(code)

            if user_data:

                if BlogUser.objects.filter(email=user_data['email']).exists():
                    return Response({"errors": {"message": "Email is already taken."}},
                                    status=status.HTTP_400_BAD_REQUEST)

                if BlogUser.objects.filter(nickname=user_data['nickname']).exists():
                    return Response({"errors": {"message": "Nickname is already taken."}},
                                    status=status.HTTP_400_BAD_REQUEST)

                user = BlogUser.objects.create_user(
                        nickname=user_data['nickname'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password']
                    )

                cache.delete(code)

                return Response({"message": "Registration successfully."}, status=status.HTTP_200_OK)

            else:

                return Response({"errors": {"message": "Wrong code."}}, status=status.HTTP_400_BAD_REQUEST)


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


class Request_Password_Recovery(generics.GenericAPIView):

    """Endpoint for code confirm"""

    serializer_class = RequestPasswordRecoverySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
        
            user_data = serializer.validated_data

            print(user_data)

            recovery_code = random.randint(100000,999999)

            cache.set(recovery_code, user_data, timeout=180)

            request.session['user_data'] = user_data

            send_mail(
                'Registration code',
                f"Here is the code for password recovery: {recovery_code} and here is the link for this action: http://localhost:4200/recovery",
                'plextaskmanager@gmail.com',
                [f'{user_data.get('email')}']
            )

            return Response({"message": "We sent to you password recovery code."}, status=status.HTTP_200_OK)

        errors = serializer.errors

        formatted_errors = {}

        for field, error in errors.items():
            formatted_errors[field] = error[0]

        print(formatted_errors)

        return Response({"errors": formatted_errors}, status=400)


class Password_Recovery(generics.GenericAPIView):

    """Endpoint for code confirm"""

    serializer_class = PasswordRecoverySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            recovery_code = serializer.data.get('code')

            password = serializer.data.get('password')
            print(password)
            user_data = cache.get(recovery_code)

            if user_data:

                try:

                    user = BlogUser.objects.get(email=user_data['email'])

                except BlogUser.DoesNotExist:

                    return Response({"errors": {"message": "User with this email does not exist."}},
                                    status=status.HTTP_404_NOT_FOUND)
                print(user)
                user.set_password(password)

                user.save()

                cache.delete(recovery_code)

                return Response({"message": "Password successfully changed."}, status=status.HTTP_200_OK)

            else:

                return Response({"errors": {"message": "Invalid code."}}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# {
#     "email": "daniilworkmail49@gmail.com"
# }

# {
#     "code": 308589,
#     "password": "password1%",
#     "confirm_password": "password1%"
# }

{
    "username": "test_user",
    "nickname": "testy_name1535235",
    "email": "gmail151251253523512412412@gmail.com",
    "password": "password1%",
    "confirm_password": "password1%"
}
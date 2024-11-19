import random

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.core.mail import send_mail

from blog_user.models import BlogUser

class RegistrationService:

    def __init__(self, user_data):

        self.user_data = user_data

        self.code = random.randint(100000, 999999)

    def send_confirmation_email(self):

        send_mail(
            'Registration code',
            f"Here is the code for registration: {self.code} and here is the link for this action: http://localhost:4200/confirm",
            'plextaskmanager@gmail.com',
            [self.user_data.get('email')]
        )

    def cache_user_data(self):

        cache.set(self.code, self.user_data, timeout=180)


class RegisterUser:

    def __init__(self, serializer_data):

        self.user_data = serializer_data

    def execute(self):

        registration_service = RegistrationService(self.user_data)
        registration_service.cache_user_data()
        registration_service.send_confirmation_email()


class RegistrationConfirmationService:

    def __init__(self, code, user_data):
        self.code = code
        self.user_data = user_data

    def check_code(self):

        cached_data = cache.get(self.code)
        if not cached_data:
            raise ValueError("Invalid code")
        return cached_data

    def check_if_user_exists(self):

        if BlogUser.objects.filter(email=self.user_data['email']).exists():
            raise ValueError("Email is already taken.")
        
        if BlogUser.objects.filter(nickname=self.user_data['nickname']).exists():
            raise ValueError("Nickname is already taken.")

    def create_user(self):

        return BlogUser.objects.create_user(
            nickname=self.user_data['nickname'],
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

    def execute(self):

        user_data = self.check_code()
        self.check_if_user_exists()
        new_user = self.create_user()
        cache.delete(self.code)
        return new_user


class AuthenticationService:

    def __init__(self, user_data):
        self.nickname = user_data.get('nickname')
        self.password = user_data.get('password')

    def validate_user(self):

        try:

            user = BlogUser.objects.filter(email=self.nickname).first()

        except Errors:

            try:

                user = BlogUser.objects.filter(nickname=self.nickname).first()

            except Errors:

                raise Exception('User does not exist.')

        try:

            user = authenticate(nickname=user, password=self.password)

        except Errors:

            try:

                user = authenticate(nickname=user, password=self.password)

            except Errors:

                raise Exception('Wrong password.')

        if not user:

            raise Exception('Wrong password.')

        return user

    def generate_tokens(self, user):

        refresh = RefreshToken.for_user(user)

        return str(refresh), str(refresh.access_token)

    def execute(self):

        user = self.validate_user()
        refresh_token, access_token = self.generate_tokens(user)

        return user, refresh_token, access_token


class RequestPasswordRecoveryService:

    def __init__(self, user_data):
        self.user_data = user_data
        self.recovery_code = random.randint(100000, 999999)

    def cache_recovery_code(self):

        cache.set(self.recovery_code, self.user_data, timeout=180)

    def send_recovery_email(self):

        send_mail(
            'Password Recovery Code',
            f"Here is the code for password recovery: {self.recovery_code} and here is the link for this action: http://localhost:4200/recovery",
            'plextaskmanager@gmail.com',
            [self.user_data.get('email')]
        )

    def execute(self):

        self.cache_recovery_code()
        self.send_recovery_email()

        return self.recovery_code


class PasswordRecoveryService:

    def __init__(self, recovery_code, new_password):

        self.recovery_code = recovery_code

        self.new_password = new_password

    def validate_code(self):

        user_data = cache.get(self.recovery_code)

        if not user_data:

            raise ValueError("Invalid code")

        return user_data

    def get_user(self, email):

        try:

            return BlogUser.objects.get(email=email)

        except ObjectDoesNotExist:

            raise ValueError("User with this email does not exist.")

    def change_password(self, user):

        user.set_password(self.new_password)

        user.save()

    def execute(self):

        user_data = self.validate_code()
        user = self.get_user(user_data['email'])
        self.change_password(user)
        cache.delete(self.recovery_code)
        return user


from blog_user.models import BlogUser


def get_user_by_request(request_user):

    try:

        user = BlogUser.objects.get(nickname=str(request_user))

    except BlogUser.DoesNotExist:

        return None

    return user
import random
import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Count
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from authify.models import Clerbie
from chat.models import ChatRoom

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


class RegisterUserUtil:

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

        if Clerbie.objects.filter(email=self.user_data['email']).exists():
            raise ValueError("Email is already taken.")
        
        if Clerbie.objects.filter(nickname=self.user_data['nickname']).exists():
            raise ValueError("Nickname is already taken.")

    def create_user(self):

        return Clerbie.objects.create_user(
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
            user = Clerbie.objects.get(email=self.nickname)

        except Exception:
            try:
                user = Clerbie.objects.get(nickname=self.nickname)
            except Exception:
                raise Exception('User does not exist.')

        try:
            user = authenticate(nickname=user, password=self.password)

        except Exception:
            try:
                user = authenticate(nickname=user, password=self.password)
            except Exception:
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
            return Clerbie.objects.get(email=email)
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


def set_tokens_in_cookies(response, refresh_token):

    response.set_cookie(
        'refreshToken', refresh_token,
        httponly=True,
        secure=True,
        samesite='Lax',
        max_age=3600*24*21
    )

def get_user_by_request(request_user):

    try:
        user = Clerbie.objects.get(nickname=str(request_user))
    except Clerbie.DoesNotExist:
        return None
    return user


def validate_password_strength(password):
    """
    Ensure the password meets specific strength requirements:
    - At least 8 characters
    - Contains at least one digit
    - Contains at least one special character
    """

    pattern = r'^(?=.*[!@#$%^&()+}{":;\'?/>.<,`~])(?=.*\d)[^\s]{8,}$'

    if not re.match(pattern, password):
        raise ValidationError(
            {
            "password": "Password must be at least 8 characters long, contain at least one digit, "
            "contain at least one special character, and not have any spaces."
            }
        )

def validate_passwords_match(new_password, confirm_password):
    """Ensure the password and confirm password fields match."""
    if new_password != confirm_password:
        raise ValidationError({"confirm_password": "Passwords must match."})

def check_current_password(user, current_password):
    """Ensure the current password matches the user's password."""
    if not user.check_password(current_password):
        raise ValidationError({"current_password": "Current password is incorrect."})

def delete_relation_single_chat(user):

    chat_rooms_to_delete = ChatRoom.objects.filter(users=user).annotate(user_count=Count('users')).filter(user_count=2)
    chat_rooms_to_delete.delete()


def receive_user_data_delete_chats(user, password):

    '''Stage 1: Delete user | Return user's data | Delete all single chat with this user.'''

    username, nickname, email, role, user_id = user.username, user.nickname, user.email, user.role, user.id
    delete_relation_single_chat(user=user)
    user.nickname = 'deleted'
    user.email = 'deleted@gmail.com'

    user.save()
    user.delete()

    return username, nickname, email, password, role, user_id


def get_reset_response(auth_service, new_user):

    refresh_token, access_token = auth_service.generate_tokens(new_user)

    response = Response({
        "access_token": access_token,
        "user": {
            "username": new_user.username,
            "nickname": new_user.nickname,
            "pk": new_user.pk,
            "email": new_user.email
        }
    })
    set_tokens_in_cookies(response=response, refresh_token=str(refresh_token))

    return response


def create_reset_user(user,validated_password):

    '''Stage 2: Create new user | Return user's data'''

    username, nickname, email, password, role, user_id = receive_user_data_delete_chats(user, validated_password)
    new_user = Clerbie.objects.create_user(
        id=user_id, username=username, nickname=nickname, email=email, password=password, role=role
    )
    user_data = {"nickname": new_user.nickname, "password": new_user.password}
    auth_service = AuthenticationService(user_data)

    return auth_service, new_user
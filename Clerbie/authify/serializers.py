import re
from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.http import JsonResponse
from django.contrib.auth import authenticate

from authify.models import Clerbie
from authify.choices import USER_ROLE_CHOICES
from authify.choices import ACCOUNT_STATUS_CHOICES

from authify.utils import (
    check_password,
    check_current_password,
    validate_passwords_match, 
    validate_password_strength,
)

class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, help_text="The user's password.")

    confirm_password = serializers.CharField(write_only=True, help_text="Confirm the user's password.")

    """
    Serializer for user registration.
    Validates that the user's nickname, email, and password meet specific criteria.
    Passwords must match and must meet strength requirements.
    """

    class Meta:

        model = Clerbie

        fields = ['nickname', 'username', 'email', 'password', 'confirm_password']
        help_texts = {
            'nickname': 'Unique nickname for the user.',
            'username': 'User’s full name.',
            'email': 'User’s email address.',
        }

    def validate_nickname(self, value):

        """Ensure the nickname is unique and doesn't exist in the database."""

        if Clerbie.objects.filter(nickname=value).exists():

            raise serializers.ValidationError("User with this nickname already exists.")

        return value

    def validate_email(self, value):

        """Ensure the email is valid and unique in the database."""

        email_pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'

        if not re.match(email_pattern, value):

            raise serializers.ValidationError("Invalid email format.")

        if Clerbie.objects.filter(email=value).exists():

            raise serializers.ValidationError("User with this email already exists.")

        return value

    def validate(self, attrs):

        validate_password_strength(attrs['password'])
        validate_passwords_match(attrs['password'], attrs['confirm_password'])

        return attrs

    def create(self, validated_data):

        """Create the user instance and set the password securely."""

        validated_data.pop('confirm_password')

        user = Clerbie(**validated_data)

        user.set_password(validated_data['password'])

        user.save()

        return user


class RegistrationConfirmSerializer(serializers.Serializer):

    """Serializer for confirming user registration with a confirmation code.
    Validates that the code is a 6-digit number.
    """

    code = serializers.IntegerField()

    def validate_code(self, value):

        if value < 100000 or value > 999999:

            raise serializers.ValidationError("Invalid Code.")

        return value


class AuthorizationSerializer(serializers.Serializer):

    """
    Serializer for user login.
    Validates the nickname and password for authentication.
    """

    nickname = serializers.CharField()

    password = serializers.CharField()

    def validate(self, attrs):

        """Validates the provided credentials (nickname and password)."""

        nickname = attrs.get('nickname')

        password = attrs.get('password')

        if nickname is None or password is None:

            raise serializers.ValidationError({
                                        "errors": {
                                            "nickname": "Field are required.",
                                            "password": "Field are required."
                                            }
                                        })

        user = authenticate(username=nickname, password=password)

        if user is None:

            try:

                user = Clerbie.objects.get(email=nickname)

            except Clerbie.DoesNotExist:

                try:

                    user = Clerbie.objects.get(nickname=nickname)

                except Clerbie.DoesNotExist:

                    raise serializers.ValidationError({"nickname": "User does not exist."})

            if not user.check_password(password):

                raise serializers.ValidationError({'password': 'Wrong password.'})

        attrs['user'] = user

        return attrs


class LogoutResponseSerializer(serializers.Serializer):

    message = serializers.CharField(default='You don\'t need submit any data. Only <<refreshToken>> cookie')


class RequestPasswordRecoverySerializer(serializers.Serializer):

    email = serializers.EmailField()

    """
    Serializer for requesting a password recovery code.
    Validates that the email exists in the database.
    """
    
    def validate_email(self, value):

        """ Ensure the provided email is associated with an existing user."""

        try:

            user = Clerbie.objects.get(email=value)

        except Clerbie.DoesNotExist:

            raise serializers.ValidationError("User with this email does not exist.")

        return value


class PasswordRecoverySerializer(serializers.Serializer):

    """
    Serializer for confirming password recovery.
    Validates the recovery code, new password, and password confirmation.
    """

    code = serializers.IntegerField()

    password = serializers.CharField()

    confirm_password = serializers.CharField()

    def validate_password(self, value):

        """Ensure the new password meets the strength requirements."""

        pattern = r'^(?=.*[!@#$%^&()+}{":;\'?/>.<,`~])(?=.*\d)[^\s]{8,}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, contain at least one digit, "
                "contain at least one special character, and not have any spaces."
            )

        return value

    def validate_code(self, value):

        """Ensure the recovery code is a valid 6-digit number."""

        if value < 100000 or value > 999999:

            raise serializers.ValidationError("Invalid Code.")

        return value

    def validate(self, attrs):

        """Ensure the password and confirm password fields match."""

        if attrs['password'] != attrs['confirm_password']:

            raise serializers.ValidationError({"confirm_password": "Passwords must match."})

        return attrs


class GetUserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring Clerbie data, including related models for friends, hobbies, education, certificates, work experience, etc.
    """

    avatar = serializers.CharField(required=False, allow_null=True)
    nickname = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=USER_ROLE_CHOICES)
    status = serializers.ChoiceField(choices=ACCOUNT_STATUS_CHOICES)


    class Meta:
        model = Clerbie
        fields = [
            'id',
            'username',
            'avatar',
            'nickname',
            'email',
            'role',
            'status'
        ]


class ChangePasswordSerializer(serializers.Serializer):

    '''Serialize data for password changing'''

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):

        validate_passwords_match(attrs['new_password'], attrs['confirm_password'])
        user = self.context.get('user')
        if user:
            check_current_password(user, attrs['current_password'])
        validate_password_strength(attrs['new_password'])
        return attrs

    def update(self, instance, validated_data):

        user = instance
        user.set_password(validated_data['new_password'])
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):


    '''Deletes user from request'''

    class Meta:
        model = Clerbie
        fields = '__all__'

class ResetAccountSerializer(serializers.ModelSerializer):


    '''Deletes user from request'''

    class Meta:
        model = Clerbie
        fields = ['password']

    def validate(self, attrs):

        validate_password_strength(attrs['password'])
        check_password(self.context['request'].user,attrs['password'])
        return attrs

# TODO: BindEmail system

# class BingEmailSerializer(serializers.Serializer):

#     linked_email = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):

#         user = self.context.get('user')
#         if user:
#             check_current_password(user, attrs['current_password'])
#         validate_password_strength(attrs['new_password'])
#         return attrs
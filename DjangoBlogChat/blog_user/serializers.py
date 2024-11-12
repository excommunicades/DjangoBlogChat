import re

from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import JsonResponse

from django.contrib.auth import authenticate

from blog_user.models import BlogUser


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    confirm_password = serializers.CharField(write_only=True)

    """Serializer for user's registration"""
    class Meta:

        model = BlogUser

        fields = ['nickname', 'username', 'email', 'password', 'confirm_password']

    def validate_nickname(self, value):

        """checks username for uniqueness in db"""

        if BlogUser.objects.filter(nickname=value).exists():

            raise serializers.ValidationError("User with this nickname already exists.")

        return value

    def validate_email(self, value):

        """checks email for uniqueness in db"""

        email_pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'

        if not re.match(email_pattern, value):

            raise serializers.ValidationError("Invalid email format.")

        if BlogUser.objects.filter(email=value).exists():

            raise serializers.ValidationError("User with this email already exists.")

        return value

    def validate_password(self, value):

        """Validates the password strength"""

        pattern = r'^(?=.*[!@#$%^&()+}{":;\'?/>.<,`~])(?=.*\d)[^\s]{8,}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, contain at least one digit, "
                "contain at least one special character, and not have any spaces."
            )

        return value

    def validate(self, attrs):

        """Check if passwords match"""

        if attrs['password'] != attrs['confirm_password']:

            raise serializers.ValidationError({"confirm_password": "Passwords must match."})

        return attrs

    def create(self, validated_data):

        """Create the user instance and set the password"""

        validated_data.pop('confirm_password')

        user = BlogUser(**validated_data)

        user.set_password(validated_data['password'])

        user.save()

        return user


class RegistrationConfirmSerializer(serializers.Serializer):

    """Serializer for code' request"""

    code = serializers.IntegerField()

    def validate_code(self, value):

        if value < 100000 or value > 999999:

            raise serializers.ValidationError("Invalid Code.")

        return value


class AuthorizationSerializer(serializers.Serializer):

    """Serializer for user's login request"""

    nickname = serializers.CharField()

    password = serializers.CharField()

    def validate(self, attrs):

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

                user = BlogUser.objects.get(email=nickname)

            except BlogUser.DoesNotExist:

                try:

                    user = BlogUser.objects.get(nickname=nickname)

                except BlogUser.DoesNotExist:

                    raise serializers.ValidationError({"nickname": "User does not exist."})

            if not user.check_password(password):

                raise serializers.ValidationError({'password': 'Wrong password.'})

        attrs['user'] = user

        return attrs


class RequestPasswordRecoverySerializer(serializers.Serializer):

    email = serializers.EmailField()

    """Serializer for user's registration"""

    def validate_email(self, value):

        try:

            user = BlogUser.objects.get(email=value)

        except BlogUser.DoesNotExist:

            raise serializers.ValidationError("User with this email does not exist.")

        return value


class PasswordRecoverySerializer(serializers.Serializer):

    code = serializers.IntegerField()

    password = serializers.CharField(write_only=True)

    confirm_password = serializers.CharField(write_only=True)

    """Serializer for user's registration"""

    def validate_password(self, value):

        """Validates the password strength"""

        pattern = r'^(?=.*[!@#$%^&()+}{":;\'?/>.<,`~])(?=.*\d)[^\s]{8,}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, contain at least one digit, "
                "contain at least one special character, and not have any spaces."
            )

        return value

    def validate_code(self, value):

        if value < 100000 or value > 999999:

            raise serializers.ValidationError("Invalid Code.")

        return value

    def validate(self, attrs):

        """Check if passwords match"""

        if attrs['password'] != attrs['confirm_password']:

            raise serializers.ValidationError({"confirm_password": "Passwords must match."})

        return attrs

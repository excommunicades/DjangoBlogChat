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

        if BlogUser.objects.filter(email=value).exists():

            raise serializers.ValidationError("User with this email already exists.")

        return value

    def validate_password(self, value):

        """Validates the password strength"""

        if len(value) < 8:

            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in value):

            raise serializers.ValidationError("Password must contain at least one digit.")

        if not any(not char.isalnum() for char in value):

            raise serializers.ValidationError("Password must contain at least one special character.")

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

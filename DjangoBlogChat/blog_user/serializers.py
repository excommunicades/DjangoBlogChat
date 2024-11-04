from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate

from blog_user.models import BlogUser


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    """Serializer for user's registration"""

    class Meta:

        """Initialization fields and models"""

        model = BlogUser

        fields = [
                'nickname',
                'username',
                'email',
                'password',
                'confirm_password',
                ]

    def validate_nickname(self, value):

        """chekcs username on unique in db"""

        if BlogUser.objects.filter(nickname=value).exists():

            raise serializers.ValidationError('User with this nickname already exists')

        return value

    def validate_email(self, value):

        """checks email on unique in db"""

        if BlogUser.objects.filter(email=value).exists():

            raise serializers.ValidationError('User with this email already exists')

        return value

    def validate_password(self, value):

        """Validates the password strength"""

        if len(value) < 8:

            raise serializers.ValidationError('Password must be at least 8 characters long.')

        has_digit = any(char.isdigit() for char in value)

        if not has_digit:

            raise serializers.ValidationError('Password must contain at least one digit.')

        has_special_char = any(not char.isalnum() for char in value)

        if not has_special_char:

            raise serializers.ValidationError('Password must contain at least one special character.')

        return value

    def validate(self, attrs):

        if attrs['password'] != attrs['confirm_password']:

            raise serializers.ValidationError("Passwords must match.")

        return attrs

    def create(self, validated_data):

        validated_data.pop('confirm_password')

        user = BlogUser(**validated_data)

        user.set_password(validated_data['password'])

        user.save()

        return user


class AuthorizationSerializer(serializers.Serializer):

    """Serializer for user's login request"""

    nickname_or_email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        
        nickname_or_email = attrs.get('nickname_or_email')
        password = attrs.get('password')

        if nickname_or_email is None or password is None:
            raise serializers.ValidationError('Both fields are required.')

        user = authenticate(username=nickname_or_email, password=password)

        if user is None:

            try:

                user = BlogUser.objects.get(email=nickname_or_email)

            except BlogUser.DoesNotExist:

                try:

                    user = BlogUser.objects.get(nickname=nickname_or_email)

                except BlogUser.DoesNotExist:

                    raise serializers.ValidationError({'nickname_or_email': 'User does not exist.'})

            if not user.check_password(password):

                raise serializers.ValidationError({'password': 'Wrong password.'})

        attrs['user'] = user

        return attrs

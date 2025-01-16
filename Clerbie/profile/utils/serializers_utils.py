import io
from PIL import Image
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from authify.models import Clerbie
from profile.models import (
    Clerbie_friends,
    Clerbie_hobbies,
    Clerbie_education,
    Clerbie_certificates,
    Clerbie_reactions,
    UserWorkExperience,
    Hobby,
    Education,
    Technologies,
    Work,
    UserWorkExperience,
    Certificates,
    Projects,
    Invitation,
    InboxMessage
)

from authify.choices import (
    USER_ROLE_CHOICES,
    GENDER_CHOICES,
    COUNTRIES,
    TIME_ZONES,
    ACCOUNT_STATUS_CHOICES,
    PROGRAMMING_ROLES_CHOICES,
)

class ClerbieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie
        fields = ['id', 'nickname', 'email', 'avatar']

class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ['name']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['name']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['name', 'description']

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWorkExperience
        fields = ['work', 'start_date', 'end_date', 'description']

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie_reactions
        fields = ['profile', 'reaction', 'review']

class TechnologiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technologies
        fields = [
            'id',
            'name',
            'description']

class ProjectSerializer(serializers.ModelSerializer):

    technologies = TechnologiesSerializer(many=True)
    users = ClerbieSerializer(many=True)
    creator = ClerbieSerializer(read_only=True)

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'technologies', 'users', 'creator']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['invite_code', 'project', 'user', 'status', 'created_at', 'expires_at']

class InboxMessageSerializer(serializers.ModelSerializer):
    invitation = InvitationSerializer()

    class Meta:
        model = InboxMessage
        fields = ['user', 'invitation', 'message', 'read', 'created_at']


def validate_avatar(self, value):
    valid_extensions = ['image/png', 'image/jpg', 'image/webp']
    if value.content_type not in valid_extensions:
        raise serializers.ValidationError('Allowed image formats: PNG, JPG, WebP.')

    if value.size > 1 * 1024 * 1024:  # 1 MB
        raise serializers.ValidationError('File size must not exceed 1MB.')

    image = Image.open(value)
    width, height = image.size

    if width < 50 or height < 50:
        raise serializers.ValidationError('Image must be at least 50x50 pixels.')

    if width > 200 or height > 200:
        image.thumbnail((200, 200))

        byte_io = io.BytesIO()
        image.save(byte_io, format='PNG' if value.content_type == 'image/png' else 'JPEG' if value.content_type == 'image/jpeg' else 'WEBP')
        byte_io.seek(0)

        if byte_io.tell() > 1 * 1024 * 1024:
            image.save(byte_io, format='PNG' if value.content_type == 'image/png' else 'JPEG' if value.content_type == 'image/jpeg' else 'WEBP', quality=85)
            byte_io.seek(0)
                
            if byte_io.tell() > 1 * 1024 * 1024:
                raise serializers.ValidationError('Compressed image size still exceeds 1MB.')

        value = InMemoryUploadedFile(
            byte_io,
            field_name=value.field_name,
            name=value.name,
            content_type=value.content_type,
            size=byte_io.tell(),
            charset=None
        )

    return value
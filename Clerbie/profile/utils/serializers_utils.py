import io
from PIL import Image
from rest_framework import serializers

from django.core.files.uploadedfile import InMemoryUploadedFile

from authify.models import Clerbie
from profile.models import (
    Offers,
    Projects,
    Companies,
    JobTitles,
    University,
    InboxMessage,
    Technologies,
    Clerbie_friends,
    Clerbie_education,
    Clerbie_reviews,
    UserJobExperience,
    Clerbie_certificates,
)


class FriendOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie_friends
        fields = [
            'id',
            'status',
            'user1',
            'user2',
            'expires_at',
            'offer_code',
            'description']

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name']

class EducationSerializer(serializers.ModelSerializer):

    university = UniversitySerializer()
    class Meta:
        model = Clerbie_education
        fields = ['id', 'user', 'university', 'specialty', 'started_at', 'ended_at']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie_certificates
        fields = ['id', 'title', 'photo', 'organization', 'issued_at', 'description']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ['id','name','photo', 'description']


class JobExperienceSerializer(serializers.ModelSerializer):

    company = CompanySerializer()
    class Meta:
        model = UserJobExperience
        fields = ['id','company','position', 'started_at','ended_at', 'description']


class JobTitlesSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobTitles
        fields = ['id', 'title']

class ClerbieSerializer(serializers.ModelSerializer):
    job_title = JobTitlesSerializer()
    class Meta:
        model = Clerbie
        fields = ['id', 'username', 'nickname', 'avatar', 'job_title'] # 'email'

class ReactionSerializer(serializers.ModelSerializer):

    user = ClerbieSerializer()

    class Meta:
        model = Clerbie_reviews
        fields = ['id', 'user', 'reaction', 'review']

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

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = ['offer_code', 'project', 'user', 'status', 'created_at', 'expires_at']

class InboxMessageSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()

    class Meta:
        model = InboxMessage
        fields = ['user', 'offer', 'message', 'read', 'created_at']


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


def validate_image_size(value):

    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError(f'File size must not exceed {max_size / (1024 * 1024)} MB.')

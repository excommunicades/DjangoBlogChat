import io
from PIL import Image
from rest_framework import serializers

from django.core.files.uploadedfile import InMemoryUploadedFile

from blog_user.choices import (
    USER_ROLE_CHOICES,
    GENDER_CHOICES,
    COUNTRIES,
    TIME_ZONES,
    ACCOUNT_STATUS_CHOICES,
    PROGRAMMING_ROLES_CHOICES,
    REACTIONS,
)
from blog_user.models import (
BlogUser,
BlogUser_friends,
BlogUser_hobbies,
BlogUser_education,
BlogUser_certificates,
BlogUser_reactions,
UserWorkExperience,
Hobby,
Education,
Technologies,
Work,
UserWorkExperience,
Certificates,
Projects,
)


class GetUserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring BlogUser data, including related models for friends, hobbies, education, certificates, work experience, etc.
    """

    avatar = serializers.CharField(required=False, allow_null=True)
    nickname = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=USER_ROLE_CHOICES)
    behavior_points = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    birthday = serializers.DateField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    country = serializers.ChoiceField(choices=COUNTRIES)
    time_zones = serializers.ChoiceField(choices=TIME_ZONES)
    status = serializers.ChoiceField(choices=ACCOUNT_STATUS_CHOICES)
    job_title = serializers.ChoiceField(choices=PROGRAMMING_ROLES_CHOICES, allow_null=True)
    two_factor_method = serializers.ChoiceField(choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')])
    
    # New "socials" field
    socials = serializers.SerializerMethodField()

    # Related fields for friends, hobbies, education, certificates, work experience, and reactions
    friends = serializers.SerializerMethodField()
    hobbies = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    work_experience = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = BlogUser
        fields = [
            'id',
            'username',
            'avatar',
            'nickname',
            'email',
            'role',
            'behavior_points',
            'gender',
            'birthday',
            'phone_number',
            'country',
            'time_zones',
            'status',
            'job_title',
            'two_factor_method',
            'socials',
            'friends',
            'hobbies',
            'education',
            'certificates',
            'work_experience',
            'reactions',
            'projects',
        ]
    def get_socials(self, obj):
        return {
            "telegram": obj.telegram,
            "linkedin": obj.linkedin,
            "github": obj.github,
            "instagram": obj.instagram,
            "skype": obj.skype,
            "discord": obj.discord,
            "website": obj.website,
            "facebook": obj.facebook,
            "youtube": obj.youtube,
            "business_email": obj.business_email
        }

    def get_friends(self, obj):
        friends = BlogUser_friends.objects.filter(user=obj)
        return BlogUserSerializer(friends, many=True).data
    
    def get_hobbies(self, obj):
        hobbies = BlogUser_hobbies.objects.filter(user=obj)
        return HobbySerializer(hobbies, many=True).data

    def get_education(self, obj):
        education = BlogUser_education.objects.filter(user=obj)
        return EducationSerializer(education, many=True).data

    def get_certificates(self, obj):
        certificates = BlogUser_certificates.objects.filter(user=obj)
        return CertificateSerializer(certificates, many=True).data

    def get_work_experience(self, obj):
        work_experience = UserWorkExperience.objects.filter(user=obj)
        return WorkExperienceSerializer(work_experience, many=True).data

    def get_reactions(self, obj):
        reactions = BlogUser_reactions.objects.filter(user=obj)
        return ReactionSerializer(reactions, many=True).data

    def get_projects(self, obj):
        projects = Projects.objects.filter(users=obj)
        return ProjectSerializer(projects, many=True).data

class BlogUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogUser
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
        model = BlogUser_reactions
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
    users = BlogUserSerializer(many=True)
    creator = BlogUserSerializer(read_only=True)

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'technologies', 'users', 'creator']

# class SetUserAvatarSerializer(serializers.ModelSerializer):

#     avatar = serializers.ImageField(required=True)

#     class Meta:

#         model = BlogUser
#         fields = ['avatar']


class UpdateGeneralDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogUser
        fields = [
            'username',
            'avatar',
            'gender',
            'birthday',
            'phone_number',
            'country',
            'time_zones',
            'business_email']

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


class SocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogUser
        fields = [
            'telegram', 
            'linkedin', 
            'github', 
            'instagram', 
            'skype', 
            'discord', 
            'website', 
            'facebook', 
            'youtube'
        ]



class CreateProjectSerializer(serializers.ModelSerializer):

    technologies = TechnologiesSerializer(many=True, required=False)

    class Meta:
        model = Projects
        fields = ['name', 'description', 'technologies']

    def create(self, validated_data):

        user = self.context['request'].user
        technologies_data = validated_data.pop('technologies', [])

        project = Projects.objects.create(creator=user, **validated_data)

        for tech_data in technologies_data:
            tech_name = tech_data.get('name')
            technology, created = Technologies.objects.get_or_create(name=tech_name)
            project.technologies.add(technology)

        project.users.add(user)

        return project
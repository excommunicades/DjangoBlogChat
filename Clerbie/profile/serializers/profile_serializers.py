from datetime import date
from rest_framework import serializers

from django.core.validators import FileExtensionValidator
from django.db.models import Q

from authify.models import Clerbie
from profile.models import (
    Offers,
    Projects,
    Companies,
    University,
    Technologies,
    Clerbie_friends,
    Clerbie_education,
    Clerbie_reactions,
    UserJobExperience,
    Clerbie_certificates,
)

from authify.choices import (
    COUNTRIES,
    TIME_ZONES,
    GENDER_CHOICES,
    USER_ROLE_CHOICES,
    ACCOUNT_STATUS_CHOICES,
    PROGRAMMING_ROLES_CHOICES,
)
from profile.utils.serializers_utils import (
    ProjectSerializer,
    ClerbieSerializer,
    ReactionSerializer,
    validate_image_size,
    EducationSerializer,
    CertificateSerializer,
    TechnologiesSerializer,
    JobExperienceSerializer,
)

class GetUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring Clerbie data, including related models for friends, hobbies, education, certificates, work experience, etc.
    """

    avatar = serializers.CharField(required=False, allow_null=True)
    nickname = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    about_me = serializers.CharField()
    technologies = TechnologiesSerializer(many=True)
    role = serializers.ChoiceField(choices=USER_ROLE_CHOICES)
    behavior_points = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    birthday = serializers.DateField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    business_email = serializers.CharField()
    country = serializers.ChoiceField(choices=COUNTRIES)
    time_zones = serializers.ChoiceField(choices=TIME_ZONES)
    status = serializers.ChoiceField(choices=ACCOUNT_STATUS_CHOICES)
    job_title = serializers.ChoiceField(choices=PROGRAMMING_ROLES_CHOICES, allow_null=True)
    two_factor_method = serializers.ChoiceField(choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')])

    # Socials
    socials = serializers.SerializerMethodField()

    # Related fields for friends, hobbies, education, certificates, work experience, and reactions
    friends = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    jobs = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = Clerbie
        fields = [
            'id',
            'username',
            'avatar',
            'nickname',
            'about_me',
            'technologies',
            'email',
            'role',
            'behavior_points',
            'gender',
            'birthday',
            'phone_number',
            'business_email',
            'country',
            'time_zones',
            'status',
            'job_title',
            'two_factor_method',
            'socials',
            'friends',
            'education',
            'certificates',
            'jobs',
            'reactions',
            'projects',
        ]

    def to_representation(self, instance):

        request_user = self.context.get('request_user')

        representation = super().to_representation(instance)

        if instance != request_user:
            representation.pop('email', None)
            representation.pop('role', None)
            representation.pop('two_factor_method', None)
            representation.pop('status', None)

        return representation

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
        }

    def get_friends(self, obj):
        relations = Clerbie_friends.objects.filter(Q(user1=obj) | Q(user2=obj))
        friends = [r.user1 if r.user2 == obj else r.user2 for r in relations]
        return ClerbieSerializer(friends, many=True).data

    def get_education(self, obj):
        education = Clerbie_education.objects.filter(user=obj)
        return EducationSerializer(education, many=True).data

    def get_certificates(self, obj):
        certificates = Clerbie_certificates.objects.filter(user=obj)
        return CertificateSerializer(certificates, many=True).data

    def get_jobs(self, obj):
        jobs = UserJobExperience.objects.filter(user=obj).order_by('-started_at')
        return JobExperienceSerializer(jobs, many=True).data

    def get_reactions(self, obj):
        reactions = Clerbie_reactions.objects.filter(user=obj)
        return ReactionSerializer(reactions, many=True).data

    def get_projects(self, obj):
        projects = Projects.objects.filter(users=obj)
        return ProjectSerializer(projects, many=True).data


class UpdateGeneralDataSerializer(serializers.ModelSerializer):

    technologies = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Clerbie
        fields = [
            'avatar',
            'gender',
            'country',
            'about_me',
            'username',
            'birthday',
            'time_zones',
            'technologies',
            'phone_number',
            'business_email',]

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            if attr != 'technologies':
                setattr(instance, attr, value)


        technologies_data = validated_data.pop('technologies', [])

        if not technologies_data:
            instance.technologies.clear()

        else:
            instance.technologies.clear()
            for tech_data in technologies_data:
                technology, created = Technologies.objects.get_or_create(name=tech_data)
                instance.technologies.add(technology)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies]

        return representation


class FriendSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='user2.id')
    nickname = serializers.CharField(source='user2.nickname')
    username = serializers.CharField(source='user2.username')
    avatar = serializers.URLField(source='user2.avatar')
    offer_code = serializers.CharField(required=False)

    class Meta:
        model = Clerbie_friends
        fields = ['id', 'nickname', 'username', 'avatar', 'offer_code']

    def to_representation(self, instance):

        request_user = self.context.get('request_user')
        representation = super().to_representation(instance)

        if request_user != instance.user1:
            avatar = instance.user1.avatar.url if instance.user1.avatar else None
            representation['id'] = instance.user1.id
            representation['nickname'] = instance.user1.nickname
            representation['username'] = instance.user1.username
            representation['avatar'] = avatar
        return representation


class FriendsOffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie_friends
        fields = [
            'id',
            'status',
            'offer_code',
            'user1',
            'user2',
            'created_at',
            'expires_at',
            'description']


class UpdateJobSerializer(serializers.ModelSerializer):

    '''Allows user to add or remove education'''

    company = serializers.CharField()
    position = serializers.CharField()
    started_at = serializers.DateField()
    ended_at = serializers.DateField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = UserJobExperience
        fields = [
            'company',
            'position',
            'started_at',
            'ended_at',
            'description']

    def validate_company(self, value):

        '''Ensures that the company is either creater or fetched.'''

        company_name = value.strip()
        if not company_name:
            raise serializers.ValidationError({"company": "company field can not be empty"})

        company, created = Companies.objects.get_or_create(name=company_name)

        return company

    def validate(self, attrs):

        for f in [f for f in self.fields if f != 'description' and f != 'ended_at']:
            if f not in attrs:
                raise serializers.ValidationError({"errors": f"{f}: 'This field is required.'"})
        return attrs

    def update(self, instance, validated_data):

        if validated_data['started_at'] and validated_data['started_at'] > date.today():
            raise serializers.ValidationError({"started_at": "You can't start to work in the future."})
        
        if 'ended_at' in validated_data.keys():
            if validated_data['ended_at'] and validated_data['ended_at'] > date.today():
                raise serializers.ValidationError({"ended_at": "You can't end your work in the future."})
            if validated_data['ended_at'] and validated_data['ended_at'] < validated_data['started_at']:
                raise serializers.ValidationError({"ended_at": "You can't end your work earlier than started."})

        user_job = UserJobExperience.objects.filter(
            user=instance,
            company=validated_data.get('company')
        ).first()

        if user_job:
            for attr, value in validated_data.items():
                setattr(user_job, attr, value)
            if not 'description' in validated_data.keys():
                setattr(user_job, 'description', None)
            if not 'ended_at' in validated_data.keys():
                setattr(user_job, 'ended_at', None)
            user_job.save()
            return user_job

        else:
            new_user_job_relation = UserJobExperience.objects.create(
                user=instance,
                company=validated_data['company'],
                position=validated_data['position'],
                started_at=validated_data['started_at'],
                ended_at=validated_data['ended_at'] if 'ended_at' in validated_data.keys() else None,
                description=validated_data['description'] if 'description' in validated_data.keys() else None,
            )
            new_user_job_relation.save()
            return new_user_job_relation


class RemoveJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserJobExperience
        fields = ['company', 'position']


class ProjectOfferSerializer(serializers.ModelSerializer):

    project = serializers.CharField(source='project.name')
    sender = serializers.CharField(source='sender.nickname')
    
    class Meta:
        model = Offers
        fields = ['id','offer_type','offer_code', 'project','description', 'sender', 'expires_at', 'status', 'created_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'offer_type' in representation:
            representation['offer_type'] = f"project_{representation['offer_type']}"

        return representation


class CreateProjectSerializer(serializers.ModelSerializer):

    technologies = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'technologies']

    def create(self, validated_data):
        user = self.context['request'].user
        technologies_data = validated_data.pop('technologies', [])
        project = Projects.objects.create(creator=user, **validated_data)

        for tech_name in technologies_data:
            technology, created = Technologies.objects.get_or_create(name=tech_name)
            project.technologies.add(technology)

        project.users.add(user)
        return project

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies]

        return representation


class UpdateSocialsSerializer(serializers.ModelSerializer):

    github = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    skype = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)
    discord = serializers.CharField(required=False, allow_blank=True)
    facebook = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    telegram = serializers.URLField(required=False, allow_blank=True)
    instagram = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Clerbie
        fields = [
            'github',
            'skype',
            'website',
            'youtube',
            'discord',
            'facebook',
            'linkedin',
            'telegram',
            'instagram',
        ]

    def validate(self, data):

        social_fields = ['github', 'skype', 'website', 'youtube', 'discord', 'facebook', 'linkedin', 'telegram', 'instagram']

        if not len(data.keys()):
            raise serializers.ValidationError({"error:": "At least one social field must be provided."})

        return data


class UpdateEducationSerializer(serializers.ModelSerializer):

    '''Allows user to add or remove education'''

    university = serializers.CharField()
    specialty = serializers.CharField()
    started_at = serializers.DateField()
    ended_at = serializers.DateField(required=False)

    class Meta:
        model = Clerbie_education
        fields = [
            'id',
            'university',
            'specialty',
            'started_at',
            'ended_at']

    def validate_university(self, value):

        '''Ensures that the university is either creater or fetched.'''

        university_name = value.strip()
        if not university_name:
            raise serializers.ValidationError({"university": "university field can not be empty"})

        university, created = University.objects.get_or_create(name=university_name)

        return university

    def update(self, instance, validated_data):

        fields = {k: (validated_data[k] if k in validated_data else None) for k, v in {"university": None,  "specialty": None, "started_at": None, "ended_at": None}.items()}
        errors = [k for k in fields.keys() if fields[k] is None and k != 'ended_at']
        ended_at = fields['ended_at']

        if errors:
            raise serializers.ValidationError({"errors": {k : 'This field is required.' for k in errors}})

        if ended_at and ended_at > date.today():
            raise serializers.ValidationError({"ended_at": "End date cannot be in the future."})

        if fields['started_at'] and fields['started_at'] > date.today():
            raise serializers.ValidationError({"started_at": "Start date cannot be in the future."})

        education_record = Clerbie_education.objects.filter(
            user=instance,
            university=fields['university']
        ).first()

        if education_record:

            for attr, value in fields.items():
                print(value)
                setattr(education_record, attr, value)
            education_record.save()
            return super().update(education_record, fields)

        else:
            new_relation = Clerbie_education.objects.create(
                user=instance,
                university=fields['university'],
                specialty=fields['specialty'],
                started_at=fields['started_at'],
                ended_at=ended_at
            )
            
            new_relation.save()
            return new_relation


class RemoveEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clerbie_education
        fields = ['university']


class UpdateCertificateSerializer(serializers.ModelSerializer):

    title = serializers.CharField()
    photo = serializers.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ]
    )
    organization = serializers.CharField()
    issued_at = serializers.DateField()
    description = serializers.CharField(required=False)

    class Meta:
        model = Clerbie_certificates
        fields = [
            'id',
            'title',
            'photo',
            'organization',
            'issued_at',
            'description'
        ]

    def validate(self, attrs):

        for f in [f for f in self.fields if f != 'description']:
            if f not in attrs:
                raise serializers.ValidationError({"errors": f"{f}: 'This field is required.'"})
        return attrs

    def update(self, instance, validated_data):


        if validated_data['issued_at'] and validated_data['issued_at'] > date.today():
            raise serializers.ValidationError({"issued_at": "You can't get certificate in the future."})

        certificate = Clerbie_certificates.objects.filter(
            user=instance,
            title=validated_data.get('title')
        ).first()

        if certificate:
            for attr, value in validated_data.items():
                setattr(certificate, attr, value)
            if not 'description' in validated_data.keys():
                setattr(certificate, 'description', None)
            certificate.save()
            return certificate

        else:
            new_certificate = Clerbie_certificates.objects.create(
                user=instance,
                title=validated_data['title'],
                photo=validated_data['photo'],
                organization=validated_data['organization'],
                description=validated_data['description'] if 'description' in validated_data.keys() else None,
                issued_at=validated_data['issued_at'],
            )
            new_certificate.save()
            return new_relation


class DeleteCertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clerbie_education
        fields = [
            'title',
            'photo',
            'organization',
            'issued_at',
            'description'
        ]

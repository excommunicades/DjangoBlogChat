from profile.utils.serializers_utils import *

class GetUserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring Clerbie data, including related models for friends, hobbies, education, certificates, work experience, etc.
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

    # Socials
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
        model = Clerbie
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
        friends = Clerbie_friends.objects.filter(user=obj)
        return ClerbieSerializer(friends, many=True).data
    
    def get_hobbies(self, obj):
        hobbies = Clerbie_hobbies.objects.filter(user=obj)
        return HobbySerializer(hobbies, many=True).data

    def get_education(self, obj):
        education = Clerbie_education.objects.filter(user=obj)
        return EducationSerializer(education, many=True).data

    def get_certificates(self, obj):
        certificates = Clerbie_certificates.objects.filter(user=obj)
        return CertificateSerializer(certificates, many=True).data

    def get_work_experience(self, obj):
        work_experience = UserWorkExperience.objects.filter(user=obj)
        return WorkExperienceSerializer(work_experience, many=True).data

    def get_reactions(self, obj):
        reactions = Clerbie_reactions.objects.filter(user=obj)
        return ReactionSerializer(reactions, many=True).data

    def get_projects(self, obj):
        projects = Projects.objects.filter(users=obj)
        return ProjectSerializer(projects, many=True).data

class UpdateGeneralDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clerbie
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
    return validate_avatar(self, value)


class SocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie
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

    technologies = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Projects
        fields = ['name', 'description', 'technologies']

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

class UpdateProjectSerializer(serializers.ModelSerializer):

    technologies = TechnologiesSerializer(many=True, required=False)

    class Meta:
        model = Projects
        fields = [
            'name',
            'description',
            'technologies',
        ]


    def update(self, instance, validated_data):

        user = self.context['request'].user

        if instance.creator != user:
            raise PermissionDenied("You do not have permission to update this project.")


        technologies_data = validated_data.pop('technologies', [])

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()

        if technologies_data:
            instance.technologies.clear()
            for tech_data in technologies_data:
                tech_name = tech_data.get('name')
                technology, created = Technologies.objects.get_or_create(name=tech_name)
                instance.technologies.add(technology)

        return instance

class CreateInvitationSerializer(serializers.ModelSerializer):
    receiver = serializers.IntegerField()
    expires_at = serializers.DateTimeField()

    class Meta:
        model = Invitation
        fields = ['receiver', 'expires_at']

    def validate_receiver(self, value):
        try:
            receiver = Clerbie.objects.get(id=value)
        except Clerbie.DoesNotExist:
            raise serializers.ValidationError("Receiver user not found.")
        return value

    def validate_expires_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value

class InvitationResponseSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=[('accepted', 'Accepted'), ('declined', 'Declined')])

    class Meta:
        model = Invitation
        fields = ['status']


class InvitationSerializer(serializers.ModelSerializer):

    project = serializers.CharField(source='project.name')
    sender = serializers.CharField(source='sender.nickname')

    class Meta:
        model = Invitation
        fields = ['invite_code', 'project', 'sender', 'expires_at', 'status', 'created_at']
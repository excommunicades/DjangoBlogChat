from profile.utils.serializers_utils import *

class GetUserProfileSerializer(serializers.ModelSerializer):
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

class UpdateProjectSerializer(serializers.ModelSerializer):

    technologies = serializers.ListField(child=serializers.CharField(), write_only=True)

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
                technology, created = Technologies.objects.get_or_create(name=tech_data)
                instance.technologies.add(technology)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies]

        return representation

class CreateOfferSerializer(serializers.ModelSerializer):
    receiver = serializers.IntegerField()
    expires_at = serializers.DateTimeField()
    description = serializers.CharField(required=False, default=None)

    class Meta:
        model = Offers
        fields = ['receiver', 'expires_at', 'description']

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
class FriendsOffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clerbie_friends
        fields = [
            'id',
            'status',
            'offer_code',
            'user_id',
            'friend_id',
            'created_at',
            'expires_at',
            'description']


class OfferResponseSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=[('accepted', 'Accepted'), ('declined', 'Declined')])

    class Meta:
        model = Offers
        fields = ['status']


class CreateFriendshipSerializer(serializers.ModelSerializer):

    friend_id = serializers.IntegerField(read_only=True)
    expires_at = serializers.DateTimeField()
    description = serializers.CharField(required=False, default=None)


    class  Meta:
        model = Clerbie_friends
        fields = [
            'friend_id',
            'expires_at',
            'description'
        ]

    def validate_expires_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value

class FriendshipResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[('accepted', 'Accepted'), ('declined', 'Declined')])

    class Meta:
        model = Clerbie_friends
        fields = ['status']


class FriendSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='friend.id')
    nickname = serializers.CharField(source='friend.nickname')
    username = serializers.CharField(source='friend.username')
    avatar = serializers.URLField(source='friend.avatar')

    class Meta:
        model = Clerbie_friends
        fields = ['id', 'nickname', 'username', 'avatar']
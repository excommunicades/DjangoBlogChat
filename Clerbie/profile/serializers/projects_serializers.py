from datetime import date
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from django.utils import timezone

from authify.models import Clerbie
from profile.models import (
    Offers,
    Projects,
    Technologies,
)


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

            existing_technologies = Technologies.objects.filter(name__in=technologies_data)
            existing_tech_names = [tech.name for tech in existing_technologies]

            new_technologies = [Technologies(name=tech_name) for tech_name in technologies_data if tech_name not in existing_tech_names]
            Technologies.objects.bulk_create(new_technologies)

            all_technologies = existing_technologies | Technologies.objects.filter(name__in=technologies_data)
            instance.technologies.set(all_technologies)

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


class OfferResponseSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=[('accepted', 'Accepted'), ('declined', 'Declined')])

    class Meta:
        model = Offers
        fields = ['status']


class KickProjectMemberSerializer(serializers.Serializer):

    members = serializers.ListField(child=serializers.IntegerField())

    def validate_members(self, value):

        if not value:
            raise serializers.ValidationError("The members list cannot be empty.")
        
        for member_id in value:
            if not Clerbie.objects.filter(id=member_id).exists():
                raise serializers.ValidationError(f"User with ID {member_id} does not exist.")
        
        return value


class LeaveFromProjectSerializer(serializers.Serializer):
    
    creator_to = serializers.CharField(required=False, allow_blank=True)

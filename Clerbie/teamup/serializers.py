from rest_framework import serializers

from teamup.models import Announcement
from profile.models import Projects, JobTitles, Technologies
from profile.utils.serializers_utils import ClerbieSerializer

class CreateAnnouncementSerializer(serializers.ModelSerializer):

    '''Serialize data to db records from records for announcement creation'''

    job_titles = serializers.ListField(child=serializers.CharField(), required=True)
    technologies = serializers.ListField(child=serializers.CharField(), required=False)
    project = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), required=True)

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'job_titles',
            'technologies',
            'project',
            'updated_at',
            'created_at'
        ]
        read_only_fields = ['id', 'updated_at', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        technologies_data = validated_data.pop('technologies', [])
        job_titles = validated_data.pop('job_titles', [])
        description = validated_data.get('description', None)
        title = validated_data.get('title', None)
        project = validated_data.get('project', None)

        if user != validated_data['project'].creator:
            raise serializers.ValidationError({'errors': {'project': 'Only project creator can create announcement for his project'}})
        if len(Announcement.objects.filter(owner=user, project=project)) > 0:
            raise serializers.ValidationError({'errors': 'You can create only one announncement for one project'})

        announcement = Announcement.objects.create(
            owner=user,
            title=title,
            description=description,
            project=project
        )

        for tech_name in technologies_data:
            technology, created = Technologies.objects.get_or_create(name=tech_name)
            announcement.technologies.add(technology)

        for job_title_name in job_titles:
            job_title, created = JobTitles.objects.get_or_create(title=job_title_name)
            announcement.job_titles.add(job_title)

        return announcement

    def to_representation(self, instance):

        representation = {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'project': instance.project.id,
            'updated_at': instance.updated_at,
            'created_at': instance.created_at,
        }

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies] if technologies else []

        job_titles = instance.job_titles.all()
        representation['job_titles'] = [job_title.title for job_title in job_titles] if job_titles else []

        return representation


class UpdateAnnouncementSerializer(serializers.ModelSerializer):

    '''Serialize data for db records from fields for update'''

    job_titles = serializers.ListField(child=serializers.CharField(), required=False)
    technologies = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'job_titles',
            'technologies',
            'updated_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):

        if len(data) == 0:
            raise serializers.ValidationError({'errors': {'error': 'At least one of field must be implemented for update.'}})
        return data

    def update(self, instance, validated_data):

        user = self.context['request'].user

        if user != instance.project.creator:
            raise serializers.ValidationError({'errors': {'project': 'Only project creator can update announcement for his project'}})

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        if 'technologies' in validated_data:
            technologies_data = validated_data.pop('technologies')
            instance.technologies.clear()
            for tech_name in technologies_data:
                technology, created = Technologies.objects.get_or_create(name=tech_name)
                instance.technologies.add(technology)

        if 'job_titles' in validated_data:
            job_titles_data = validated_data.pop('job_titles')
            instance.job_titles.clear()
            for job_title_name in job_titles_data:
                job_title, created = JobTitles.objects.get_or_create(title=job_title_name)
                instance.job_titles.add(job_title)

        instance.save()
        return instance

    def to_representation(self, instance):

        representation = {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'project': instance.project.id,
            'updated_at': instance.updated_at,
            'created_at': instance.created_at,
        }

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies] if technologies else []

        job_titles = instance.job_titles.all()
        representation['job_titles'] = [job_title.title for job_title in job_titles] if job_titles else []

        return representation


class GetAnnouncementListSerializer(serializers.ModelSerializer):

    '''Serialize list of announcemnt data'''
    
    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'job_titles',
            'technologies',
            'project',
            'updated_at',
            'created_at'
        ]


    def to_representation(self, instance):

        representation = {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'project': instance.project.id,
            'updated_at': instance.updated_at,
            'created_at': instance.created_at,
        }

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies] if technologies else []

        job_titles = instance.job_titles.all()
        representation['job_titles'] = [job_title.title for job_title in job_titles] if job_titles else []

        return representation


class GetAnnouncementSerializer(serializers.ModelSerializer):
    
    '''Serialize data from db (announcemnet fields)'''

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'job_titles',
            'technologies',
            'project',
            'updated_at',
            'created_at'
        ]


    def to_representation(self, instance):

        representation = {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'project': {
                'id': instance.project.id,
                'creator': ClerbieSerializer(instance.project.creator).data,
                'name': instance.project.name,
                'description': instance.project.description,
                'members': ClerbieSerializer(instance.project.users.all(), many=True).data,
            },
            'updated_at': instance.updated_at,
            'created_at': instance.created_at,
        }

        technologies = instance.technologies.all()
        representation['technologies'] = [tech.name for tech in technologies] if technologies else []

        job_titles = instance.job_titles.all()
        representation['job_titles'] = [job_title.title for job_title in job_titles] if job_titles else []

        return representation
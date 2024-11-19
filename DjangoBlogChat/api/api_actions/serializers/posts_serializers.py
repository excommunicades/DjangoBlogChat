from rest_framework import serializers

from publish.models.posts_models import Posts

class PostsOutSerializer(serializers.ModelSerializer):

    """Transform json data to db datatype"""

    class Meta:

        model = Posts

        fields = [
            'pk',
            'owner',
            'title',
            'content',
            'head_image',
            'add_image_1',
            'add_image_2',
            'add_image_3',
            'add_image_4',
            'add_image_5',
        ]

    def create(self, validated_data):

        owner = self.context['request'].user

        validated_data['owner'] = owner

        return super().create(validated_data)

class PostsInSerializer(serializers.ModelSerializer):

    """Transform json data to db datatype"""

    class Meta:

        model = Posts

        fields = [
            'title',
            'content',
            'head_image',
            'add_image_1',
            'add_image_2',
            'add_image_3',
            'add_image_4',
            'add_image_5',
        ]

    def create(self, validated_data):

        owner = self.context['request'].user

        validated_data['owner'] = owner

        return super().create(validated_data)

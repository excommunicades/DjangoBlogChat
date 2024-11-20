from rest_framework import serializers

from publish.models.posts_models import Posts, PostReactions

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


class PostsUpdateSerializer(serializers.ModelSerializer):

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

        extra_kwargs = {
            'title': {'required': False},
            'content': {'required': False},
            'head_image': {'required': False},
            'add_image_1': {'required': False},
            'add_image_2': {'required': False},
            'add_image_3': {'required': False},
            'add_image_4': {'required': False},
            'add_image_5': {'required': False},
        }

    def validate(self, data):

        if not any(data.values()):

            raise serializers.ValidationError({"error": "At least one field must be provided."})

        return data


class SetReactionSerializer(serializers.ModelSerializer):

    class Meta:

        model = PostReactions

        fields = ['post', 'reaction']

        extra_kwargs = {
            'post': {'required': True},
            'reaction': {'required': True},
        }

    def create(self, validated_data):

        user = self.context['request'].user

        validated_data['user'] = user

        return super().create(validated_data)

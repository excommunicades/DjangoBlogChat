from rest_framework import serializers

from django.utils import timezone

from profile.models import (
    Clerbie_friends
)


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


class CreateFriendshipSerializer(serializers.ModelSerializer):

    user2 = serializers.IntegerField(read_only=True)
    expires_at = serializers.DateTimeField()
    description = serializers.CharField(required=False, default=None)


    class  Meta:
        model = Clerbie_friends
        fields = [
            'user2',
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
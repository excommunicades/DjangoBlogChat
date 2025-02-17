from rest_framework import serializers
from typing import Optional, Dict

from django.db.models import Q

from authify.models import Clerbie, BlackList
from profile.models import Clerbie_friends
from profile.utils.serializers_utils import ClerbieSerializer

class UserListSerializer(serializers.ModelSerializer):

    friend_info = serializers.SerializerMethodField()

    class Meta:
        model = Clerbie
        fields = [
            'id',
            'nickname',
            'username',
            'friend_info', 
        ]

    def get_friend_info(self, obj) -> Optional[Dict[str, str]]:
        request_user = self.context.get('request').user

        if not request_user:
            return None

        if request_user.is_authenticated:
            try:
                friendship = Clerbie_friends.objects.get(Q(user1=request_user, user2=obj) | Q(user1=obj, user2=request_user))
                if friendship.status == 'declined':
                    return None
                return {
                    'sender_id': friendship.user1.id,
                    'offer_code': friendship.offer_code,
                    'status': friendship.status
                }
            except Clerbie_friends.DoesNotExist:
                return None
        else:
            return None

class UserDataSerializer(serializers.ModelSerializer):

    class Meta:

        model = Clerbie

        fields = [
            'id',
            'nickname',
            'username']


class BlockuserSerializer(serializers.ModelSerializer):

    '''Adds blocked user to db'''

    user = serializers.CharField(read_only=True)
    blocked_user = serializers.CharField(read_only=True)
    class Meta:
        model = BlackList
        fields = [
            'user',
            'blocked_user',
            'expires_at'
        ]

    def create(self, validated_data):

        return super().create(validated_data)

    def validate(self, data):

        if 'user' in data or 'blocked_user' in data:
            raise serializers.ValidationError("You cannot provide 'user' or 'blocked_user' fields in the request.")
        return data


class BlockUserListSerializer(serializers.ModelSerializer):

    '''Serializer for list of blocked user'''

    blocked_user = serializers.SerializerMethodField()

    class Meta:
        model = BlackList
        fields = [
            'expires_at',
            'blocked_user',
        ]

    def get_blocked_user(self, obj) -> Dict[str, str]:
        return {
            'id': obj.blocked_user.id,
            'username': obj.blocked_user.username,
            'nickname': obj.blocked_user.nickname
        }
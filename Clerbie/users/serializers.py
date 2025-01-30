from rest_framework import serializers

from django.db.models import Q

from authify.models import Clerbie, BlackList
from profile.models import Clerbie_friends

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

    def get_friend_info(self, obj):
        request_user = self.context.get('request').user

        if not request_user:
            return None

        if request_user.is_authenticated:
            try:
                friendship = Clerbie_friends.objects.get(Q(user=request_user, friend=obj) | Q(user=obj, friend=request_user))
                if friendship.status == 'declined':
                    return None
                return {
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
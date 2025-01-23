from rest_framework import serializers

from django.db.models import Q

from authify.models import Clerbie
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

        try:
            friendship = Clerbie_friends.objects.get(Q(user=request_user, friend=obj) | Q(user=obj, friend=request_user))
            return {
                'offer_code': friendship.offer_code,
                'status': friendship.status
            }
        except Clerbie_friends.DoesNotExist:
            return None

class UserDataSerializer(serializers.ModelSerializer):

    class Meta:

        model = Clerbie

        fields = [
            'id',
            'nickname',
            'username']

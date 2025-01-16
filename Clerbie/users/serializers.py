from rest_framework import serializers

from authify.models import Clerbie

class UserListSerializer(serializers.ModelSerializer):

    class Meta:

        model = Clerbie

        fields = [
            'id',
            'nickname',
            'username',]


class UserDataSerializer(serializers.ModelSerializer):

    class Meta:

        model = Clerbie

        fields = [
            'id',
            'nickname',
            'username']

from rest_framework import serializers

from blog_user.models import BlogUser

class UserListSerializer(serializers.ModelSerializer):

    class Meta:

        model = BlogUser

        fields = [
            'id',
            'nickname',
            'username',]


class UserDataSerializer(serializers.ModelSerializer):

    class Meta:

        model = BlogUser

        fields = [
            'id',
            'nickname',
            'username']

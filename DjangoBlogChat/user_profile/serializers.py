from rest_framework import serializers


class GetUserDataSerializer(serializers.Serializer):

    """
    Serializer for data transfer for bd/ also for swagger.
    """

    username = serializers.CharField()
    nickname = serializers.CharField()
    email = serializers.EmailField()
    is_activated = serializers.BooleanField()
    role = serializers.CharField()

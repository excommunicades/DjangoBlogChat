from rest_framework import serializers
from blog_user.models import BlogUser

class GetUserDataSerializer(serializers.ModelSerializer):

    """
    Serializer for data transfer for bd/ also for swagger.
    """

    avatar = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = BlogUser
        fields = [
            'id',
            'username',
            'nickname',
            'email',
            'role',
            'avatar',
            'registered_at',
            'behavior_points',
            'gender',
            'birthday',
            'phone_number',
            'country',
            'time_zones',
            'status',
            'telegram',
            'whatsapp',
            'viber',
            'linkedin',
            'github',
            'instagram',
            'skype',
            'discord',
            'dou',
            'djinni',
            'website',
            'facebook',
            'twitter',
            'youtube',
            'pinterest',
            'tiktok',
            'reddit',
            'snapchat',
            'business_email',
            'job_title',
            'two_factor_method',
        ]

class SetUserAvatarSerializer(serializers.ModelSerializer):

    avatar = serializers.ImageField(required=True)

    class Meta:

        model = BlogUser
        fields = ['avatar']

    def validate_avatar(self, value):

        valid_extensions = ['image/png', 'image/jpg', 'image/webp']
        if value.content_type not in valid_extensions:
            raise serializers.ValidationError('Allowed image formats: PNG, JPG, WebP.')

        if value.size > 1 * 1024 * 1024:  # 1 MB
            raise serializers.ValidationError('File size must not exceed 1MB.')

        image = Image.open(value)
        width, height = image.size

        if width < 50 or height < 50:
            raise serializers.ValidationError('Image must be at least 50x50 pixels.')

        if width > 200 or height > 200:
            image.thumbnail((200, 200))

            byte_io = io.BytesIO()
            image.save(byte_io, format='PNG' if value.content_type == 'image/png' else 'JPEG' if value.content_type == 'image/jpeg' else 'WEBP')
            byte_io.seek(0)

            if byte_io.tell() > 1 * 1024 * 1024:

                image.save(byte_io, format='PNG' if value.content_type == 'image/png' else 'JPEG' if value.content_type == 'image/jpeg' else 'WEBP', quality=85)
                byte_io.seek(0)
                
                if byte_io.tell() > 1 * 1024 * 1024:
                    raise serializers.ValidationError('Compressed image size still exceeds 1MB.')

            value = value.__class__(file=byte_io, name=value.name)

        return value
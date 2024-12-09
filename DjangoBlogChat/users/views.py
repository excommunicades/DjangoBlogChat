from rest_framework.generics import ListAPIView, RetrieveAPIView

from blog_user.models import BlogUser

from users.serializers import (
    UserListSerializer,
    UserDataSerializer
)

class User_List(ListAPIView):

    '''Returns a list of users'''

    queryset = BlogUser.objects.all()

    serializer_class = UserListSerializer


class User_Data(RetrieveAPIView):

    queryset = BlogUser.objects.all()

    serializer_class = UserDataSerializer
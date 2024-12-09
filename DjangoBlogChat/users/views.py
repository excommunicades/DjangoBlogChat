from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError

from blog_user.models import BlogUser

from users.serializers import (
    UserListSerializer,
    UserDataSerializer
)

from users.utlis import (
    user_pagination
)

class User_List(ListAPIView):

    '''Returns a list of users'''

    # queryset = BlogUser.objects.all()

    serializer_class = UserListSerializer

    def get_queryset(self):

        page = self.request.query_params.get('page', None)

        if page and not page.isdigit():

            raise ValidationError({"error": "Query parameter does not exist."})

        page_size = 15

        return user_pagination(page, page_size)

class User_Data(RetrieveAPIView):

    queryset = BlogUser.objects.all()

    serializer_class = UserDataSerializer

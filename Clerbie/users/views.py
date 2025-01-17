from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError

from authify.models import Clerbie

from users.serializers import (
    UserListSerializer,
    UserDataSerializer,
)

from users.utils.views_utils import (
    user_pagination
)

class User_List(ListAPIView):

    '''Returns a list of users'''

    serializer_class = UserListSerializer

    def get_queryset(self):

        user = self.request.user

        page = self.request.query_params.get('page', None)

        if page and not page.isdigit():

            raise ValidationError({"error": "Query parameter does not exist."})

        page_size = 15

        return user_pagination(page, page_size, user)


class User_Data(RetrieveAPIView):

    '''Retrieve user data by user id'''

    queryset = Clerbie.objects.all()

    serializer_class = UserDataSerializer
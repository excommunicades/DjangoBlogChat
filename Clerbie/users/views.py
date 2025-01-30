from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db import IntegrityError

from authify.models import Clerbie, BlackList

from users.serializers import (
    UserDataSerializer,
    UserListSerializer,
    BlockuserSerializer,
)

from users.utils.views_utils import (
    user_pagination
)

class GetUserList(generics.ListAPIView):

    '''Returns a list of users'''

    serializer_class = UserListSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):

        user = self.request.user

        page = self.request.query_params.get('page', None)

        if page and not page.isdigit():

            raise ValidationError({"error": "Query parameter does not exist."})

        page_size = 15

        return user_pagination(page, page_size, user)


class GetUserData(generics.RetrieveAPIView):

    '''Retrieve user data by user id'''

    queryset = Clerbie.objects.all()

    serializer_class = UserDataSerializer


class BlockUserView(generics.GenericAPIView):

    ''' Process user data for blocking '''

    queryset = BlackList.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = BlockuserSerializer

    def post(self, request, *args, **kwargs):
        request_user = self.request.user
        blocked_user_id = self.kwargs.get('blocked_user_id')

        if blocked_user_id:
            try:

                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=request_user, blocked_user_id=blocked_user_id)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

            except IntegrityError:

                return Response({'errors': 'This user has already blocked this user.'}, status=status.HTTP_409_CONFLICT)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'errors': 'Blocked user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response

from user_profile.serializers import (
    GetUserDataSerializer,
    # SetUserAvatarSerializer,
    UpdateGeneralDataSerializer,
    SocialLinksSerializer,
)

from user_profile.utils.views_utils import (
    get_user_by_request
)

from blog_user.models import BlogUser

class Get_User_Data(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = GetUserDataSerializer

    def get(self, request, *args, **kwargs):

        request_user = self.request.user

        user = get_user_by_request(request_user=request_user)

        if user is None:

            return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

# class Set_User_Avatar(generics.UpdateAPIView):

#     '''Retrieve user data by user id'''

#     serializer_class = SetUserAvatarSerializer

#     def patch(self, request):

#         request_user = self.request.user

#         user = get_user_by_request(request_user=request_user)

#         if user is None:

#             return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

#         serializer = self.get_serializer(user, data=request.data)

#         if serializer.is_valid():

#             serializer.save()

#             return Response(status=status.HTTP_200_OK, data=serializer.data)

#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request):

#         request_user = self.request.user

#         user = get_user_by_request(request_user=request_user)

#         if user is None:

#             return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

#         serializer = self.get_serializer(user, data=request.data)

#         if serializer.is_valid():

#             serializer.save()

#             return Response(status=status.HTTP_200_OK, data=serializer.data)

#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Update_User_GeneralData(generics.UpdateAPIView):

    queryset = BlogUser.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        return BlogUser.objects.get(pk=self.request.user.pk)

class Update_Social_Links(generics.UpdateAPIView):
    queryset = BlogUser.objects.all()
    serializer_class = SocialLinksSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        return BlogUser.objects.get(pk=self.request.user.pk)
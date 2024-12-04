from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response

from user_profile.serializers import (
    GetUserDataSerializer
)

from user_profile.utils.views_utils import (
    get_user_by_request
)

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

        return Response({
                    "id": user.pk,
                    "username": user.username,
                    "nickname": user.nickname,
                    "email": user.email,
                    "is_activated": user.is_actived,
                    "role": user.role
                }, status=status.HTTP_200_OK)

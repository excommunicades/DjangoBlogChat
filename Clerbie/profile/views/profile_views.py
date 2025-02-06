from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from django.db.models import Q

from profile.serializers import (
    FriendSerializer,
    ProjectSerializer,
    ProjectOfferSerializer,
    CreateProjectSerializer,
    UpdateSocialsSerializer,
    FriendsOffersSerializer,
    GetUserProfileSerializer,
    UpdateGeneralDataSerializer,
)

from profile.utils.views_utils import get_user_by_request
from profile.utils.views_permissions import (
    isNotBlockedUser,
    isOfferReceiverOrSender,
)

from authify.models import Clerbie
from profile.models import (
    Offers,
    Clerbie_friends,
)

@extend_schema(tags=['Profile'])
class GetProfile(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [isNotBlockedUser, AllowAny]
    serializer_class = GetUserProfileSerializer

    def get(self, request, *args, **kwargs):
        
        request_user = self.kwargs.get('user')
        if request_user:
            user = get_user_by_request(request_user=request_user)
        else:
            user = self.request.user

        if user is None:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, context={'request_user': request.user})

        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=['Inbox'])
class GetInbox(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer

    def get(self, request):

        user = request.user

        projects_offers = Offers.objects.filter(receiver=user, expires_at__gt=timezone.now()).order_by('-created_at')
        friends_offers = Clerbie_friends.objects.filter(Q(user1=user) | Q(user2=user))

        projects_offers_serializer = ProjectOfferSerializer(projects_offers, many=True)
        friends_offers_serializer = FriendsOffersSerializer(friends_offers, many=True)
        for friend_offer in friends_offers_serializer.data:
            friend_offer['offer_type'] = 'friend_invite'

        return Response({
            "content": {
                "projects_offers": projects_offers_serializer.data,
                "friends_offers": friends_offers_serializer.data
            }
        }, status=status.HTTP_200_OK)

@extend_schema(tags=['Inbox'])
class DeleteOffer(generics.DestroyAPIView):

    queryset = Offers.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [isOfferReceiverOrSender, IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Offers.objects.filter(id=self.kwargs['pk'])


@extend_schema(tags=['Profile'])
class UpdateUserGeneralData(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.prefetch_related('technologies').get(pk=self.request.user.pk)


@extend_schema(tags=['Profile'])
class UpdateSocials(generics.UpdateAPIView):

    '''CRUD Operations for Socials in profile'''

    queryset = Clerbie.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateSocialsSerializer

    def get_object(self):

        """Ensures that the user can only update their own profile"""

        user_profile = self.request.user
        
        if not user_profile:
            raise PermissionDenied("Профиль пользователя не найден.")
        
        return user_profile

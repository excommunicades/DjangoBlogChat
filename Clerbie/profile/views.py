from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync

from django.utils import timezone
from django.db.models import Q

from profile.serializers import (
    FriendSerializer,
    FriendSerializer,
    ProjectSerializer,
    CreateOfferSerializer,
    ProjectOfferSerializer,
    UpdateSocialsSerializer,
    UpdateProjectSerializer,
    CreateProjectSerializer,
    OfferResponseSerializer,
    FriendsOffersSerializer,
    GetUserProfileSerializer,
    CreateFriendshipSerializer,
    UpdateGeneralDataSerializer,
    FriendshipResponseSerializer,
)
from profile.utils.views_utils import (
    get_offer_by_id,
    ProjectBaseView,
    response_by_status,
    get_user_by_request,
    send_offer_to_receiver,
    get_offer_response_data,
    create_friendship_business_logic,
    respond_to_friend_business_logic,

)
from profile.utils.views_permissions import (
    IsProjectCreatorOrAdmin,
    isOfferReceiverOrSender,
    isNotBlockedUser,
)

from authify.models import Clerbie
from profile.models import (
    Projects,
    Offers,
    Clerbie_friends,
)

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

class UpdateUserGeneralData(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.get(pk=self.request.user.pk)


class CreateProject(generics.CreateAPIView):

    queryset = Projects.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]


class UpdateProject(ProjectBaseView, generics.UpdateAPIView):

    queryset = Projects.objects.all()
    serializer_class = UpdateProjectSerializer



class DeleteProject(ProjectBaseView, generics.DestroyAPIView):

    queryset = Projects.objects.all()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


from profile.utils.views_utils import get_project_by_id, create_project_business_logic

class CreateProjectOffer(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = CreateOfferSerializer

    def post(self, request, project_id):

        try:
            project = get_project_by_id(project_id)
        except Projects.DoesNotExist:

            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        sender = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return create_project_business_logic(serializer, project, sender)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetInbox(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
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

class ResponseOffer(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = OfferResponseSerializer

    def post(self, request, offer_code):

        try:
            offer = get_offer_by_id(offer_code)
        except Offers.DoesNotExist:
            return Response({"detail": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        if offer.receiver != self.request.user:
            return Response({"detail": "This offer is not for you."}, status=status.HTTP_403_FORBIDDEN)

        user = offer.receiver if offer.offer_type == 'invite' else offer.sender
        serializer = self.get_serializer(offer, data=request.data)

        if serializer.is_valid():
            offer.status = serializer.validated_data["status"]
            offer.save()

        offer_response_data = get_offer_response_data(offer, user)
        return response_by_status(offer, user, offer_response_data)

class DeleteOffer(generics.DestroyAPIView):

    queryset = Offers.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [isOfferReceiverOrSender]


class GetProjectList(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

class CreateFriendship(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = CreateFriendshipSerializer

    def post(self, request, friend_id):

        serializer = self.get_serializer(data=request.data)
        sender = request.user

        if sender.id == friend_id:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if Clerbie_friends.objects.filter(user1__in=[sender, friend_id], user2_id__in=[sender.id, friend_id], status='pending').exists():
            return Response({"error": "Friend offer already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if Clerbie_friends.objects.filter(status='accepted', user1__in=[sender, friend_id], user2_id__in=[sender.id, friend_id]).exists():
            return Response({"error": "You are already friend with this user"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():

            return create_friendship_business_logic(serializer, sender, friend_id)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespondToFriendship(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendshipResponseSerializer

    def post(self, request, offer_code):

        user = request.user

        try:
            friendship = Clerbie_friends.objects.get(offer_code=offer_code)
        except Clerbie_friends.DoesNotExist:
            return Response({"error": "Friendship request not found."}, status=status.HTTP_404_NOT_FOUND)

        if friendship.user2 != user:
            return Response({"error": "This request is not for you."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            return respond_to_friend_business_logic(serializer, friendship, user)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveFriendship(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendshipResponseSerializer

    def delete(self, request, friend_id):

        user = request.user

        friends_offer = Clerbie_friends.objects.filter(Q(user1=user) & Q(user2=friend_id))
        if not friends_offer:
            friends_offer = Clerbie_friends.objects.filter(Q(user1=friend_id) & Q(user2=user))
        if not friends_offer:
            return Response({"error": "Friend does not exist."}, status=status.HTTP_404_NOT_FOUND)

        friends_offer.delete()
        return Response({"error": "Friend was removed successfully."}, status=status.HTTP_204_NO_CONTENT)


class DeleteFriendOffer(generics.DestroyAPIView):

    '''deletes user's friend offer'''

    authentication_classes = [JWTAuthentication]
    serializer_class = FriendsOffersSerializer
    lookup_field = 'offer_code'

    def get_queryset(self):
        queryset = Clerbie_friends.objects.filter(offer_code=self.kwargs['offer_code'])
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user1 == self.request.user:
            self.perform_destroy(instance)
            return Response({"detail": "Offer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"errors":"You can not delete foreign offer"}, status=status.HTTP_403_FORBIDDEN)


class GetFriendsList(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendSerializer

    def get_queryset(self):

        user = self.request.user
        queryset = Clerbie_friends.objects.all()

        return queryset

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        friends = queryset.filter(Q(status='accepted') & (Q(user1=self.request.user) | Q(user2=self.request.user)))
        sent_requests = queryset.filter(user1=request.user, status='pending')
        received_requests = queryset.filter(user2=request.user, status='pending')

        friends_data = FriendSerializer(friends, many=True, context={'request_user': request.user}).data
        sent_requests_data = FriendSerializer(sent_requests, many=True).data
        received_requests_data = FriendSerializer(received_requests, many=True).data
        return Response({
            'friends': friends_data,
            'sent_requests': sent_requests_data,
            'received_requests': received_requests_data,
        })


class UpdateSocials(generics.UpdateAPIView):

    '''CRUD Operations for Socials in profile'''

    queryset = Clerbie.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateSocialsSerializer

    def get_object(self):

        """Ensures that the user can only update their own profile"""

        user_profile = self.request.user
        
        if not user_profile:
            raise PermissionDenied("Профиль пользователя не найден.")
        
        return user_profile

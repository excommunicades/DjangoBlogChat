from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response

from django.db.models import Q

from profile.serializers import (
    FriendSerializer,
    FriendSerializer,
    ProjectSerializer,
    FriendsOffersSerializer,
    CreateFriendshipSerializer,
    FriendshipResponseSerializer,
)
from profile.utils.views_utils import (
    create_friendship_business_logic,
    respond_to_friend_business_logic,
)
from profile.utils.views_permissions import (
    isNotBlockedUser
)

from authify.models import Clerbie
from profile.models import (
    Offers,
    Clerbie_friends,
)


@extend_schema(tags=['Friends'])
class GetFriendsList(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendSerializer

    def get_queryset(self):

        return Clerbie_friends.objects.prefetch_related('user1', 'user2')

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


@extend_schema(tags=['Friends'])
class CreateFriendship(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = CreateFriendshipSerializer
    permission_classes = [isNotBlockedUser]

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


@extend_schema(tags=['Friends'])
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


@extend_schema(tags=['Friends'])
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


@extend_schema(tags=['Friends'])
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

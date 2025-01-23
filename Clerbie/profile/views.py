from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync

from django.utils import timezone
from django.db.models import Q

from profile.serializers import (
    GetUserProfileSerializer,
    UpdateGeneralDataSerializer,
    SocialLinksSerializer,
    CreateProjectSerializer,
    UpdateProjectSerializer,
    OfferResponseSerializer,
    CreateOfferSerializer,
    ProjectSerializer,
    FriendSerializer,
    CreateFriendshipSerializer,
    FriendshipResponseSerializer,
    FriendSerializer,
    FriendsOffersSerializer,
    ProjectOfferSerializer,
)
from profile.utils.views_utils import (
    IsProjectCreatorOrAdmin,
    isOfferReceiverOrSender,
    ProjectBaseView,
    get_user_by_request,
    send_offer_to_receiver
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
    permission_classes = [AllowAny]
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

class UpdateSocialLinks(generics.UpdateAPIView):
    queryset = Clerbie.objects.all()
    serializer_class = SocialLinksSerializer
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


class CreateProjectOffer(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = CreateOfferSerializer

    def post(self, request, project_id):

        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        
        sender = request.user

        serializer = CreateOfferSerializer(data=request.data)
        if serializer.is_valid():
            receiver_id = serializer.validated_data["receiver"]
            expires_at = serializer.validated_data["expires_at"]
            description = serializer.validated_data.get("description", None)

            try:
                receiver = Clerbie.objects.get(id=receiver_id)
            except Clerbie.DoesNotExist:
                return Response({"error": "Receiver user not found."}, status=status.HTTP_404_NOT_FOUND)

            if receiver in project.users.all() and receiver != project.creator:
                return Response({'error': 'User already joined to team.'}, status=status.HTTP_400_BAD_REQUEST)

            if receiver == sender:
                return Response({"error": "You can not send offer to yourself."}, status=status.HTTP_400_BAD_REQUEST)

            offer = Offers.objects.create(
                offer_type='project_' + 'invite' if project.creator == sender else 'request',
                project=project,
                sender=sender,
                receiver=receiver,
                expires_at=expires_at,
                description=description
            )

            websocket_offer_data = {
                "type": 'project_' + offer.offer_type,
                "offer_code": str(offer.offer_code),
                "project": {
                    "project_id": project.id,
                    "project_name": project.name,
                    "project_description": project.description
                },
                "sender": {
                    "sender_name": sender.username,
                    "sender_nickname": sender.nickname,
                },
                "expires_at": offer.expires_at.isoformat(),
                "description": offer.description if offer.description else None,
            }

            async_to_sync(send_offer_to_receiver)(receiver.id, websocket_offer_data)

            return Response({
                "offer_type": 'project_' + offer.offer_type,
                "offer_code": str(offer.offer_code),
                "project": project.id,
                "sender": sender.id,
                "receiver": receiver.id,
                "status": offer.status,
                "expires_at": offer.expires_at,
                "description": offer.description if offer.description else None,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetInbox(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    # serializer_class = OfferSerializer

    def get(self, request):
        user = request.user

        projects_offers = Offers.objects.filter(receiver=user, expires_at__gt=timezone.now()).order_by('-created_at')
        friends_offers = Clerbie_friends.objects.filter(Q(user=user) | Q(friend=user))

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
            offer = Offers.objects.get(offer_code=offer_code)
        except Offers.DoesNotExist:
            return Response({"detail": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        user = offer.receiver if offer.offer_type == 'invite' else offer.sender

        if offer.receiver != self.request.user:
            return Response({"detail": "This offer is not for you."}, status=status.HTTP_403_FORBIDDEN)


        serializer = OfferResponseSerializer(offer, data=request.data)
        if serializer.is_valid():
            offer.status = serializer.validated_data["status"]
            offer.save()


        offer_response_data = {
                "type": 'project_' + str(offer.offer_type) + '_' + str(offer.status),
                "offer_code": str(offer.offer_code),
                "responser": {
                    "responser_name": user.username,
                    "responser_nickname": user.nickname,
                },
                "expires_at": offer.expires_at.isoformat(),
                "description": offer.description if offer.description else None,
            }

        if offer.status == 'accepted':
            if user not in offer.project.users.all():
                offer.project.users.add(user)
                offer.project.save()
            else:
                return Response({"detail": "User already in the project."}, status=status.HTTP_400_BAD_REQUEST)

            async_to_sync(send_offer_to_receiver)(offer.sender.id, offer_response_data)

            return Response({"detail": f"Offer {offer.status}."}, status=status.HTTP_200_OK)
        
        else:

            async_to_sync(send_offer_to_receiver)(offer.sender.id, offer_response_data)

            return Response({"detail": f"Offer {offer.status}."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        serializer = CreateFriendshipSerializer(data=request.data)
        sender = request.user

        if sender.id == friend_id:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if Clerbie_friends.objects.filter(user__in=[sender, friend_id], friend_id__in=[sender, friend_id], status='pending').exists():
            return Response({"error": "Friend offer already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if Clerbie_friends.objects.filter(status='accepted').exists():
            return Response({"error": "You are already friend with this user"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():

            friend = Clerbie.objects.filter(id=friend_id).first()
            if not friend:
                return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)

            expires_at = serializer.validated_data["expires_at"]
            description = serializer.validated_data.get("description", None)

            expires_at_str = expires_at.isoformat() if expires_at else None

            friendship = Clerbie_friends.objects.create(
                user=sender,
                friend=friend,
                expires_at=expires_at_str,
                description=description,
                status='pending'
            )

            offer_response_data = {
                        "type": 'friend_invite',
                        "offer_code": str(friendship.offer_code),
                        "sender": {
                            "id": sender.id,
                            "nickname": sender.nickname,
                            "username": sender.username,
                        },
                        "status": 'pending',
                        "expires_at": expires_at_str,
                        "description": friendship.description if friendship.description else None,
                    }
            async_to_sync(send_offer_to_receiver)(friend_id, offer_response_data)

            return Response({
                            "offer_code": str(friendship.offer_code),
                            "sender": sender.id,
                            "friend_id": friend.id,
                            "status": 'pending',
                            "expires_at": friendship.expires_at,
                            "description": friendship.description if friendship.description else None,
                        }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespondToFriendship(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendshipResponseSerializer

    def post(self, request, offer_code):

        try:
            friendship = Clerbie_friends.objects.get(offer_code=offer_code)
        except Clerbie_friends.DoesNotExist:
            return Response({"error": "Friendship request not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if friendship.friend != user:
            return Response({"error": "This request is not for you."}, status=status.HTTP_403_FORBIDDEN)

        serializer = FriendshipResponseSerializer(data=request.data)

        if serializer.is_valid():

            status_value = serializer.validated_data['status']
            expires_at_str = friendship.expires_at.isoformat() if friendship.expires_at else None
            
            if status_value:
                if friendship.status == 'pending':
                    friendship.status = status_value
                    friendship.save()
                    offer_response_data = {
                                "type": 'friend_invite_' + status_value, 
                                "offer_code": str(friendship.offer_code),
                                "responder": {
                                    "id": user.id,
                                    "nickname": user.nickname,
                                    "username": user.username,
                                },
                                "status": status_value,
                                "expires_at": expires_at_str,
                                "description": friendship.description if friendship.description else None,
                            }
                    async_to_sync(send_offer_to_receiver)(friendship.user.id, offer_response_data)
                    return Response({"detail": f"Friend offer with was {status_value}!"}, status=status.HTTP_200_OK)

                else:
                    return Response({"detail": "Friend offer was already responded."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespondToFriendship(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendshipResponseSerializer

    def post(self, request, offer_code):

        try:
            friendship = Clerbie_friends.objects.get(offer_code=offer_code)
        except Clerbie_friends.DoesNotExist:
            return Response({"error": "Friendship request not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if friendship.friend != user:
            return Response({"error": "This request is not for you."}, status=status.HTTP_403_FORBIDDEN)

        serializer = FriendshipResponseSerializer(data=request.data)

        if serializer.is_valid():

            status_value = serializer.validated_data['status']
            expires_at_str = friendship.expires_at.isoformat() if friendship.expires_at else None
            
            if status_value:
                if friendship.status == 'pending':
                    friendship.status = status_value
                    friendship.save()
                    offer_response_data = {
                                "type": 'friend_invite_' + status_value, 
                                "offer_code": str(friendship.offer_code),
                                "responder": {
                                    "id": user.id,
                                    "nickname": user.nickname,
                                    "username": user.username,
                                },
                                "status": status_value,
                                "expires_at": expires_at_str,
                                "description": friendship.description if friendship.description else None,
                            }
                    async_to_sync(send_offer_to_receiver)(friendship.user.id, offer_response_data)
                    return Response({"detail": f"Friend offer with was {status_value}!"}, status=status.HTTP_200_OK)

                else:
                    return Response({"detail": "Friend offer was already responded."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RemoveFriendship(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = FriendshipResponseSerializer

    def post(self, request, friend_id):

        user = request.user

        friends_offer = Clerbie_friends.objects.filter(Q(user=user) & Q(friend=friend_id))
        if not friends_offer:
            friends_offer = Clerbie_friends.objects.filter(Q(user=friend_id) & Q(friend=user))
        if not friends_offer:
            return Response({"detail": "Friend does not exist."}, status=status.HTTP_404_NOT_FOUND)

        friends_offer.delete()
        return Response({"detail": "Friend was removed successfully."}, status=status.HTTP_204_NO_CONTENT)


class GetFriendsList(generics.ListAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = FriendSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Clerbie_friends.objects.filter(Q(user=user) | Q(friend=user) & Q(status='accepted'))
        
        return queryset
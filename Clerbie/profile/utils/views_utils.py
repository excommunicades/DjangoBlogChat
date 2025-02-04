import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.http import JsonResponse

from authify.models import Clerbie
from profile.models import Projects, Offers, Clerbie_friends
from profile.utils.views_permissions import IsProjectCreatorOrAdmin
from websocket.consumers import connected_users


async def send_offer_to_receiver(user_id, offer_data):

    receiver_channel = connected_users.get(user_id)
    if receiver_channel:
        await receiver_channel.send(text_data=json.dumps(offer_data))

def get_user_by_request(request_user):

    try:
        user = Clerbie.objects.get(id=str(request_user))
    except Clerbie.DoesNotExist:
        return None
    return user

def get_project_by_id(project_id):

    project = Projects.objects.get(id=project_id)
    return project

def get_offer_by_id(offer_code):

    offer = Offers.objects.get(offer_code=offer_code)
    return offer

def get_friendship_by_id():

    friendship = Clerbie_friends.objects.get(offer_code=offer_code)
    return friendship

def create_project_business_logic(serializer, project, sender):

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
        offer_type='invite' if project.creator == sender else 'request',
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


def get_offer_response_data(offer, user):

    return {
            "type": 'project_' + str(offer.offer_type) + '_' + str(offer.status),
            "offer_code": str(offer.offer_code),
            "responser": {
                "responser_name": user.username,
                "responser_nickname": user.nickname,
            },
            "expires_at": offer.expires_at.isoformat(),
            "description": offer.description if offer.description else None,
        }

def response_by_status(offer, user, offer_response_data):

    if offer.status == 'accepted':
        print(offer.project.users.all())
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

def create_friendship_business_logic(serializer, sender, friend_id):

    friend = Clerbie.objects.filter(id=friend_id).first()
    if not friend:
        return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)

    expires_at = serializer.validated_data["expires_at"]
    description = serializer.validated_data.get("description", None)

    expires_at_str = expires_at.isoformat() if expires_at else None

    friendship = Clerbie_friends.objects.create(
        user1=sender,
        user2=friend,
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


def respond_to_friend_business_logic(serializer, friendship, user):

    status_value = serializer.validated_data['status']
    expires_at_str = friendship.expires_at.isoformat() if friendship.expires_at else None

    if status_value:
        if status_value == 'declined':

            friendship.delete()
            return Response({"detail": "Friend offer was declined."}, status=status.HTTP_204_NO_CONTENT)

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
            async_to_sync(send_offer_to_receiver)(friendship.user1.id, offer_response_data)
            return Response({"detail": f"Friend offer with was {status_value}!"}, status=status.HTTP_200_OK)

        else:
            return Response({"detail": "Friend offer was already responded."}, status=status.HTTP_400_BAD_REQUEST)

class ProjectBaseView:

    '''BaseView for project functionallity'''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProjectCreatorOrAdmin]

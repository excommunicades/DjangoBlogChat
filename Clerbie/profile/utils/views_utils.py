import json
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.layers import get_channel_layer

from django.http import JsonResponse

from authify.models import Clerbie
from websocket.consumers import connected_users

def get_user_by_request(request_user):

    try:

        user = Clerbie.objects.get(id=str(request_user))

    except Clerbie.DoesNotExist:

        return None

    return user

class IsProjectCreatorOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):

        user = request.user

        if obj.creator == user or user.role == 'admin':
            return True

        return False

class isOfferReceiverOrSender(BasePermission):

    def has_object_permission(self, request, view, obj):

        user = request.user

        if obj.receiver == user or obj.sender or user.role == 'admin':
            return True

        return False

class ProjectBaseView:

    '''BaseView for project functionallity'''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProjectCreatorOrAdmin]

async def send_offer_to_receiver(user_id, offer_data):
    channel_layer = get_channel_layer()
    receiver_channel = connected_users.get(user_id)

    if receiver_channel:

        await receiver_channel.send(text_data=json.dumps(offer_data))
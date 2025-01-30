import json
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from channels.layers import get_channel_layer

from django.http import JsonResponse

from authify.models import Clerbie, BlackList
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


class isNotBlockedUser(BasePermission):

    def has_permission(self, request, view):

        user = view.kwargs.get('user')
        is_blocked_user = request.user.id
        try:
            is_blocked = BlackList.objects.get(user__id=user, blocked_user__id=is_blocked_user)
            user_data = Clerbie.objects.get(id=user)
            raise PermissionDenied({
                            "user": {
                                "username": user_data.nickname,
                                "avatar": user_data.avatar},
                            "errors": "You cannot interact with this user because you are blocked."})

        except BlackList.DoesNotExist:
            return True



class ProjectBaseView:

    '''BaseView for project functionallity'''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProjectCreatorOrAdmin]

async def send_offer_to_receiver(user_id, offer_data):
    channel_layer = get_channel_layer()
    receiver_channel = connected_users.get(user_id)

    if receiver_channel:

        await receiver_channel.send(text_data=json.dumps(offer_data))
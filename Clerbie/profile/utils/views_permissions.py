from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from authify.models import Clerbie, BlackList


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


class isNotBlockedUserReview(BasePermission):

    def has_permission(self, request, view):
        profile = view.kwargs.get('profile_id')
        is_blocked_user = request.user.id
        try:
            is_blocked = BlackList.objects.get(user__id=profile, blocked_user__id=is_blocked_user)
            user_data = Clerbie.objects.get(id=is_blocked_user)
            raise PermissionDenied({
                            "user": {
                                "username": user_data.nickname,
                                "avatar": user_data.avatar},
                            "errors": "You cannot write review to this user because you are blocked."})

        except BlackList.DoesNotExist:
            return True

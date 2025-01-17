from authify.models import Clerbie
from rest_framework.permissions import BasePermission

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
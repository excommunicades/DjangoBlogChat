from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from publish.models import ChatRoom

from api.api_actions.serializers.chat_serializers import ChatListSerializer

class UserChatRoomsView(generics.ListAPIView):

    serializer_class = ChatListSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):

        user = self.request.user

        return ChatRoom.objects.filter(users=user)


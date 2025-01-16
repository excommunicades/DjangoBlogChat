from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response

from django.utils import timezone

from profile.serializers import (
    GetUserDataSerializer,
    UpdateGeneralDataSerializer,
    SocialLinksSerializer,
    CreateProjectSerializer,
    UpdateProjectSerializer,
    InvitationResponseSerializer,
    CreateInvitationSerializer,
)
from profile.utils.views_utils import (
    get_user_by_request
)

from authify.models import Clerbie

from profile.models import (
    Projects,
    Invitation,
)

class Get_User_Data(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = GetUserDataSerializer

    def get(self, request, *args, **kwargs):

        request_user = self.request.user

        user = get_user_by_request(request_user=request_user)

        if user is None:

            return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

class Update_User_GeneralData(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.get(pk=self.request.user.pk)

class Update_Social_Links(generics.UpdateAPIView):
    queryset = Clerbie.objects.all()
    serializer_class = SocialLinksSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.get(pk=self.request.user.pk)

class Create_Project(generics.CreateAPIView):

    queryset = Projects.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]

class Update_Project(generics.UpdateAPIView):

    queryset = Projects.objects.all()
    serializer_class = UpdateProjectSerializer
    authentication_classes = [JWTAuthentication]


class Create_Project_Invite(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request, project_id):

        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        
        sender = request.user

        if project.creator != sender:
            return Response({"detail": "Only the project creator can send invitations."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateInvitationSerializer(data=request.data)
        if serializer.is_valid():
            receiver_id = serializer.validated_data["receiver"]
            expires_at = serializer.validated_data["expires_at"]

            try:
                receiver = Clerbie.objects.get(id=receiver_id)
            except Clerbie.DoesNotExist:
                return Response({"detail": "Receiver user not found."}, status=status.HTTP_404_NOT_FOUND)

            invite = Invitation.objects.create(
                project=project,
                sender=sender,
                receiver=receiver,
                expires_at=expires_at
            )

            return Response({
                "invite_code": str(invite.invite_code),
                "project": project.id,
                "sender": sender.id,
                "receiver": receiver.id,
                "status": invite.status,
                "expires_at": invite.expires_at,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Get_Inbox(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        invitations = Invitation.objects.filter(receiver=user, expires_at__gt=timezone.now()).order_by('-created_at')

        invites_data = []
        for invite in invitations:
            invites_data.append({
                "invite_code": str(invite.invite_code),
                "project": invite.project.name,
                "sender": invite.sender.nickname,
                "expires_at": invite.expires_at,
                "status": invite.status,
                "created_at": invite.created_at,
            })

        return Response({"invitations": invites_data}, status=status.HTTP_200_OK)

class InvitationResponseView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request, invite_code):

        try:
            invite = Invitation.objects.get(invite_code=invite_code)
        except Invitation.DoesNotExist:
            return Response({"detail": "Invitation not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if invite.receiver != user:
            return Response({"detail": "This invitation is not for you."}, status=status.HTTP_403_FORBIDDEN)

        serializer = InvitationResponseSerializer(invite, data=request.data)
        if serializer.is_valid():
            invite.status = serializer.validated_data["status"]
            invite.save()

            if invite.status == 'accepted':
                invite.project.users.add(user)

            return Response({"detail": f"Invitation {invite.status}."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from profile.utils.serializers_utils import (
    ProjectSerializer
)

from profile.serializers.projects_serializers import (
    CreateOfferSerializer,
    UpdateProjectSerializer,
    CreateProjectSerializer,
    OfferResponseSerializer,
    LeaveFromProjectSerializer,
    KickProjectMemberSerializer,
)

from profile.utils.views_utils import (
    get_offer_by_id,
    get_project_by_id,
    ProjectBaseView,
    response_by_status,
    get_offer_response_data,
    create_project_business_logic,

)
from profile.utils.views_permissions import (
    isOfferReceiverOrSender,
    isNotBlockedUser,
)

from profile.models import (
    Clerbie,
    Projects,
    Offers,
)

@extend_schema(tags=['Projects'])
class GetProjectList(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

@extend_schema(tags=['Projects'])
class CreateProject(generics.CreateAPIView):

    queryset = Projects.objects.prefetch_related('technologies')
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Projects'])
class UpdateProject(ProjectBaseView, generics.UpdateAPIView):

    queryset = Projects.objects.prefetch_related('technologies')
    serializer_class = UpdateProjectSerializer

@extend_schema(tags=['Projects'])
class DeleteProject(ProjectBaseView, generics.DestroyAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

    def get_object(self):
        """Override to ensure the project exists and possibly prefetch related data"""

        project = super().get_object()
        return project

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

@extend_schema(tags=['Projects | Offers'])
class CreateProjectOffer(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = CreateOfferSerializer
    permission_classes = [IsAuthenticated]

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

@extend_schema(tags=['Projects | Offers'])
class ResponseOffer(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = OfferResponseSerializer
    permission_classes = [IsAuthenticated]

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


@extend_schema(tags=['Projects | Members'])
class KickProjectMember(ProjectBaseView, generics.DestroyAPIView):

    queryset = Projects.objects.prefetch_related('users')
    serializer_class = KickProjectMemberSerializer

    def delete(self, request, *args, **kwargs):

        project_id = kwargs.get('pk')
        project = self.get_object()

        members_to_kick = request.data.get('members', [])

        if not members_to_kick:
            return Response(
                {"error": f"You didn't choose any users to kick"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for member_id in members_to_kick:
            if member_id != self.request.user.id:
                if project.users.filter(id=member_id).exists():
                    project.users.remove(member_id)
                else:
                    return Response(
                        {"error": f"User with ID {member_id} is not a member of your project."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": f"You can not kick yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"message": "Selected members have been removed from the project."},
            status=status.HTTP_200_OK
        )

@extend_schema(tags=['Projects | Members'])
class LeaveFromProject(generics.DestroyAPIView):

    queryset = Projects.objects.prefetch_related('users')
    serializer_class = LeaveFromProjectSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        project_id = kwargs.get('pk')
        project = self.get_object()
        user_id = self.request.user.id

        if project.creator.id != user_id:

            if project.users.filter(id=user_id).exists():
                project.users.remove(user_id)
            else:
                return Response(
                    {"error": f"You are not a member of this project."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if len(list(project.users.all())) != 1:
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    try:
                        creator_to = serializer.validated_data['creator_to']
                        if creator_to:
                            if int(creator_to) != int(user_id):
                                if project.users.filter(id=creator_to).exists():
                                    project.creator = Clerbie.objects.get(id=creator_to)
                                    project.save()
                                    project.users.remove(user_id)
                                    return Response(
                                                {"message": f"You leaved from this project! New Owner of this project with id {creator_to}"},
                                                status=status.HTTP_200_OK
                                            )
                                else:
                                    return Response(
                                        {"error": f"This user is not a member of your project."},
                                        status=status.HTTP_400_BAD_REQUEST
                                    ) 
                            else:
                                return Response(
                                    {"error": f"You need to transfer your creator status to another member or delete your project."},
                                    status=status.HTTP_400_BAD_REQUEST
                                ) 
                    except:
                        return Response(
                            {"error": f"You need to transfer your creator status to another member or delete your project."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            else:
                project.users.remove(user_id)
                project.delete()
        return Response(
            {"message": "You leaved from this project!"},
            status=status.HTTP_200_OK
        )

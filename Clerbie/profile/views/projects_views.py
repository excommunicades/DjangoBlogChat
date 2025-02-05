from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response

from profile.serializers import (
    ProjectSerializer,
    CreateOfferSerializer,
    UpdateProjectSerializer,
    CreateProjectSerializer,
    OfferResponseSerializer,
)
from profile.utils.views_utils import (
    get_offer_by_id,
    ProjectBaseView,
    response_by_status,
    get_offer_response_data,

)
from profile.utils.views_permissions import (
    isOfferReceiverOrSender,
    isNotBlockedUser,
)

from profile.models import (
    Projects,
    Offers,
)

@extend_schema(tags=['Projects'])
class GetProjectList(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

@extend_schema(tags=['Projects'])
class CreateProject(generics.CreateAPIView):

    queryset = Projects.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]


@extend_schema(tags=['Projects'])
class UpdateProject(ProjectBaseView, generics.UpdateAPIView):

    queryset = Projects.objects.all()
    serializer_class = UpdateProjectSerializer

@extend_schema(tags=['Projects'])
class DeleteProject(ProjectBaseView, generics.DestroyAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

@extend_schema(tags=['Projects'])
class CreateProjectOffer(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = CreateOfferSerializer

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

@extend_schema(tags=['Projects'])
class ResponseOffer(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = OfferResponseSerializer

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

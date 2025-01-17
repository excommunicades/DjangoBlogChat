from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.utils import timezone

from profile.serializers import (
    GetUserProfileSerializer,
    UpdateGeneralDataSerializer,
    SocialLinksSerializer,
    CreateProjectSerializer,
    UpdateProjectSerializer,
    OfferResponseSerializer,
    CreateOfferSerializer,
    ProjectSerializer,
    
    OfferSerializer,
)
from profile.utils.views_utils import (
    get_user_by_request,
    IsProjectCreatorOrAdmin,
    isOfferReceiverOrSender
)

from authify.models import Clerbie

from profile.models import (
    Projects,
    Offers,
)

class Get_Profile(generics.GenericAPIView):

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
    permission_classes = [IsProjectCreatorOrAdmin]


class Delete_Project(generics.DestroyAPIView):

    queryset = Projects.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProjectCreatorOrAdmin]

    def perform_destroy(self, instance):

        super().perform_destroy(instance)

class Create_Project_Offer(generics.GenericAPIView):
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
                offer_type='invite' if project.creator == sender else 'request',
                project=project,
                sender=sender,
                receiver=receiver,
                expires_at=expires_at,
                description=description
            )

            return Response({
                "offer_type": offer.offer_type,
                "offer_code": str(offer.offer_code),
                "project": project.id,
                "sender": sender.id,
                "receiver": receiver.id,
                "status": offer.status,
                "expires_at": offer.expires_at,
                "description": offer.description if offer.description else None,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Get_Inbox(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = OfferSerializer

    def get(self, request):
        user = request.user

        offers = Offers.objects.filter(receiver=user, expires_at__gt=timezone.now()).order_by('-created_at')
        
        serializer = OfferSerializer(offers, many=True)

        return Response({"content": serializer.data}, status=status.HTTP_200_OK)


class Response_Offer(generics.GenericAPIView):
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

        if offer.status == 'accepted':
            if user not in offer.project.users.all():
                offer.project.users.add(user)
                offer.project.save()
            else:
                return Response({"detail": "User already in the project."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": f"Offer {offer.status}."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Delete_Offer(generics.DestroyAPIView):

    queryset = Offers.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [isOfferReceiverOrSender]


class Get_Project_List(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

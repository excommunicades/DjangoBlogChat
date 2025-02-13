from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.utils import timezone
from django.db.models import Q


from profile.serializers.profile_serializers import (
    ProjectSerializer,
    UpdateJobSerializer,
    RemoveJobSerializer,
    ProjectOfferSerializer,
    CreateProjectSerializer,
    UpdateSocialsSerializer,
    FriendsOffersSerializer,
    GetUserProfileSerializer,
    UpdateEducationSerializer,
    RemoveEducationSerializer,
    UpdateGeneralDataSerializer,
    UpdateCertificateSerializer,
    DeleteCertificateSerializer,



)
from profile.serializers.friends_serializers import (
    FriendSerializer,
)
# from profile.serializers.projects_serializers import (

# )


from profile.utils.views_utils import get_user_by_request
from profile.utils.views_permissions import (
    isNotBlockedUser,
    isOfferReceiverOrSender,
)

from authify.models import Clerbie
from profile.models import (
    Offers,
    Clerbie_friends,
    Clerbie_education,
    UserJobExperience,
    Clerbie_certificates,
)

@extend_schema(tags=['Profile'])
class GetProfile(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [isNotBlockedUser, AllowAny]
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

@extend_schema(tags=['Inbox'])
class GetInbox(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer

    def get(self, request):

        user = request.user

        projects_offers = Offers.objects.filter(receiver=user, expires_at__gt=timezone.now()).order_by('-created_at')
        friends_offers = Clerbie_friends.objects.filter(Q(user1=user) | Q(user2=user))

        projects_offers_serializer = ProjectOfferSerializer(projects_offers, many=True)
        friends_offers_serializer = FriendsOffersSerializer(friends_offers, many=True)
        for friend_offer in friends_offers_serializer.data:
            friend_offer['offer_type'] = 'friend_invite'

        return Response({
            "content": {
                "projects_offers": projects_offers_serializer.data,
                "friends_offers": friends_offers_serializer.data
            }
        }, status=status.HTTP_200_OK)

@extend_schema(tags=['Inbox'])
class DeleteOffer(generics.DestroyAPIView):

    queryset = Offers.objects.all()
    serializer_class = CreateProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [isOfferReceiverOrSender, IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Offers.objects.filter(id=self.kwargs['pk'])


@extend_schema(tags=['Profile'])
class UpdateUserGeneralData(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.prefetch_related('technologies').get(pk=self.request.user.pk)


@extend_schema(tags=['Profile'])
class UpdateSocials(generics.UpdateAPIView):

    '''CRUD Operations for Socials in profile'''

    queryset = Clerbie.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateSocialsSerializer

    def get_object(self):

        """Ensures that the user can only update their own profile"""

        user_profile = self.request.user
        
        if not user_profile:
            raise PermissionDenied("Profile does not exist.")
        
        return user_profile

@extend_schema(tags=['Profile'])
class UpdateUserEducation(generics.UpdateAPIView):

    '''Endpoint for add|remove education to user profile '''

    queryset = Clerbie_education.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateEducationSerializer


    def get_object(self):

        """Ensures that the user can only update their own educational in profile"""

        user = self.request.user

        if not user:
            raise PermissionDenied("User does not exist.")

        return user

@extend_schema(tags=['Profile'])
class RemoveEducation(generics.DestroyAPIView):

    '''Removes education from user profile. '''

    serializer_class = RemoveEducationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Clerbie_education.objects.all()

    def destroy(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=self.request.data)

        if serializer.is_valid():
            university = serializer.validated_data['university']
            try:
                education = Clerbie_education.objects.get(user=self.request.user, university=university)
                education.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Clerbie_education.DoesNotExist:
                return Response({"error": "Education record not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Profile'])
class UpdateCertificates(generics.UpdateAPIView):

    '''Updates or creates certificates at user profile'''

    queryset = Clerbie_certificates.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateCertificateSerializer

    def get_object(self):

        user = self.request.user

        if not user:
            raise PermissionDenied("User does not exist.")

        return user

@extend_schema(tags=['Profile'])
class DeleteCertificate(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = DeleteCertificateSerializer

    def get_object(self):

        certificate_id = self.kwargs.get('id')

        certificate = Clerbie_certificates.objects.filter(id=certificate_id).first()

        if not certificate:
            raise PermissionDenied("Certificate does not exist.")

        if certificate.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this certificate.")

        return certificate


@extend_schema(tags=['Profile'])
class UpdateUserJobs(generics.UpdateAPIView):

    '''Endpoint for add|remove education to user profile '''

    queryset = UserJobExperience.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateJobSerializer


    def get_object(self):

        """Ensures that the user can only update their own job in profile"""

        user = self.request.user

        if not user:
            raise PermissionDenied("User does not exist.")

        return user

@extend_schema(tags=['Profile'])
class RemoveJob(generics.DestroyAPIView):

    '''Removes education from user profile. '''

    serializer_class = RemoveJobSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return UserJobExperience.objects.all()

    def destroy(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=self.request.data)

        if serializer.is_valid():
            company = serializer.validated_data['company']
            position = serializer.validated_data['position']
            try:
                job = UserJobExperience.objects.get(user=self.request.user, company=company, position=position)
                job.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except UserJobExperience.DoesNotExist:
                return Response({"error": "Job record not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

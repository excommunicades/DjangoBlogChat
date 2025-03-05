from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import async_to_sync

from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from profile.serializers.profile_serializers import (
    ProjectSerializer,
    UpdateJobSerializer,
    RemoveJobSerializer,
    ProjectOfferSerializer,
    CreateProjectSerializer,
    UpdateSocialsSerializer,
    FriendsOffersSerializer,
    GetUserProfileSerializer,
    UpdateJobTitleSerializer,
    UpdateEducationSerializer,
    RemoveEducationSerializer,
    UpdateGeneralDataSerializer,
    UpdateCertificateSerializer,
    DeleteCertificateSerializer,
    CreateProfileReviewSerializer,
    DeleteProfileReviewSerializer,

)
from profile.serializers.friends_serializers import (
    FriendSerializer,
)
# from profile.serializers.projects_serializers import (

# )


from profile.utils.views_utils import (
    get_user_by_request,
    send_offer_to_receiver,
)
from profile.utils.views_permissions import (
    isNotBlockedUser,
    isNotBlockedUserReview,
    isOfferReceiverOrSender,
)

from authify.models import Clerbie
from profile.models import (
    Offers,
    JobTitles,
    Clerbie_friends,
    Clerbie_education,
    UserJobExperience,
    Clerbie_reviews,
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
        
        request_user = self.kwargs.get('user_id')
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


@extend_schema(tags=['Profile'], methods=['PATCH'])
class UpdateUserGeneralData(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    serializer_class = UpdateGeneralDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        return Clerbie.objects.prefetch_related('technologies').get(pk=self.request.user.pk)


@extend_schema(tags=['Profile'], methods=['PATCH'])
class UpdateSocials(generics.UpdateAPIView):

    '''CRUD Operations for Socials in profile'''

    queryset = Clerbie.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateSocialsSerializer
    http_method_names = ['patch']

    def get_object(self):

        """Ensures that the user can only update their own profile"""

        user_profile = self.request.user
        
        if not user_profile:
            raise PermissionDenied("Profile does not exist.")
        
        return user_profile

@extend_schema(tags=['Profile'], methods=['PATCH'])
class UpdateUserEducation(generics.UpdateAPIView):

    '''Endpoint for add|remove education to user profile '''

    queryset = Clerbie_education.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateEducationSerializer
    http_method_names = ['patch']


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
    lookup_field = 'id'

    def get_queryset(self):
        return Clerbie_education.objects.all()


    def perform_destroy(self, instance):

        '''Check if the eduication belongs to the current user before deleting.'''

        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this education from profile.")

        super().perform_destroy(instance)


@extend_schema(tags=['Profile'], methods=['PATCH'])
class UpdateCertificates(generics.UpdateAPIView):

    '''Updates or creates certificates at user profile'''

    queryset = Clerbie_certificates.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateCertificateSerializer
    http_method_names = ['patch']

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
    lookup_field = 'id'

    def get_queryset(self):
        return Clerbie_certificates.objects.all()

    def perform_destroy(self, instance):

        '''Check if the certificate belongs to the current user before deleting.'''

        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this certificate.")

        super().perform_destroy(instance)



@extend_schema(tags=['Profile'], methods=['PATCH'])
class UpdateUserJobs(generics.UpdateAPIView):

    '''Endpoint for add|remove education to user profile '''

    queryset = UserJobExperience.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateJobSerializer
    http_method_names = ['patch']

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
    lookup_field = 'id'

    def get_queryset(self):
        return UserJobExperience.objects.all()

    def perform_destroy(self, instance):

        '''Check if the job experience belongs to the current user before deleting.'''

        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this job experience.")

        super().perform_destroy(instance)

@extend_schema(tags=['Profile'])
class CreateProfileReview(generics.CreateAPIView):

    queryset = Clerbie_reviews.objects.all()
    serializer_class = CreateProfileReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [isNotBlockedUserReview, IsAuthenticated]

    def perform_create(self, serializer):
        
        user = self.request.user
        profile = get_object_or_404(Clerbie, id=self.kwargs['profile_id'])
        if user == profile:
            raise ValidationError({"erorr": "You can not write review for yourself."})

        serializer.save(user=user, profile=profile)
        review = serializer.validated_data
        message = {
            'type': 'review_created',
            'message': f'{user.username} wrote a review for you.',
            'review': {
                'review_owner': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                },
                'reaction': review.get('reaction', None),
                'review': review.get('review', None)
            }
        }

        async_to_sync(send_offer_to_receiver)(profile.id, message)

@extend_schema(tags=['Profile'])
class DeleteProfileReview(generics.DestroyAPIView):

    queryset = Clerbie_reviews.objects.all()
    serializer_class = DeleteProfileReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'review_id'


    def get_object(self):

        profile = get_object_or_404(Clerbie, id=self.kwargs['profile_id'])
        review = get_object_or_404(Clerbie_reviews, id=self.kwargs['review_id'], profile=profile)

        return review

    def perform_destroy(self, instance):

        user = self.request.user
        profile = get_object_or_404(Clerbie, id=self.kwargs['profile_id'])

        if user == instance.user: #  or user == profile - владелец тоже может удалять
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this review.")

@extend_schema(tags=['Profile'])
class UpdateJobTitle(generics.UpdateAPIView):

    '''Endpoint for add|remove job title to user profile '''

    queryset = JobTitles.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UpdateJobTitleSerializer
    http_method_names = ['patch']


    def get_object(self):

        """Ensures that the user can only update their own job title in profile"""

        user = self.request.user

        if not user:
            raise PermissionDenied("User does not exist.")

        return user

@extend_schema(tags=['Profile'])
class RemoveJobTitle(generics.DestroyAPIView):

    '''Removes job title from user's profile'''

    queryset = Clerbie.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_destroy(self, instance):

        instance.job_title = None
        instance.save()

    def delete(self, request, *args, **kwargs):

        instance = request.user

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
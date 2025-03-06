from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404

from profile.models import University, Companies
from teamup.models import Announcement, AnnouncementRequests
from teamup.filters import AnnouncementFilter
from teamup.serializers import (
    GetAnnouncementSerializer,
    GetCompaniesListSerializer,
    ApplyAnnouncementSerializer,
    CreateAnnouncementSerializer,
    UpdateAnnouncementSerializer,
    GetAnnouncementListSerializer,
    GetUniversitiesListSerializer,
    GetAnnouncementRequestsListSerializer,
)
from profile.utils.views_utils import send_offer_to_receiver

@extend_schema(tags=['Announcements'])
class CreateAnnouncement(generics.CreateAPIView):

    '''Create Announcement of project (if u are creator of project)'''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateAnnouncementSerializer

@extend_schema(tags=['Announcements'])
class UpdateAnnouncement(generics.UpdateAPIView):

    '''Update announcement of project'''

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAnnouncementSerializer
    http_method_names = ['patch']

@extend_schema(tags=['Announcements'])
class GetAnnouncementList(generics.ListAPIView):

    '''Return List of announcements'''

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnnouncementFilter

@extend_schema(tags=['Announcements'])
class GetAnnouncement(generics.RetrieveAPIView):

    '''Return User's additional information about announcement of project'''

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementSerializer


@extend_schema(tags=['Announcements'])
class DeleteAnnouncement(generics.DestroyAPIView):

    '''Delete User's announcement for project'''

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementSerializer

    def perform_destroy(self, instance):
        user = self.request.user

        if user != instance.owner:
            raise PermissionDenied("You do not have permission to delete this announcement.")

        instance.delete()

@extend_schema(tags=['Announcements | functionality'])
class ApplyAnnouncement(generics.CreateAPIView):

    queryset = AnnouncementRequests.objects.all()
    serializer_class = ApplyAnnouncementSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_announcement(self):

        announcement_id = self.kwargs.get('announcement_id')
        announcement = get_object_or_404(Announcement, id=announcement_id)
        return announcement

    def get_serializer_context(self):

        context = super().get_serializer_context()
        announcement = self.get_announcement()
        context['announcement'] = announcement
        return context

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            announcenemnt_request = serializer.data

            websocket_announcement_apply_data = {
                "type": 'announcement_apply',
                "announcenemnt": {
                    "announcenemnt_id": announcenemnt_request['announcement']['id'],
                    "announcenemnt_title": announcenemnt_request['announcement']['title'],
                    "announcenemnt_project": announcenemnt_request['announcement']['project_id']
                },
                "applier": {
                    "sender_username": self.request.user.username,
                    "sender_nickname": self.request.user.nickname,
                },
                "created_at": announcenemnt_request['created_at'],
            }

            async_to_sync(send_offer_to_receiver)(announcenemnt_request['announcement']['owner'], websocket_announcement_apply_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Announcements | functionality'])
class GetAnnouncementRequestsList(generics.ListAPIView):

    serializer_class = GetAnnouncementRequestsListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return AnnouncementRequests.objects.filter(announcement__in=Announcement.objects.filter(owner=self.request.user))


# GetCompaniesList, GetUniversitiesList

class GetCompaniesList(generics.ListAPIView):

    queryset = Companies.objects.all()
    serializer_class = GetCompaniesListSerializer


class GetUniversitiesList(generics.ListAPIView):

    queryset = University.objects.all()
    serializer_class = GetUniversitiesListSerializer

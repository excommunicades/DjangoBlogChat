from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from teamup.models import Announcement
from teamup.serializers import (
    CreateAnnouncementSerializer,
    UpdateAnnouncementSerializer,
    GetAnnouncementSerializer,
    GetAnnouncementListSerializer,
)

@extend_schema(tags=['Announcements'])
class CreateAnnouncement(generics.CreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateAnnouncementSerializer

@extend_schema(tags=['Announcements'])
class UpdateAnnouncement(generics.UpdateAPIView):

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAnnouncementSerializer
    http_method_names = ['patch']

@extend_schema(tags=['Announcements'])
class GetAnnouncementList(generics.ListAPIView):

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementListSerializer


@extend_schema(tags=['Announcements'])
class GetAnnouncement(generics.RetrieveAPIView):

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementSerializer


@extend_schema(tags=['Announcements'])
class DeleteAnnouncement(generics.DestroyAPIView):

    queryset = Announcement.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetAnnouncementSerializer

    def perform_destroy(self, instance):
        user = self.request.user

        if user != instance.owner:
            raise PermissionDenied("You do not have permission to delete this announcement.")

        instance.delete()
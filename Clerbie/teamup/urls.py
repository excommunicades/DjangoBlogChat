from django.urls import path

from teamup.views import (
    GetAnnouncement,
    GetCompaniesList,
    ApplyAnnouncement,
    CreateAnnouncement,
    UpdateAnnouncement,
    DeleteAnnouncement,
    GetAnnouncementList,
    GetUniversitiesList,
    GetAnnouncementRequestsList,
)

urlpatterns = [

    # announcements object
    path('announcements/create', CreateAnnouncement.as_view(), name='create-announcement'),
    path('announcements/update/<int:pk>', UpdateAnnouncement.as_view(), name='update-announcement'),
    path('announcements/list', GetAnnouncementList.as_view(), name='announcement-list'),
    path('announcements/get/<int:pk>', GetAnnouncement.as_view(), name='get-announcement'),
    path('announcements/delete/<int:pk>', DeleteAnnouncement.as_view(), name='delete-announcement'),

    # announcement functionallity

    path('announcements/requests/apply/<int:announcement_id>', ApplyAnnouncement.as_view(), name='apply-announcement'),
    path('announcements/requests/list', GetAnnouncementRequestsList.as_view(), name='get-announcement-request-list'),

    # additional information endpoints
    path('companies/list', GetCompaniesList.as_view(), name='get-companies-list'),
    path('universities/list', GetUniversitiesList.as_view(), name='get-universities-list')
]

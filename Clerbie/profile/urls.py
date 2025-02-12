from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from profile.views.profile_views import (
    GetInbox,
    GetProfile,
    DeleteOffer,
    UpdateSocials,
    RemoveEducation,
    DeleteCertificate,
    UpdateCertificates,
    UpdateUserEducation,
    UpdateUserGeneralData,
)
from profile.views.projects_views import (
    CreateProject,
    UpdateProject,
    DeleteProject,
    ResponseOffer,
    GetProjectList,
    LeaveFromProject,
    KickProjectMember,
    CreateProjectOffer,

)
from profile.views.friends_views import (
    GetFriendsList,
    CreateFriendship,
    RemoveFriendship,
    DeleteFriendOffer,
    RespondToFriendship,
)

urlpatterns = [

    # Profile data
    path('', GetProfile.as_view(), name='get-mine-data'),
    path('<int:user>', GetProfile.as_view(), name='get-user-data'),

    # Update profile data
    path('general/update', UpdateUserGeneralData.as_view(), name='update-general-data'),
    path('socials/update', UpdateSocials.as_view(), name='update-social-links'),
    path('education/update', UpdateUserEducation.as_view(), name='update-education'),
    path('education/remove', RemoveEducation.as_view(), name='remove-education'),
    path('certificates/update', UpdateCertificates.as_view(), name='update-add-certificate'),
    path('certificates/delete/<int:id>', DeleteCertificate.as_view(), name='delete-certificate'),


    # Friend Actions

    path('friends/offers/create/<int:friend_id>', CreateFriendship.as_view(), name='offer-to-user-add-to-friendlist'),
    path('friends/offers/response/<uuid:offer_code>', RespondToFriendship.as_view(), name='repsonse-to-friend-invite'),
    path('friends/offers/delete/<uuid:offer_code>', DeleteFriendOffer.as_view(), name='delete-friend-offer'),
    path('friends/remove/<int:friend_id>', RemoveFriendship.as_view(), name='remove-friend'),
    path('friends/list', GetFriendsList.as_view(), name='get-friend-list'),

    # Projects Actions
    path('projects', GetProjectList.as_view(), name='project-list'),
    path('projects/create', CreateProject.as_view(), name='create-project'),
    path('projects/update/<int:pk>', UpdateProject.as_view(), name='update-project'),
    path('projects/delete/<int:pk>', DeleteProject.as_view(), name='delete-project'),
    path('projects/<int:pk>/members/kick', KickProjectMember.as_view(), name='kick-member-from-project'),
    path('projects/<int:pk>/members/leave', LeaveFromProject.as_view(), name='leave-from-project'),
    
    # Project offer actions
    path('projects/members/offers/create/<int:project_id>', CreateProjectOffer.as_view(), name='create_offer'),
    path('projects/members/offers/response/<uuid:offer_code>', ResponseOffer.as_view(), name='offer-response'),

    # Inbox actions
    path('inbox', GetInbox.as_view(), name='get-offers'),
    path('inbox/delete/<int:pk>', DeleteOffer.as_view(), name='delete-offers')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

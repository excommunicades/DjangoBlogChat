from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from profile.views import(
    GetProfile,
    GetInbox, 
    DeleteOffer,
    CreateProject,
    UpdateProject,
    DeleteProject,
    ResponseOffer,
    GetProjectList,
    GetFriendsList,
    CreateFriendship,
    RemoveFriendship,
    UpdateSocialLinks,
    CreateProjectOffer, 
    RespondToFriendship,
    UpdateUserGeneralData,
)

urlpatterns = [

    # Profile data
    path('', GetProfile.as_view(), name='get-mine-data'),
    path('<int:user>', GetProfile.as_view(), name='get-user-data'),

    # Update profile data
    path('update-general', UpdateUserGeneralData.as_view(), name='update-general-data'),
    path('update-socials', UpdateSocialLinks.as_view(), name='update-social-links'),

    # Friend Actions

    path('friends/add/<int:friend_id>', CreateFriendship.as_view(), name='offer-to-user-add-to-friendlist'),
    path('friends/response/<uuid:offer_code>', RespondToFriendship.as_view(), name='repsonse-to-friend-invite'),
    path('friends/remove/<int:friend_id>', RemoveFriendship.as_view(), name='remove-friend-from-'),
    path('friends/list', GetFriendsList.as_view(), name='get-friend-list'),

    # Projects Actions
    path('projects', GetProjectList.as_view(), name='project-list'),
    path('create-project', CreateProject.as_view(), name='create-project'),
    path('update-project/<int:pk>', UpdateProject.as_view(), name='update-project'),
    path('delete-project/<int:pk>', DeleteProject.as_view(), name='delete-project'),
    
    # Project offer actions
    path('offer/create/<int:project_id>', CreateProjectOffer.as_view(), name='create_offer'),
    path('offer/response/<uuid:offer_code>', ResponseOffer.as_view(), name='offer-response'),

    # Inbox actions
    path('inbox', GetInbox.as_view(), name='get-offers'),
    path('inbox/delete/<int:pk>', DeleteOffer.as_view(), name='delete-offers')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from profile.views import(
    Get_User_Data,
    Update_User_GeneralData,
    Update_Social_Links,
    Create_Project,
    Update_Project,
    Create_Project_Invite, 
    Get_Inbox, 
    InvitationResponseView,
    Get_Project_List
)

urlpatterns = [

    # Profile data
    path('user-data', Get_User_Data.as_view(), name='get-user-data'),

    # Update profile data
    path('update-general', Update_User_GeneralData.as_view(), name='update-general-data'),
    path('update-socials', Update_Social_Links.as_view(), name='update-social-links'),

    # Projects Actions
    path('projects', Get_Project_List.as_view(), name='project-list'),
    path('create-project', Create_Project.as_view(), name='create-project'),
    path('update-project/<int:pk>', Update_Project.as_view(), name='update-project'),
    path('create-invite/<int:project_id>', Create_Project_Invite.as_view(), name='create_invitation'),
    path('response-invite/<uuid:invite_code>', InvitationResponseView.as_view(), name='invitation-response'),

    # Inbox
    path('inbox/', Get_Inbox.as_view(), name='inbox'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from profile.views import(
    Get_Profile,
    Update_User_GeneralData,
    Update_Social_Links,
    Create_Project,
    Update_Project,
    Delete_Project,
    Create_Project_Offer, 
    Get_Inbox, 
    Response_Offer,
    Delete_Offer,
    Get_Project_List,
    Create_Friendship,
    Respond_To_Friendship,
    GetFriendsList,
    Remove_Friendship
)

urlpatterns = [

    # Profile data
    path('', Get_Profile.as_view(), name='get-mine-data'),
    path('<int:user>', Get_Profile.as_view(), name='get-user-data'),

    # Update profile data
    path('update-general', Update_User_GeneralData.as_view(), name='update-general-data'),
    path('update-socials', Update_Social_Links.as_view(), name='update-social-links'),

    # Friend Actions

    path('friends/add/<int:friend_id>', Create_Friendship.as_view(), name='offer-to-user-add-to-friendlist'),
    path('friends/response/<uuid:offer_code>', Respond_To_Friendship.as_view(), name='repsonse-to-friend-invite'),
    path('friends/remove/<int:friend_id>', Remove_Friendship.as_view(), name='remove-friend-from-'),
    path('friends/list', GetFriendsList.as_view(), name='get-friend-list'),

    # Projects Actions
    path('projects', Get_Project_List.as_view(), name='project-list'),
    path('create-project', Create_Project.as_view(), name='create-project'),
    path('update-project/<int:pk>', Update_Project.as_view(), name='update-project'),
    path('delete-project/<int:pk>', Delete_Project.as_view(), name='delete-project'),
    
    # Project offer actions
    path('offer/create/<int:project_id>', Create_Project_Offer.as_view(), name='create_offer'),
    path('offer/response/<uuid:offer_code>', Response_Offer.as_view(), name='offer-response'),

    # Inbox actions
    path('inbox', Get_Inbox.as_view(), name='get-offers'),
    path('inbox/delete/<int:pk>', Delete_Offer.as_view(), name='delete-offers')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

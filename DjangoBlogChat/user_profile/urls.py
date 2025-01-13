from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from user_profile.views import(
    Get_User_Data,
    # Set_User_Avatar,
    Update_User_GeneralData,
    Update_Social_Links
)

urlpatterns = [
    path('user-data', Get_User_Data.as_view(), name='get-user-data'),
    # path('update-avatar', Set_User_Avatar.as_view(), name='update-user-avatar'),
    path('update-general', Update_User_GeneralData.as_view(), name='update-general-data'),
    path('update-socials', Update_Social_Links.as_view(), name='update-social-links'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

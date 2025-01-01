from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from user_profile.views import(
    Get_User_Data,
    Set_User_Avatar,
)

urlpatterns = [
    path('user-data', Get_User_Data.as_view(), name='get-user-data'),
    path('update-avatar', Set_User_Avatar.as_view(), name='update-user-avatar'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

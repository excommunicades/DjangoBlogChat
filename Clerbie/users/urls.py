from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from users.views import (
    GetUserList,
    GetUserData,
    BlockUserView,
    BlockUserListView,
)

urlpatterns = [

    # Users data 

    path('list/', GetUserList.as_view(), name='user-list'),
    path('data/<int:pk>', GetUserData.as_view(), name='user-data'),

    # Blacklist actions

    path('blacklist/add/<int:blocked_user_id>', BlockUserView.as_view(), name='add-user-to-blacklist'),
    path('blacklist/list', BlockUserListView.as_view(), name='blacklisted-user-list'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from users.views import (
    GetUserList,
    GetUserData,
    BlockUserView,
)

urlpatterns = [
    path('list/', GetUserList.as_view(), name='user-list'),
    path('data/<int:pk>', GetUserData.as_view(), name='user-data'),
    path('block/<int:blocked_user_id>', BlockUserView.as_view(), name='block-user'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

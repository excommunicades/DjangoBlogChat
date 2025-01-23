from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from users.views import (
    GetUserList,
    GetUserData,
)

urlpatterns = [
    path('list/', GetUserList.as_view(), name='user-list'),
    path('data/<int:pk>', GetUserData.as_view(), name='user-data')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

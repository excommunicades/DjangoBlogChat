from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from users.views import (
    User_List,
    User_Data
)

urlpatterns = [
    path('list/', User_List.as_view(), name='user-list'),
    path('data/<int:pk>', User_Data.as_view(), name='user-data')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

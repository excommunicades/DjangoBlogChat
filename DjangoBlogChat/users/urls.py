from django.urls import path

from users.views import (
    User_List,
    User_Data,
)

urlpatterns = [
    path('list/', User_List.as_view(), name='user-list'),
    path('data/<int:pk>', User_Data.as_view(), name='user-data')
]

from django.urls import path

from user_profile.views import(
    Get_User_Data,
)

urlpatterns = [
    path('user-data', Get_User_Data.as_view(), name='get-user-data')
]

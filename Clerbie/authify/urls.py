from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from authify.views import (
    Register_User,
    Login_User,
    Logout_User,
    Get_User_Data,
    Register_Confirm,
    Request_Password_Recovery,
    Password_Recovery,
    refresh_token_view
)


urlpatterns = [
    
    #main functionallity
    path('register', Register_User.as_view(), name="user_registration"),
    path('login', Login_User.as_view(), name="user_authorization"),
    path('logout', Logout_User.as_view(), name='user_logout'),
    path('user-data', Get_User_Data.as_view(), name='user_data'),
    
    #register actions
    path('register-confirm', Register_Confirm.as_view(), name="user_registration_confirm"),

    #password actions
    path('request-password-recovery', Request_Password_Recovery.as_view(), name="request_password_recovery"),
    path('password-recovery', Password_Recovery.as_view(), name="password_recovery"),

    #token
    path('token/refresh', refresh_token_view, name='token_refresh'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


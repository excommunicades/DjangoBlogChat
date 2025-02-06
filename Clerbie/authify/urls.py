from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from authify.views import (
    LoginUser,
    LogoutUser,
    GetUserData,
    RegisterUser,
    ChangePassword,
    RegisterConfirm,
    PasswordRecovery,
    refresh_token_view,
    RequestPasswordRecovery,
)


urlpatterns = [
    
    #main functionallity
    path('register', RegisterUser.as_view(), name="user_registration"),
    path('login', LoginUser.as_view(), name="user_authorization"),
    path('logout', LogoutUser.as_view(), name='user_logout'),
    path('user-data', GetUserData.as_view(), name='user_data'),
    
    #register actions
    path('register-confirm', RegisterConfirm.as_view(), name="user_registration_confirm"),

    #password actions
    path('request-password-recovery', RequestPasswordRecovery.as_view(), name="request_password_recovery"),
    path('password-recovery', PasswordRecovery.as_view(), name="password_recovery"),
    path('change-password', ChangePassword.as_view(), name='change_password'),

    #token
    path('token/refresh', refresh_token_view, name='token_refresh'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


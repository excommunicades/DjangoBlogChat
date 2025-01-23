from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from authify.views import (
    RegisterUser,
    LoginUser,
    LogoutUser,
    GetUserData,
    RegisterConfirm,
    RequestPasswordRecovery,
    PasswordRecovery,
    refresh_token_view
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

    #token
    path('token/refresh', refresh_token_view, name='token_refresh'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path

from blog_user.views import (
    Register_User,
    Login_User,
    Register_Confirm
)

urlpatterns = [
    path('register', Register_User.as_view(), name="user_registration"),
    path('login', Login_User.as_view(), name="user_authorization"),
    path('register-confirm', Register_Confirm.as_view(), name="user_registration_confirm"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
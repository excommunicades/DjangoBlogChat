import uuid
from drf_spectacular.utils import extend_schema

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from authify.serializers import (
    AccountSerializer,
    GetUserDataSerializer,
    RegistrationSerializer,
    ResetAccountSerializer,
    AuthorizationSerializer,
    LogoutResponseSerializer,
    ChangePasswordSerializer,
    PasswordRecoverySerializer,
    RegistrationConfirmSerializer,
    RequestPasswordRecoverySerializer,
    )
from authify.utils import (
    RegisterUserUtil,
    get_user_by_request,
    AuthenticationService,
    set_tokens_in_cookies,
    PasswordRecoveryService,
    RequestPasswordRecoveryService,
    receive_user_data_delete_chats,
    RegistrationConfirmationService,
)
from authify.models import Clerbie


@extend_schema(tags=['Registration'])
class RegisterUser(generics.CreateAPIView):

    """
    Endpoint for user registration.
    Creates a new user and sends a confirmation code to the user's email.
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            user_data = serializer.validated_data
            registration_service = RegisterUserUtil(user_data)
            code = registration_service.execute()
            return Response({"message": "Please check your email for confirmation with code"}, status=status.HTTP_200_OK)

        errors = serializer.errors
        formatted_errors = {}

        for field, error_list in errors.items():
            for i, e in enumerate(error_list):
                match e:
                    case 'blog user with this nickname already exists.':
                        error_list[i] = 'User with this nickname already exists.'
                    case 'blog user with this email already exists.':
                        error_list[i] = 'User with this email already exists.'
            formatted_errors[field] = " ".join(error_list)

        return Response(
            {"errors": formatted_errors},
            status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(tags=['Registration'])
class RegisterConfirm(generics.GenericAPIView):

    """
    Endpoint for confirming registration with a code.
    Confirms the user registration if the code is valid.
    """

    serializer_class = RegistrationConfirmSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            code = serializer.data.get('code')
            user_data = cache.get(code)
            if user_data:
                try:
                    confirmation_service = RegistrationConfirmationService(code, user_data)
                    confirmation_service.execute()
                    return Response({"message": "Registration successfully."}, status=status.HTTP_200_OK)
                except ValueError as e:
                    return Response({"errors": {"message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"errors": {"message": "Wrong code."}}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"errors": {"message": "Wrong code."}}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authorization'])
class LoginUser(generics.GenericAPIView):

    """
    Endpoint for user authentication.
    Returns access and refresh tokens upon successful login.
    """

    serializer_class = AuthorizationSerializer

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():

            errors = serializer.errors
            nickname_error = errors.get('nickname', [])

            if nickname_error:
                nickname_error_msg = str(nickname_error[0])
                if nickname_error_msg in ['User does not exist.', 'This field is required.']:
                    return Response({'errors': {'nickname': nickname_error_msg}}, status=status.HTTP_404_NOT_FOUND)
            password_error = errors.get('password', [])
            if password_error and str(password_error[0]) == 'Wrong password.':
                return Response({'errors': {'password': 'Wrong password.'}}, status=status.HTTP_404_NOT_FOUND)

            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        user_data = serializer.validated_data
        auth_service = AuthenticationService(user_data)

        try:
            user, refresh_token, access_token = auth_service.execute()
            try:
                user_data = Clerbie.objects.get(email=str(user))
            except Clerbie.DoesNotExist:
                try:
                    user_data = Clerbie.objects.get(nickname=str(user))
                except:
                    raise serializers.ValidationError({"nickname": "User does not exist."})

            response = Response({
                'access_token': access_token,
                "user": {
                    "username": user_data.username,
                    "nickname": user_data.nickname,
                    "pk": user_data.pk,
                    "email": user_data.email
                }
            })

            set_tokens_in_cookies(response=response, refresh_token=str(refresh_token))

            return response

        except Exception as e:
            return Response({'errors': {'error': str(e)}}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(tags=['Authorization'])
class LogoutUser(generics.GenericAPIView):

    '''Logoutes a user from his session.

        [Deletes refreshToken cookie]
    '''

    serializer_class = LogoutResponseSerializer

    def post(self, request, *args, **kwargs):

        response = Response({
            "message": "User logget out successfully.",
        }, status=status.HTTP_200_OK)

        response.delete_cookie(
                        'refreshToken',
                        path='/',
                        samesite='Lax')

        return response


@extend_schema(tags=['Token'])
@csrf_exempt
@api_view(['POST'])
def refresh_token_view(request):

    refresh_token = request.COOKIES.get('refreshToken')

    if not refresh_token:

        return Response({'error': 'Refresh token is missing in cookies'}, status=status.HTTP_401_UNAUTHORIZED)

    try:

        token = RefreshToken(refresh_token)

        access_token = token.access_token

        return Response({
            'access_token': str(access_token)
        })

    except Exception as e:

        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


# TODO: Bind Email functionallity

# class BindEmail(generics.UpdateAPIView):

#     queryset = Clerbie.objects.all()
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get_object(self):
#         user = self.request.user
#         if user is None:
#             raise PermissionDenied("Authentication required.")
#         return user

@extend_schema(tags=['Password'])
class RequestPasswordRecovery(generics.GenericAPIView):

    """
    Endpoint for requesting a password recovery code.

    This endpoint accepts the user's email, checks if the user exists,
    and sends a password recovery code to the user's email.
    """

    serializer_class = RequestPasswordRecoverySerializer

    def post(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return Response(
                {"error": "You are already logged in. You cannot request a password recovery code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            user_data = serializer.validated_data
            recovery_service = RequestPasswordRecoveryService(user_data)

            try:
                recovery_code = recovery_service.execute()
                request.session['user_data'] = user_data
                return Response({"message": "We sent you a password recovery code."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"errors": {"message": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        errors = serializer.errors
        formatted_errors = {field: error[0] for field, error in errors.items()}

        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Password'])
class PasswordRecovery(generics.GenericAPIView):

    """
    Endpoint for submitting the password recovery code and new password.

    This endpoint allows the user to submit the recovery code and a new password to change their password.
    """

    serializer_class = PasswordRecoverySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            recovery_code = serializer.data.get('code')

            password = serializer.data.get('password')

            recovery_service = PasswordRecoveryService(recovery_code, password)

            try:

                user = recovery_service.execute()

                return Response({"message": "Password successfully changed."}, status=status.HTTP_200_OK)

            except ValueError as e:

                return Response({"errors": {"message": str(e)}}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(tags=['Password'])
class ChangePassword(generics.UpdateAPIView):

    queryset = Clerbie.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        user = self.request.user
        if user is None:
            raise PermissionDenied("Authentication required.")
        return user

    def perform_update(self, serializer):

        user = self.get_object()
        serializer.update(user, serializer.validated_data)

    def update(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"message": "Password was changed successfully!"}, status=status.HTTP_200_OK)
        
        return Response({"errors": {
            field: error[0] for field, error in serializer.errors.items()
        }}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['User-data'])
class GetUserData(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = GetUserDataSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        request_user = self.request.user

        user = get_user_by_request(request_user=request_user)

        if user is None:
            return Response({"error": "You should be authorized."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(user, context={'request_user': request.user})

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAccount(generics.DestroyAPIView):

    """
    API endpoint that allows the authenticated user to delete their own account.
    """

    queryset = Clerbie.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        """
        Perform the deletion.
        """
        instance.delete()

    def delete(self, request, *args, **kwargs):

        self.perform_destroy(self.get_object())

        response = Response({"message": "Your account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
                        'refreshToken',
                        path='/',
                        samesite='Lax')
        response.delete_cookie(
                        'access_token',
                        path='/',
                        samesite='Strict')
        
        return response

class FreezeAccount(generics.UpdateAPIView):
    # TODO: Implement Freeze functionallity
    pass

class ResetAccount(generics.UpdateAPIView):
    """
    API endpoint for deleting the user and recreating the account with the same email, 
    nickname, password, and role, avoiding unique constraint violation.
    """

    queryset = Clerbie.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ResetAccountSerializer
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = self.get_object()

            username, nickname, email, password, role, user_id = receive_user_data_delete_chats(user, serializer.validated_data.get('password', None))
            new_user = Clerbie.objects.create_user(
                id=user_id, username=username, nickname=nickname, email=email, password=password, role=role
            )

            user_data = {"nickname": new_user.nickname, "password": new_user.password}
            auth_service = AuthenticationService(user_data)

            try:
                refresh_token, access_token = auth_service.generate_tokens(new_user)

                response = Response({
                    "access_token": access_token,
                    "user": {
                        "username": new_user.username,
                        "nickname": new_user.nickname,
                        "pk": new_user.pk,
                        "email": new_user.email
                    }
                })
                set_tokens_in_cookies(response=response, refresh_token=str(refresh_token))

                return response

            except:
                return Response({'errors': {'error': "Permissions denied."}}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'error': serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)
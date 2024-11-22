from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.core.cache import cache

from blog_user.serializers import (
    RegistrationSerializer,
    AuthorizationSerializer,
    RegistrationConfirmSerializer,
    RequestPasswordRecoverySerializer,
    PasswordRecoverySerializer,
    GetUserDataSerializer,
    )

from blog_user.utils import (
    RegisterUser,
    RegistrationConfirmationService,
    AuthenticationService,
    RequestPasswordRecoveryService,
    PasswordRecoveryService,
    get_user_by_request
)



from blog_user.models import BlogUser


class Register_User(generics.CreateAPIView):

    """
    Endpoint for user registration.
    Creates a new user and sends a confirmation code to the user's email.
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            user_data = serializer.validated_data

            registration_service = RegisterUser(user_data)

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



class Register_Confirm(generics.GenericAPIView):

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


class Login_User(generics.GenericAPIView):

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

                return Response({'errors': {'password': 'Wrong password.'}}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        user_data = serializer.validated_data

        auth_service = AuthenticationService(user_data)
        
        try:

            user, refresh_token, access_token = auth_service.execute()

            try:
                print(user)
                user_data = BlogUser.objects.get(email=str(user))
                print(user_data)
            except BlogUser.DoesNotExist:

                try:

                    user_data = BlogUser.objects.get(nickname=str(user))

                except:

                    raise serializers.ValidationError({"nickname": "User does not exist."})

            return Response({
                'refresh_token': refresh_token,
                'access_token': access_token,
                "user": {
                    "username": user_data.username,
                    "nickname": user_data.nickname,
                    "pk": user_data.pk,
                    "email": user_data.email
                }
            })

        except Exception as e:

            return Response({'errors': {'error': str(e)}}, status=status.HTTP_401_UNAUTHORIZED)


class Request_Password_Recovery(generics.GenericAPIView):

    """
    Endpoint for requesting a password recovery code.

    This endpoint accepts the user's email, checks if the user exists,
    and sends a password recovery code to the user's email.
    """

    serializer_class = RequestPasswordRecoverySerializer

    def post(self, request, *args, **kwargs):

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


class Password_Recovery(generics.GenericAPIView):

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


class Get_User_Data(generics.GenericAPIView):

    """
    Endpoint for getting user data.

    This endpoint allows the take info about user account.
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = GetUserDataSerializer

    def get(self, request, *args, **kwargs):

        request_user = self.request.user

        user = get_user_by_request(request_user=request_user)

        if user is None:

            return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
                    "username": user.username,
                    "nickname": user.nickname,
                    "email": user.email,
                    "is_activated": user.is_actived,
                    "role": user.role
                }, status=status.HTTP_200_OK)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
import urllib.request
import json
import os

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

from .models import CustomUser
from .serializers import (
    RegisterSerializer, UserSerializer,
    GoogleAuthSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
)
from .utils import send_password_reset_email
from destinations.models import Destination
from destinations.serializers import DestinationSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class FavoriteListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = request.user.favorite_destinations.all()
        serializer = DestinationSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.favorite_destinations.add(destination)
        return Response({'status': 'added', 'destination_id': pk}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.favorite_destinations.remove(destination)
        return Response({'status': 'removed', 'destination_id': pk}, status=status.HTTP_200_OK)


class WishlistListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist = request.user.wishlist_destinations.all()
        serializer = DestinationSerializer(wishlist, many=True, context={'request': request})
        return Response(serializer.data)


class WishlistToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.wishlist_destinations.add(destination)
        return Response({'status': 'added', 'destination_id': pk}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.wishlist_destinations.remove(destination)
        return Response({'status': 'removed', 'destination_id': pk}, status=status.HTTP_200_OK)


class VisitedListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        visited = request.user.visited_destinations.all()
        serializer = DestinationSerializer(visited, many=True, context={'request': request})
        return Response(serializer.data)


class VisitedToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.visited_destinations.add(destination)
        return Response({'status': 'added', 'destination_id': pk}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        destination = get_object_or_404(Destination, pk=pk)
        request.user.visited_destinations.remove(destination)
        return Response({'status': 'removed', 'destination_id': pk}, status=status.HTTP_200_OK)


class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not settings.GOOGLE_OAUTH_CLIENT_ID:
            return Response(
                {'error': 'Google OAuth is not configured on this server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        email = None
        name = ''
        picture = ''

        code = serializer.validated_data.get('code')
        if code:
            try:
                flow = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                            "redirect_uris": ["postmessage"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                    },
                    scopes=["openid", "email", "profile"],
                    redirect_uri="postmessage",
                )
                flow.fetch_token(code=code)
                credentials = flow.credentials
                id_info = id_token.verify_oauth2_token(
                    credentials.id_token,
                    GoogleRequest(),
                    settings.GOOGLE_OAUTH_CLIENT_ID
                )
                email = id_info.get('email')
                name = id_info.get('name', '')
                picture = id_info.get('picture', '')
            except Exception as e:
                return Response(
                    {'error': f'Failed to exchange Google code: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        credential = serializer.validated_data.get('credential')
        if not email and credential:
            try:
                id_info = id_token.verify_oauth2_token(
                    credential,
                    GoogleRequest(),
                    settings.GOOGLE_OAUTH_CLIENT_ID
                )
                email = id_info.get('email')
                name = id_info.get('name', '')
                picture = id_info.get('picture', '')
            except Exception:
                pass

            if not email:
                try:
                    req = urllib.request.Request(
                        'https://www.googleapis.com/oauth2/v3/userinfo',
                        headers={'Authorization': f'Bearer {credential}'}
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        userinfo = json.loads(resp.read().decode())
                        email = userinfo.get('email')
                        name = userinfo.get('name', '')
                        picture = userinfo.get('picture', '')
                except Exception as e:
                    return Response(
                        {'error': f'Failed to verify Google credential: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if not email:
            return Response(
                {'error': 'Invalid Google credential or unable to retrieve email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use filter().first() to avoid MultipleObjectsReturned when the
            # same email was previously registered via email/password.
            user = CustomUser.objects.filter(email=email).first()

            if not user:
                base_username = email.split('@')[0].replace('.', '_')
                username = base_username
                for i in range(1, 11):
                    if not CustomUser.objects.filter(username=username).exists():
                        break
                    username = f"{base_username}_{i}"

                user = CustomUser(
                    username=username,
                    email=email,
                    first_name=name.split(' ')[0] if name else '',
                    last_name=' '.join(name.split(' ')[1:]) if name and len(name.split(' ')) > 1 else '',
                )
                user.set_unusable_password()
                user.save()
                if picture:
                    user.avatar_url = picture
                    user.save(update_fields=['avatar_url'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'User lookup/creation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        message = {'message': 'If this email is registered, a password reset link has been sent.'}

        user = CustomUser.objects.filter(email=email).first()
        if user:
            try:
                send_password_reset_email(user)
            except Exception as e:
                return Response(
                    {'error': f'Failed to send email: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(message, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=pk)
        except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Reset link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful. You can now log in.'}, status=status.HTTP_200_OK)
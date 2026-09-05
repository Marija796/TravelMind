import logging

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.files.base import ContentFile
from django.db.models import Q
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
import ssl
import certifi

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

logger = logging.getLogger(__name__)

# Used for every urllib HTTPS call below (Google userinfo lookup, profile
# picture download) instead of ssl.create_default_context()'s bare default,
# which trusts whatever root CAs happen to be installed in the OS
# certificate store. On Windows that store commonly picks up a root
# certificate (frequently injected by antivirus/security software that
# intercepts HTTPS) with a malformed Basic Constraints extension, which
# fails verification with "Basic Constraints of CA cert not marked
# critical" - a real bug this fixes, not a theoretical one: Google sign-in
# failed with a generic "Invalid or expired Google credential" error even
# though the credential itself was fine, because the userinfo request never
# even reached Google - it failed local TLS verification and was swallowed
# by the broad except below. Pinning to certifi's maintained, known-good CA
# bundle instead sidesteps whatever is (or isn't) trusted by the OS.
_HTTPS_CONTEXT = ssl.create_default_context(cafile=certifi.where())

from .models import CustomUser
from .serializers import (
    RegisterSerializer, UserSerializer, VerifiedTokenObtainPairSerializer,
    GoogleAuthSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    VerifyEmailSerializer, ResendVerificationSerializer,
)
from .utils import send_password_reset_email, send_verification_email, email_verification_token
from .vectors import calculate_similarity, RATING_LIKE_THRESHOLD
from destinations.models import Destination
from destinations.serializers import DestinationSerializer
from destinations.views import _annotated_destination_queryset


def _safe_profile_image_url(request, user):
    # other.profile_image is truthy for any non-empty ImageFieldFile, but
    # .url still raises if the field has no name (blank) or the underlying
    # file record is orphaned - guard both cases rather than the bare
    # `if other.profile_image` check this used to rely on.
    if not user.profile_image or not user.profile_image.name:
        return None
    try:
        return request.build_absolute_uri(user.profile_image.url)
    except ValueError:
        return None


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        try:
            send_verification_email(user)
        except Exception:
            # A failed/misconfigured email send must never turn a
            # successful account creation into a 500 - the user can still
            # request a fresh link via ResendVerificationEmailView once
            # email delivery is fixed.
            logger.exception('Failed to send verification email to user id=%s', user.pk)


class VerifiedTokenObtainPairView(TokenObtainPairView):
    """Backs /api/users/login/ - see VerifiedTokenObtainPairSerializer."""
    serializer_class = VerifiedTokenObtainPairSerializer


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=pk)
        except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verified:
            # Checked before check_token: the token hash includes
            # is_verified, so a link clicked a second time after a
            # successful first verification would otherwise fail the token
            # check and show a confusing "invalid link" error instead of
            # this friendly, correct explanation.
            return Response({'message': 'Your email is already verified. You can log in.'}, status=status.HTTP_200_OK)

        if not email_verification_token.check_token(user, token):
            return Response({'error': 'Verification link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return Response({'message': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        # Same generic response regardless of whether the email exists or
        # is already verified - mirrors PasswordResetRequestView's
        # enumeration protection below.
        message = {'message': 'If this email is registered and not yet verified, a verification link has been sent.'}

        user = CustomUser.objects.filter(email__iexact=email).first()
        if user and not user.is_verified:
            try:
                send_verification_email(user)
            except Exception:
                logger.exception('Failed to resend verification email to user id=%s', user.pk)

        return Response(message, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        # SlugRelatedField (preferred_travel_type/preferred_season) doesn't
        # accept '' as "no value" the way the old CharFields did - the
        # frontend sends '' for "unset" (TravelType | ''), so normalize it
        # to None here before it reaches the serializer.
        data = request.data
        if hasattr(data, 'copy'):
            data = data.copy()
            for field in ('preferred_travel_type', 'preferred_season'):
                if field in data and data[field] == '':
                    data[field] = None
        serializer = UserSerializer(
            request.user, data=data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


SIMILAR_USERS_LIMIT = 8


def _compute_similar_users(request, me):
    """
    Shared by SimilarUsersView (a user viewing their own matches) and
    AdminSimilarUsersView (an admin inspecting/verifying any user's
    matches) - same real, weighted, live calculation either way, so the
    admin tool can't drift from what a normal user actually sees.
    """
    my_favorites = set(me.favorite_destinations.values_list('id', flat=True))
    my_wishlist = set(me.wishlist_destinations.values_list('id', flat=True))
    my_rated = set(me.reviews.filter(rating__gte=RATING_LIKE_THRESHOLD).values_list('destination_id', flat=True))
    has_preferences = any([
        me.preferred_travel_type_id, me.preferred_season_id,
        me.preferred_activities, me.budget, me.trip_duration_preference,
        my_favorites, my_wishlist, my_rated,
    ])
    if not has_preferences:
        # Without this guard every criterion in calculate_similarity is
        # incomparable (nothing set on "me") and it returns 0.0 for every
        # comparison - a meaningless "everyone ties at 0%" list rather than
        # a real empty state the frontend can render distinctly.
        return {'count': 0, 'results': [], 'reason': 'no_preferences_set'}

    # role='admin' is this app's actual admin designation (see
    # core.permissions.IsAdminRole) - is_staff/is_superuser are Django's
    # separate built-in flags for the /admin/ site and aren't necessarily
    # set together with role, so both must be checked to keep every kind of
    # admin account out of the candidate pool.
    others = CustomUser.objects.exclude(pk=me.pk).exclude(role='admin').filter(
        is_staff=False, is_superuser=False, is_active=True,
    ).prefetch_related('favorite_destinations', 'wishlist_destinations', 'reviews')

    scored = []
    for other in others:
        # .values_list() always issues a fresh query and ignores the
        # prefetch_related() cache above - only .all() (or iterating the
        # manager directly, as here) reads from it. Using values_list() here
        # would silently turn this back into one query per candidate user.
        other_favorites = {d.id for d in other.favorite_destinations.all()}
        other_wishlist = {d.id for d in other.wishlist_destinations.all()}
        other_rated = {r.destination_id for r in other.reviews.all() if r.rating >= RATING_LIKE_THRESHOLD}
        similarity = calculate_similarity(
            me, other, favorites_a=my_favorites, favorites_b=other_favorites,
            wishlist_a=my_wishlist, wishlist_b=other_wishlist, rated_a=my_rated, rated_b=other_rated,
        )
        scored.append((similarity, other))
    scored.sort(key=lambda item: item[0], reverse=True)
    scored = scored[:SIMILAR_USERS_LIMIT]

    results = [{
        'id': other.id,
        'username': other.username,
        'gender': other.gender,
        'short_summary': other.short_summary,
        'profile_image': _safe_profile_image_url(request, other),
        'similarity': round(similarity * 100, 1),
    } for similarity, other in scored]

    return {'count': len(results), 'results': results, 'reason': None}


DESTINATION_INTERESTED_USERS_LIMIT = 8


class DestinationInterestedUsersView(APIView):
    """
    Similar Users, made contextual to one destination instead of a standalone
    dashboard feature: for the destination being viewed, finds real users who
    favorited/wishlisted it (direct interest), and - only when that pool is
    thin - backfills with users who favorited/wishlisted a *similar*
    destination (same travel type or same country). Every candidate is then
    ranked by the same real, weighted calculate_similarity score used
    elsewhere in the app (never random/hardcoded), highest first.

    Query shape is deliberately fixed regardless of how many users match:
    one query for the direct-interest set (+1 prefetch), at most one more
    for the similar-destination id list and one more for the backfill set
    (+1 prefetch) - never one query per candidate user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, pk=destination_id)
        me = request.user
        my_favorites = set(me.favorite_destinations.values_list('id', flat=True))
        my_wishlist = set(me.wishlist_destinations.values_list('id', flat=True))
        my_rated = set(me.reviews.filter(rating__gte=RATING_LIKE_THRESHOLD).values_list('destination_id', flat=True))

        base_qs = CustomUser.objects.exclude(pk=me.pk).exclude(role='admin').filter(
            is_active=True, is_staff=False, is_superuser=False,
        )

        direct_qs = base_qs.filter(
            Q(favorite_destinations=destination) | Q(wishlist_destinations=destination)
        ).distinct().prefetch_related('favorite_destinations', 'wishlist_destinations', 'reviews')
        candidates = list(direct_qs)
        interest_kind = {u.id: 'direct' for u in candidates}

        if len(candidates) < DESTINATION_INTERESTED_USERS_LIMIT:
            similar_destination_ids = list(
                Destination.objects.filter(
                    Q(travel_type_id=destination.travel_type_id) | Q(country=destination.country)
                ).exclude(pk=destination.pk).values_list('id', flat=True)
            )
            if similar_destination_ids:
                extra_qs = base_qs.exclude(pk__in=interest_kind.keys()).filter(
                    Q(favorite_destinations__id__in=similar_destination_ids)
                    | Q(wishlist_destinations__id__in=similar_destination_ids)
                ).distinct().prefetch_related('favorite_destinations', 'wishlist_destinations', 'reviews')
                for other in extra_qs:
                    if other.id not in interest_kind:
                        candidates.append(other)
                        interest_kind[other.id] = 'similar_destination'

        scored = []
        for other in candidates:
            # .all() (not .values_list()) so this reads the prefetch_related
            # cache above instead of issuing a fresh query per candidate.
            other_favorites = {d.id for d in other.favorite_destinations.all()}
            other_wishlist = {d.id for d in other.wishlist_destinations.all()}
            other_rated = {r.destination_id for r in other.reviews.all() if r.rating >= RATING_LIKE_THRESHOLD}
            similarity = calculate_similarity(
                me, other, favorites_a=my_favorites, favorites_b=other_favorites,
                wishlist_a=my_wishlist, wishlist_b=other_wishlist, rated_a=my_rated, rated_b=other_rated,
            )
            scored.append((similarity, other))
        scored.sort(key=lambda item: item[0], reverse=True)
        scored = scored[:DESTINATION_INTERESTED_USERS_LIMIT]

        results = [{
            'id': other.id,
            'username': other.username,
            'gender': other.gender,
            'short_summary': other.short_summary,
            'profile_image': _safe_profile_image_url(request, other),
            'similarity': round(similarity * 100, 1),
            'interest': interest_kind[other.id],
        } for similarity, other in scored]

        return Response({'count': len(results), 'results': results})


def _engagement_serializer_context(request):
    # Same select_related/annotation + id-set-context pattern as
    # destinations/views.py's DestinationListView, so listing a user's own
    # favorites/wishlist/visited doesn't fall back to DestinationSerializer's
    # per-object queries (travel_type/best_season joins, rating aggregation,
    # is_favorited/is_wishlisted/is_visited existence checks) for every
    # returned destination.
    user = request.user
    return {
        'request': request,
        'favorited_ids': set(user.favorite_destinations.values_list('id', flat=True)),
        'wishlisted_ids': set(user.wishlist_destinations.values_list('id', flat=True)),
        'visited_ids': set(user.visited_destinations.values_list('id', flat=True)),
    }


class FavoriteListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = _annotated_destination_queryset().filter(favorited_by=request.user)
        serializer = DestinationSerializer(favorites, many=True, context=_engagement_serializer_context(request))
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
        wishlist = _annotated_destination_queryset().filter(wishlisted_by=request.user)
        serializer = DestinationSerializer(wishlist, many=True, context=_engagement_serializer_context(request))
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
        visited = _annotated_destination_queryset().filter(visited_by=request.user)
        serializer = DestinationSerializer(visited, many=True, context=_engagement_serializer_context(request))
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
            except Exception:
                # Logged for diagnosis, but the client only ever sees a
                # generic message - the real exception can contain OAuth
                # library/network internals that shouldn't reach the user.
                logger.exception('Failed to exchange Google authorization code')
                return Response(
                    {'error': 'Failed to sign in with Google. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        credential = serializer.validated_data.get('credential')
        if not email and credential:
            # First try: verify as a JWT ID token (returned by credential/One-Tap flow)
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

            # Second try: treat credential as an access token and call userinfo endpoint
            # (used by the implicit flow which returns access_token instead of id_token)
            if not email:
                try:
                    req = urllib.request.Request(
                        'https://www.googleapis.com/oauth2/v3/userinfo',
                        headers={'Authorization': f'Bearer {credential}'}
                    )
                    with urllib.request.urlopen(req, timeout=10, context=_HTTPS_CONTEXT) as resp:
                        userinfo = json.loads(resp.read().decode())
                        email = userinfo.get('email')
                        name = userinfo.get('name', '')
                        picture = userinfo.get('picture', '')
                except Exception:
                    # Logged at full detail server-side (this catches
                    # everything from a genuinely invalid/expired token to a
                    # local TLS/network failure that never reached Google at
                    # all - see _HTTPS_CONTEXT) - the client only ever sees
                    # the generic message below, same reasoning as the code-
                    # exchange except block above.
                    logger.exception('Failed to verify Google credential')
                    return Response(
                        {'error': 'Invalid or expired Google credential. Please try again.'},
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
                    # Google has already proven this account owns the
                    # email address (that's what the OAuth token exchange
                    # above verified) - a separate email-verification loop
                    # would be redundant.
                    is_verified=True,
                )
                user.set_unusable_password()
                user.save()
                if picture:
                    # Best-effort: a slow/broken Google CDN URL must never
                    # block or fail the OAuth login itself.
                    try:
                        req = urllib.request.Request(
                            picture, headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req, timeout=5, context=_HTTPS_CONTEXT) as resp:
                            content = resp.read()
                        user.profile_image.save(
                            f'google_{user.pk}.jpg', ContentFile(content), save=True
                        )
                    except Exception:
                        pass
            elif not user.is_verified:
                # An existing account (e.g. registered the normal
                # email/password way but never clicked the verification
                # link) that now signs in with Google has, by that very
                # act, proven ownership of the email address just as
                # surely as a brand-new Google signup does above - the
                # same reasoning, applied after the fact instead of at
                # creation. Without this, Google sign-in itself still
                # succeeds (this view never checked is_verified), but the
                # account stays marked unverified, so a *later* plain
                # username/password login attempt is wrongly rejected by
                # VerifiedTokenObtainPairSerializer with "email not
                # verified" - confusing after they just successfully
                # signed in.
                user.is_verified = True
                user.save(update_fields=['is_verified'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user, context={'request': request}).data,
            }, status=status.HTTP_200_OK)

        except Exception:
            logger.exception('Google sign-in user lookup/creation failed')
            return Response(
                {'error': 'Something went wrong while signing you in. Please try again.'},
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
            except Exception:
                # Deliberately still returns the same generic `message`
                # below rather than an error - surfacing send failures
                # (or their internal detail, e.g. SMTP config) here would
                # both leak that this email is registered and expose
                # infrastructure internals, undoing the enumeration
                # protection the generic message exists for.
                logger.exception('Failed to send password reset email to user id=%s', user.pk)

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
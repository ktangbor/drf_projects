from json import JSONDecodeError
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from . import serializers, models
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from utils.mailing import Util
from django.http import HttpResponsePermanentRedirect
import os


class RegisterView(generics.CreateAPIView):
    """
    Endpoint for registering as a new user
    """
    serializer_class = serializers.RegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = serializers.RegisterSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Json decoding error"}, status=400)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestPasswordResetEmail(generics.GenericAPIView):
    """
    Endpoint for requesting password reset by providing a valid registered user email
    It returns a reset token
    It could be implemented by emailing a reset link
    """

    serializer_class = serializers.ResetPasswordEmailRequestSerializer
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # current_site = get_current_site(
            #     request=request).domain
            # relativeLink = reverse(
            #     'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            # redirect_url = request.data.get('redirect_url', '')
            # absurl = 'http://' + current_site + relativeLink
            # email_body = 'Hello, \n Use link below to reset your password  \n' + \
            #              absurl + "?redirect_url=" + redirect_url
            # data = {'email_body': email_body, 'to_email': user.email,
            #         'email_subject': 'Reset your passsword'}
            # Util.send_email(data)
            return Response({'uidb64': uidb64, 'reset token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'failure': 'No user with this mail'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = serializers.SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = serializers.SetNewPasswordSerializer
    parser_classes = [JSONParser]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = serializers.UpdateProfileSerializer
    queryset = models.Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]


class AddSkillView(generics.CreateAPIView):
    serializer_class = serializers.AddSkillSerializer
    queryset = models.ProgrammingSkill.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = serializers.AddSkillSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Json decoding error"}, status=400)


class RemoveSkillView(generics.GenericAPIView):
    serializer_class = serializers.AddSkillSerializer
    queryset = models.ProgrammingSkill.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]

    def delete(self, request, pk=None):
        user = self.request.user
        profile = models.Profile.objects.get(user=user)
        skill = self.get_object()
        if profile == skill.profile:
            skill.delete()
            return Response('Skill Removed', status=status.HTTP_200_OK)
        else:
            return Response('Invalid skill', status=status.HTTP_400_BAD_REQUEST)

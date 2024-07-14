import asyncio

from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework_simplejwt.tokens import RefreshToken
from telethon import TelegramClient

from .models import MyUser
from .serializers import LoginSerializer, ActivationSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyUserSerializer


class RegistrationView(APIView):
    serializer_class = MyUserSerializer

    def post(self, request):
        serializer = MyUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.activation_code = ''
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendActivationCodeAPIView(APIView):

    def post(self, request):
        username = request.data.get('username')
        tg = request.data.get('tg')
        user = get_object_or_404(MyUser, username=username)
        user.create_activation_code()
        user.save()
        asyncio.run(self.send_activation_code_via_telegram(user, tg))

        return Response({'message': 'Код активации отправлен'})

    async def send_activation_code_via_telegram(self, user, username):
        if user.activation_code:
            api_id = '23641712'
            api_hash = '273fb50fc859e8f2a3537c9c8678ed38'
            bot_token = '7468362553:AAF1qoGiclhmhSswHrTOT7H3eVnO9UEMG1Y'

            async with TelegramClient('session_name', api_id, api_hash) as client:
                await client.start(bot_token=bot_token)
                message_text = f'Ваш код активации: {user.activation_code}'
                await client.send_message(username, message_text)
                await client.disconnect()
                print('Код активации успешно отправлен!')
        else:
            print('Код активации не сгенерирован.')


class ActivationView(APIView):
    serializer_class = ActivationSerializer

    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate()
            return Response('Account successfully activated', status=200)


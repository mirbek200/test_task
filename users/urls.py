from django.urls import path
from .views import RegistrationView, LoginView, SendActivationCodeAPIView, ActivationView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('send_activation_code/', SendActivationCodeAPIView.as_view(), name='send_activation_code'),
    path('activation_account/', ActivationView.as_view(), name='activation_account'),
]

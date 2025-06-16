from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', obtain_auth_token),
    path('profile/', views.profile_view, name='profile'),
]

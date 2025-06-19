from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', obtain_auth_token),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    path('blogs/', views.blog_list_create, name='blog-list-create'),
    path('blogs/<int:pk>/', views.blog_detail, name='blog-detail'),
]
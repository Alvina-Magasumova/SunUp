from django.urls import path
from .views import login_page, register_page, profile_page, index_page

urlpatterns = [
    path('', index_page, name='home'),
    path('login/', login_page, name='login-page'),
    path('register/', register_page, name='register-page'),
    path('profile/', profile_page, name='profile-page'),
]
from django.urls import path

from .views import RegisterView, MeView, TopicListView, SetTopicsView, SetCityView, \
    index_page, login_page, register_page, profile_page, verify_email


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('me/topics/', SetTopicsView.as_view(), name='set-topics'),
    path('me/city/', SetCityView.as_view(), name='set-city'),
    path('', index_page, name='home'),
    path('login/', login_page, name='login-page'),
    path('register/', register_page, name='register-page'),
    path('profile/', profile_page, name='profile-page'),
    path('verify/', verify_email, name='verify-email'),
]
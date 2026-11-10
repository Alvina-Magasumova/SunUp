from django.urls import path

from .views import RegisterView, MeView, TopicListView, SetTopicsView, SetCityView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('me/topics/', SetTopicsView.as_view(), name='set-topics'),
    path('me/city/', SetCityView.as_view(), name='set-city'),
]
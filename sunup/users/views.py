from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import UserRegistrationSerializer, UserProfileSerializer, TopicSerializer
from .models import Topic
from .services.geocoding import fetch_city_coordinates
from asgiref.sync import async_to_sync


class RegisterView(APIView):
    """Регистрация нового пользователя."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
        description='Регистрация нового пользователя. Возвращает id, username, email.',
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля текущего пользователя"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]  # Только для авторизованных!

    def get_object(self):
        """Возвращаем текущего пользователя (того, чей токен прислали)"""
        return self.request.user


class TopicListView(ListAPIView):
    """Список всех активных тем"""
    queryset = Topic.objects.filter(is_active=True)
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]


class SetTopicsView(APIView):
    """Установить темы для текущего пользователя"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'topics': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['technology', 'science'],
                    },
                },
            },
        },
        responses={200: None},
        description='Установить темы для текущего пользователя. Передайте список slug\'ов.',
    )

    def put(self, request):
        # Получаем список slug'ов из запроса
        topic_slugs = request.data.get('topics', [])

        if not isinstance(topic_slugs, list):
            return Response(
                {'error': 'topics должен быть списком'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Находим темы по slug
        topics = Topic.objects.filter(slug__in=topic_slugs, is_active=True)

        # Если какие-то slug'и не найдены — сообщаем
        found_slugs = set(topics.values_list('slug', flat=True))
        missing = set(topic_slugs) - found_slugs
        if missing:
            return Response(
                {'error': f'Темы не найдены: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Устанавливаем темы пользователю (заменяем все)
        request.user.topics.set(topics)

        return Response({
            'status': 'ok',
            'topics': [t.slug for t in topics],
        })


class SetCityView(APIView):
    """Установить город для текущего пользователя"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'city_name': {'type': 'string', 'example': 'Москва'},
                },
            },
        },
        responses={200: None},
        description='Установить город. Координаты подтягиваются автоматически из Open-Meteo.',
    )
    def post(self, request):
        city_name = request.data.get('city_name', '').strip()

        if not city_name:
            return Response(
                {'error': 'city_name обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Вызываем асинхронный сервис синхронно
        coordinates = async_to_sync(fetch_city_coordinates)(city_name)

        if not coordinates:
            return Response(
                {'error': f'Город "{city_name}" не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Сохраняем в профиль
        request.user.city_name = coordinates['name']
        request.user.city_latitude = coordinates['latitude']
        request.user.city_longitude = coordinates['longitude']
        request.user.save(update_fields=['city_name', 'city_latitude', 'city_longitude'])

        return Response({
            'status': 'ok',
            'city_name': request.user.city_name,
            'latitude': request.user.city_latitude,
            'longitude': request.user.city_longitude,
        })

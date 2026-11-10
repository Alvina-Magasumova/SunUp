from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Topic

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""

    # Пароль — write_only, чтобы он не попадал в ответ API
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate(self, attrs):
        """Проверяем, что пароли совпадают"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Пароли не совпадают.'}
            )
        return attrs

    def create(self, validated_data):
        """Создаём пользователя с захешированным паролем"""
        # Убираем password_confirm — его нет в модели
        validated_data.pop('password_confirm')

        # create_user сам захеширует пароль
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования профиля"""

    # Показываем темы как список их названий (строк), а не как ID
    topics = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        # Поля, которые пользователь увидит и сможет менять
        fields = (
            'id', 'username', 'email', 'city_name',
            'timezone', 'morning_time', 'is_digest_enabled', 'topics'
        )
        # Эти поля нельзя менять через API
        read_only_fields = ('id', 'username', 'email')

class TopicSerializer(serializers.ModelSerializer):
    """Сериализатор для справочника тем."""
    class Meta:
        model = Topic
        fields = ('id', 'slug', 'name')
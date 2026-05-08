from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin_owner', True)
        extra_fields.setdefault('email_verified', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=32, blank=True, null=True)

    email_verified = models.BooleanField('Email подтверждён', default=False)
    is_admin_owner = models.BooleanField('Главный администратор', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Story(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PUBLISHED = 'published'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'На подтверждении'),
        (STATUS_PUBLISHED, 'Опубликована'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories',
        verbose_name='Автор'
    )

    fio = models.CharField('ФИО героя/рассказчика', max_length=255)
    story_date = models.DateField('Дата истории')
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6)
    text = models.TextField('Текст истории')

    status = models.CharField(
        'Статус',
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'История'
        verbose_name_plural = 'Истории'

    def __str__(self):
        return f'{self.fio} — {self.story_date}'


class StoryMedia(models.Model):
    MEDIA_PHOTO = 'photo'
    MEDIA_VIDEO = 'video'
    MEDIA_AUDIO = 'audio'

    MEDIA_CHOICES = [
        (MEDIA_PHOTO, 'Фото'),
        (MEDIA_VIDEO, 'Видео'),
        (MEDIA_AUDIO, 'Аудио'),
    ]

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='media_files',
        verbose_name='История'
    )

    media_type = models.CharField(
        'Тип файла',
        max_length=10,
        choices=MEDIA_CHOICES
    )

    file = models.FileField(
        'Файл',
        upload_to='stories/media/'
    )

    uploaded_at = models.DateTimeField(
        'Загружено',
        auto_now_add=True
    )

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Файл истории'
        verbose_name_plural = 'Файлы истории'

    def __str__(self):
        return f'{self.get_media_type_display()} для {self.story}'


class Review(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_reviews'
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )

    text = models.TextField('Текст отзыва')

    rating = models.PositiveSmallIntegerField(
        'Оценка',
        default=5
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
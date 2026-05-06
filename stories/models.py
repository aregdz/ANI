from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Телефон обязателен')
        user = self.model(phone=phone, username=phone, **extra_fields)
        user.set_password(password or phone)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin_owner', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=32, unique=True)
    phone = models.CharField('Телефон', max_length=32, unique=True)
    is_admin_owner = models.BooleanField('Главный администратор', default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone


class Story(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PUBLISHED = 'published'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На подтверждении'),
        (STATUS_PUBLISHED, 'Опубликована'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories', verbose_name='Автор')
    fio = models.CharField('ФИО героя/рассказчика', max_length=255)
    story_date = models.DateField('Дата истории')
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6)
    text = models.TextField('Текст истории')
    photo = models.ImageField('Фото', upload_to='stories/photos/', blank=True, null=True)
    video = models.FileField('Видео', upload_to='stories/videos/', blank=True, null=True)
    audio = models.FileField('Аудио', upload_to='stories/audio/', blank=True, null=True)
    status = models.CharField('Статус', max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'История'
        verbose_name_plural = 'Истории'

    def __str__(self):
        return f'{self.fio} — {self.story_date}'

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User, Story, Review


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [super(MultipleFileField, self).clean(d, initial) for d in data]

        return [super().clean(data, initial)]


class EmailRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует'
            )

        return email


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()

        email = cleaned.get('email', '').strip().lower()
        password = cleaned.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            raise forms.ValidationError('Неверный email или пароль')

        cleaned['user'] = user
        return cleaned


class StoryForm(forms.ModelForm):
    photos = MultipleFileField(
    label='Фото',
    required=False,
    widget=MultipleFileInput(attrs={
        'multiple': True,
        'accept': 'image/*',
        })
    )

    videos = MultipleFileField(
        label='Видео',
        required=False,
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'video/*',
        })
    )

    audios = MultipleFileField(
        label='Аудио',
        required=False,
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'audio/*',
        })
    )

    class Meta:
        model = Story
        fields = [
            'fio',
            'story_date',
            'latitude',
            'longitude',
            'text',
            'photos',
            'videos',
            'audios',
        ]

        widgets = {
            'story_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 7}),
            'latitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': '55.755800',
            }),
            'longitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': '37.617300',
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']

        widgets = {
            'rating': forms.RadioSelect(
                choices=[
                    (5, '★★★★★'),
                    (4, '★★★★'),
                    (3, '★★★'),
                    (2, '★★'),
                    (1, '★'),
                ]
            ),
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите отзыв к этой истории...',
            })
        }
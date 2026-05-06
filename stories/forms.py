from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, Story


class EmailRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')

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
    class Meta:
        model = Story
        fields = [
            'fio',
            'story_date',
            'latitude',
            'longitude',
            'photo',
            'video',
            'audio',
            'text',
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
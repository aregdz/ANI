from django import forms
from django.contrib.auth import authenticate
from .models import User, Story


class PhoneRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone', 'password']

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip().replace(' ', '')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким телефоном уже существует')
        return phone

    def save(self, commit=True):
        phone = self.cleaned_data['phone']
        password = self.cleaned_data['password']
        user = User(phone=phone, username=phone)
        user.set_password(password)
        if commit:
            user.save()
        return user


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(label='Телефон')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get('phone', '').strip().replace(' ', '')
        password = cleaned.get('password')
        user = authenticate(phone=phone, password=password)
        if not user:
            raise forms.ValidationError('Неверный телефон или пароль')
        cleaned['user'] = user
        return cleaned


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['fio', 'story_date', 'latitude', 'longitude', 'photo', 'video', 'audio', 'text']
        widgets = {
            'story_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 7}),
            'latitude': forms.NumberInput(attrs={'step': '0.000001', 'placeholder': '55.755800'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001', 'placeholder': '37.617300'}),
        }

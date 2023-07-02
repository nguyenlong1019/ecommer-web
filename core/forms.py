from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': "Username",
        'class': "form-control",
        'required': True
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Password",
        'class': "form-control",
        'required': True
    }))


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': "Enter Username",
        'class': 'form-control',
        'required': True
    }), label="Username: ")

    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': "Enter Email",
        'class': 'form-control',
        'required': True
    }), label="Email: ")

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Enter Password",
        'class': 'form-control',
        'required': True
    }), label="Password: ")

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Confirm Password",
        'class': 'form-control',
        'required': True
    }), label="Confirm Password: ")



from django import forms
from .models import Ativo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PesquisaForm(forms.Form):
    palavra_chave = forms.CharField(label='palavra_chave', max_length=100)


class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['periodicidade', 'limite_inferior', 'limite_superior']


class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

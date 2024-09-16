from django import forms
from .models import AtivoDetalhe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PesquisaForm(forms.Form):
    palavra_chave = forms.CharField(label='palavra_chave', max_length=100)


class AtivoDetalheForm(forms.ModelForm):
    class Meta:
        model = AtivoDetalhe
        fields = ['periodicidade', 'limite_inferior', 'limite_superior']


class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    # Customizing widget, forcing every user to authenticate with password
    def __init__(self, *args, **kwargs):
        super(CadastroForm, self).__init__(*args, **kwargs)
        # Remove the unwanted fields
        if 'can_authenticate_with_password' in self.fields:
            del self.fields['can_authenticate_with_password']
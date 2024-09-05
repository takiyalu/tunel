from django import forms
from .models import Ativo


class PesquisaForm(forms.Form):
    palavra_chave = forms.CharField(label='palavra_chave', max_length=100)


class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['periodicidade', 'limite_inferior', 'limite_superior']
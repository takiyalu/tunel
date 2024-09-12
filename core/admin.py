from django.contrib import admin
from .models import Ativo


@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nome', 'ticker', 'periodicidade', 'preco',
                    'limite_superior', 'limite_inferior', 'active', 'updated')

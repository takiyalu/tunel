from django.contrib import admin
from .models import Ativo, AtivoDetalhe


class AtivoDetalheInline(admin.TabularInline):
    model = AtivoDetalhe
    extra = 1  # Number of empty forms to display initially
    fields = ['usuario', 'ativo', 'periodicidade', 'limite_inferior', 'limite_superior']
    # Exclude fields if necessary
    # exclude = ['campo_a_excluir']


@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ticker', 'preco', 'active', 'updated')
    inlines = [AtivoDetalheInline]


@admin.register(AtivoDetalhe)
class AtivoDetalheAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ativo', 'periodicidade', 'limite_inferior', 'limite_superior', 'email_enviado'
                    ,'created', 'updated')
    list_filter = ('usuario', 'ativo')
    search_fields = ('ativo__ticker', 'usuario__username')  # Adjust based on the fields available

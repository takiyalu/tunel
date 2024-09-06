from django.urls import path
from .views import IndexView, PesquisaView, AtivosSalvosView, AtivoView

app_name = 'core'  # This defines the namespace for this app (Useful to be referenced when working with other apps

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('pesquisa/', PesquisaView.as_view(), name='pesquisa'),
    path('salvos/', AtivosSalvosView.as_view(), name='salvos'),
    path('ativo/<str:symbol>/', AtivoView.as_view(), name='ativo-detail'),
    path('ativo/', AtivoView.as_view(), name='ativo'),
]

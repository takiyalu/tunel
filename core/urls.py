from django.urls import path
from .views import (IndexView, PesquisaView, AtivosSalvosView, AtivoView, CadastroView, CustomLoginView,
                    AtualizaPerfilView, PerfilView)
from django.contrib.auth.views import LogoutView

app_name = 'core'  # This defines the namespace for this app (Useful to be referenced when working with other apps

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:login'), name='logout'),
    path('accounts/profile/', PerfilView.as_view(), name='perfil'),
    path('accounts/profile/edit/', AtualizaPerfilView.as_view(), name='atualiza-perfil'),
    path('pesquisa/', PesquisaView.as_view(), name='pesquisa'),
    path('salvos/', AtivosSalvosView.as_view(), name='salvos'),
    path('ativo/<str:symbol>/', AtivoView.as_view(), name='ativo-detail'),
    path('ativo/', AtivoView.as_view(), name='ativo'),
]

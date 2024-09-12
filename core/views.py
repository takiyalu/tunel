from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django.contrib.auth.forms import UserChangeForm
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.conf import settings
from .models import Ativo
from .forms import PesquisaForm, AtivoForm, CadastroForm
import yfinance as yf
import requests
import pandas as pd
from io import StringIO


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    form_class = PesquisaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        http = HttpResponse()
        http['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        http['Pragma'] = 'no-cache'
        http['Expires'] = '0'

        form = self.form_class(self.request.GET or None)

        if form.is_valid():
            palavra_chave = form.cleaned_data.get('palavra_chave')
            # Redirect to PesquisaView with palavra_chave as a query parameter
            return redirect(f'{reverse("core:pesquisa")}?palavra_chave={palavra_chave}')
        return context


class CadastroView(FormView):
    template_name = 'cadastro.html'
    form_class = CadastroForm
    success_url = reverse_lazy('core:login')  # Redirect to login page after successful registration

    def form_valid(self, form):
        user = form.save()
        # Optionally log in the user after registration
        from django.contrib.auth import login
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'login.html'


class PerfilView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'perfil.html'

    def get_object(self):
        return self.request.user  # Return the currently logged-in user


class AtualizaPerfilView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'atualiza_perfil.html'
    success_url = '/accounts/profile/'  # Redirect after successful update

    def get_object(self):
        return self.request.user  # Return the currently logged-in user


class PesquisaView(LoginRequiredMixin, TemplateView):
    template_name = 'pesquisa.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        palavra_chave = self.request.GET.get('palavra_chave')
        chave_api = settings.ALPHA_VANTAGE_API_KEY

        if palavra_chave:
            # Buscando dados da Alpha Vantage
            url = (f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={palavra_chave}&'
                   f'apikey={chave_api}&datatype=csv')
            response = requests.get(url)
            # Processamento de dados
            if response.status_code == 200:
                data = StringIO(response.text)
                df = pd.read_csv(data)
                # A API da Alpha Vantage retorna o símbolo dos ativos com uma letra a mais no final
                # Exemplo: A Sanepar é retornada como "SAPR11.SAO", mas a yfinance precisa que o ticker seja passado
                # como "SAPR11.SA", portanto fazemos o slicing abaixo.
                df.loc[df['region'] == 'Brazil/Sao Paolo', 'symbol'] = df['symbol'].str[:-1]
                context['pesquisa'] = df.to_dict(orient='records')  # Converts DataFrame to list of dicts
            else:
                context['pesquisa'] = []

        return context


class AtivoView(LoginRequiredMixin, FormView):
    template_name = 'ativo.html'
    form_class = AtivoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        symbol = self.kwargs.get('symbol')
        product = yf.Ticker(symbol)
        data = product.history(period="1d")  # Retrieve data for the most recent day
        if not data.empty:
            preco = data.iloc[0]['Close']
        else:
            # caso não haja dado nenhum preco (O mercado para aquele ativo provavelmente ainda não está aberto ou ja
            # fechou) utilizamos o último valor registrado
            preco = product.info['previousClose']
        context.update({**product.info})
        context['preco'] = round(preco, 2)
        return context

    def get(self, request, *args, **kwargs):
        # Check if the request is an AJAX request for validation
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            ticker = request.GET.get('ticker')
            is_monitored = Ativo.objects.filter(ticker=ticker, usuario=request.user).exists()
            return JsonResponse({'is_monitored': is_monitored})

        # If not an AJAX request, handle normally
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        symbol = self.kwargs.get('symbol')
        product = yf.Ticker(symbol)
        context = self.get_context_data(form=form)
        data = product.history(period="1d")  # Retrieve data for the most recent day
        if not data.empty:
            preco = data.iloc[0]['Close']
        else:
            # caso não haja dado nenhum preco (O mercado para aquele ativo provavelmente ainda não está aberto ou ja
            # fechou) utilizamos o último valor registrado
            preco = product.info['previousClose']

        ativo = Ativo(
            nome=product.info['longName'],
            ticker=symbol,
            preco=preco,
            periodicidade=form.cleaned_data['periodicidade'],
            limite_superior=form.cleaned_data['limite_superior'],
            limite_inferior=form.cleaned_data['limite_inferior'],
            usuario=self.request.user
        )

        ativo.save()
        return self.render_to_response(context)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AtivosSalvosView(LoginRequiredMixin, TemplateView):
    template_name = 'ativos_salvos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Campos a serem excluídos
        campos_nao_selecionados = ['created', 'active', 'usuario']

        # Todos os campos do modelo
        todos_os_campos = [campo.name for campo in Ativo._meta.fields]

        # Campos a serem incluídos
        campos_selecionados = [campo for campo in todos_os_campos if campo not in campos_nao_selecionados]

        # Campos editáveis
        campos_editaveis = ['periodicidade', 'limite_inferior', 'limite_superior']
        # Buscando ativos salvos na base de dados
        context['ativos'] = list(Ativo.objects.filter(usuario=self.request.user).values(*campos_selecionados))
        context['editaveis'] = campos_editaveis
        return context

    def post(self, request, *args, **kwargs):
        for chave, valor in request.POST.items():
            if chave.startswith('ativo_'):  # Ensure only relevant fields are processed
                _, id, campo = chave.split('_', 2)  # Recupera id e campo da chave
                try:
                    ativo = Ativo.objects.get(id=id)
                    setattr(ativo, campo, valor.replace(',', '.'))
                    ativo.save()
                except Ativo.DoesNotExist:
                    continue  # Gerencia casos em que o Ativo não é encontrado

        return redirect('core:salvos')

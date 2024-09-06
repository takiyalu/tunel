from django.views.generic import TemplateView, FormView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Ativo
from .forms import PesquisaForm, AtivoForm
import yfinance as yf
import requests
import pandas as pd
from io import StringIO


class IndexView(TemplateView):
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


class PesquisaView(TemplateView):
    template_name = 'pesquisa.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        palavra_chave = self.request.GET.get('palavra_chave')

        if palavra_chave:
            # Buscando dados da Alpha Vantage
            url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={palavra_chave}&apikey=8ZPUWB8RKO3FC9KZ&datatype=csv'
            response = requests.get(url)
            # Processamento de dados
            if response.status_code == 200:
                data = StringIO(response.text)
                df = pd.read_csv(data)
                # A API da Alpha Vantage retorna o símbolo dos ativos com uma letra uma letra a mais no final
                # Exemplo: A Sanepar é retornada como "SAPR11.SAO", mas a yfinance precisa que o ticker seja passado
                # como "SAPR11.SA", portanto fazemos o slicing abaixo.
                df.loc[df['region'] == 'Brazil/Sao Paolo', 'symbol'] = df['symbol'].str[:-1]
                context['pesquisa'] = df.to_dict(orient='records')  # Converts DataFrame to list of dicts
                print(context['pesquisa'])
            else:
                context['pesquisa'] = []

        return context


class AtivoView(FormView):
    template_name = 'ativo.html'
    form_class = AtivoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        symbol = self.kwargs.get('symbol')
        product = yf.Ticker(symbol)
        context.update({**product.info})
        return context

    def get(self, request, *args, **kwargs):
        # Check if the request is an AJAX request for validation
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            ticker = request.GET.get('ticker')
            is_monitored = Ativo.objects.filter(ticker=ticker).exists()
            return JsonResponse({'is_monitored': is_monitored})

        # If not an AJAX request, handle normally
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        symbol = self.kwargs.get('symbol')
        product = yf.Ticker(symbol)
        context = self.get_context_data(form=form)
        ativo = Ativo(
            nome=product.info['longName'],
            ticker=symbol,
            preco=product.info['previousClose'],
            periodicidade=form.cleaned_data['periodicidade'],
            limite_superior=form.cleaned_data['limite_superior'],
            limite_inferior=form.cleaned_data['limite_inferior']
        )
        ativo.save()
        return self.render_to_response(context)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AtivosSalvosView(TemplateView):
    template_name = 'ativos_salvos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Campos a serem excluídos
        campos_nao_selecionados = ['created', 'active']

        # Todos os campos do modelo
        todos_os_campos = [campo.name for campo in Ativo._meta.fields]

        # Campos a serem incluídos
        campos_selecionados = [campo for campo in todos_os_campos if campo not in campos_nao_selecionados]

        # Campos editáveis
        campos_editaveis = ['periodicidade', 'limite_inferior', 'limite_superior']
        # Buscando ativos salvos na base de dados
        context['ativos'] = list(Ativo.objects.values(*campos_selecionados))
        context['editaveis'] = campos_editaveis
        print(context['ativos'])
        return context


    def post(self, request, *args, **kwargs):
        # Process form data here
        for chave, valor in request.POST.items():
            if chave.startswith('ativo_'):  # Ensure only relevant fields are processed
                _, id, campo = chave.split('_', 2)  # Extract id and campo from the key
                try:
                    print(campo + 'socorro')
                    ativo = Ativo.objects.get(id=id)
                    setattr(ativo, campo, valor.replace(',', '.'))
                    ativo.save()
                except Ativo.DoesNotExist:
                    continue  # Handle cases where Ativo is not found

        return redirect('core:salvos')

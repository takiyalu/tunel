from django.views.generic import TemplateView, FormView, View
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
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
            else:
                context['pesquisa'] = []

        return context


class AtivoView(FormView):
    template_name = 'ativo.html'
    form_class = AtivoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ativo_symbol = self.kwargs.get('ativo_symbol')
        # You can now use the product_symbol and product_name in your context
        product = yf.Ticker(ativo_symbol)
        # Update the preco field for the current Ativo instance
        table = {'previousClose': product.info['previousClose'], 'bid': product.info['bid'], 'ask': product.info['ask'],
                 'marketCap': product.info['marketCap'], 'volume': product.info['volume'],
                 'beta': product.info['beta']}
        context['table'] = table
        context['ativo_symbol'] = ativo_symbol
        context = {**context, **product.info, 'form': self.get_form()}
        return context

    def form_valid(self, form):
        # Get additional data
        symbol = self.kwargs.get('ativo_symbol')
        product = yf.Ticker(symbol)
        context = self.get_context_data(form=form)
        if symbol not in Ativo.objects.values_list('ticker', flat=True):

            # Create and save the Ativo object
            ativo = Ativo(
                nome=product.info['longName'],
                ticker=symbol,
                preco=product.info['previousClose'],
                periodicidade=form.cleaned_data['periodicidade'],
                limite_superior=form.cleaned_data['limite_superior'],
                limite_inferior=form.cleaned_data['limite_inferior']
            )
            ativo.save()
            messages.success(self.request, 'Ativo salvo com sucesso')
        else:
            messages.error(self.request, 'Ativo já está sendo monitorado')
        return render(self.request, self.template_name, context)  # Redirect after saving

    def form_invalid(self, form):
        # If the form is invalid, re-render the template with the form errors
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AtivosSalvosView(TemplateView):
    template_name = 'lista_ativos.html'


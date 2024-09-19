import json
from django.views.generic import TemplateView, FormView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.http import JsonResponse, HttpResponseServerError, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import re
from django.conf import settings
from .models import Ativo, AtivoDetalhe
from .forms import PesquisaForm, AtivoDetalheForm, CadastroForm
import yfinance as yf
import requests
import pandas as pd
from io import StringIO

# LoginRequiredMixin ensures that the user must be logged in order to access the template for that view.
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    form_class = PesquisaForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)

        if form.is_valid():
            palavra_chave = form.cleaned_data.get('palavra_chave')
            # Redirect to PesquisaView with palavra_chave as a query parameter
            return redirect(f'{reverse("core:pesquisa")}?palavra_chave={palavra_chave}')

        # If the form is not valid or no form data is provided, proceed normally
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET or None)  # Include form in context
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
        messages.success(request, "Usuário Cadastrado com Sucesso")
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

    def get_success_url(self):
        messages.success(self.request, "Perfil Editado com Sucesso")
        return reverse('core:perfil')  # Redirect after successful update

    def get_object(self):
        return self.request.user  # Return the currently logged-in user


class PesquisaView(LoginRequiredMixin, TemplateView):
    template_name = 'pesquisa.html'

    def get(self, request, *args, **kwargs):
        palavra_chave = request.GET.get('palavra_chave')
        if palavra_chave:
            chave_api = settings.ALPHA_VANTAGE_API_KEY
            # Send an api request to alphavantage search app and returns a table with the stock's information
            url = (f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={palavra_chave}&'
                   f'apikey={chave_api}&datatype=csv')
            response = requests.get(url)
            # When AlphaVantage does not return any data or does not allow any more requests they return a json instead
            # of the csv response.
            content_type = response.headers.get('Content-Type')
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    if 'Information' in data:

                        return render(request, '503.html', {'message': data['Information']}, status=503)
                    else:
                        # Return error response if JSON data is not valid
                        return HttpResponseServerError(render(request, '500.html'))
                except ValueError:
                    messages.error(request, "Response content is not valid JSON.")
                    return redirect(reverse("core:index"))

            elif response.status_code == 200:
                # Process CSV data
                data = StringIO(response.text)
                df = pd.read_csv(data)
                if 'symbol' in df.columns and 'region' in df.columns:
                    # AlphaVantage`s brazilian stock's tickers comes with an extra 'O' in the name that yfinance can't
                    # process, so we remove it below.
                    df.loc[df['region'] == 'Brazil/Sao Paolo', 'symbol'] = df['symbol'].str[:-1]
                    context = {'pesquisa': df.to_dict(orient='records')}
                else:
                    # If the symbol was not found
                    context = {'pesquisa': []}
            # If we don't receive 200 response
            else:
                context = {'pesquisa': []}

            return self.render_to_response(context)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AtivoView(LoginRequiredMixin, FormView):
    template_name = 'ativo.html'
    form_class = AtivoDetalheForm

    def get_success_url(self):
        return reverse('core:index')

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

            try:
                # Retrieve the Ativo instance based on ticker, if it does not exist we can monitor it.
                ativo = Ativo.objects.get(ticker=ticker)
            except Ativo.DoesNotExist:
                return JsonResponse({'is_monitored': False})

            is_monitored = AtivoDetalhe.objects.filter(ativo=ativo, usuario=request.user).exists()
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

        # Check whether the current ativo already exists in the database, if not, it is created.
        ativo, created = Ativo.objects.get_or_create(
            ticker=symbol,
            defaults={'nome': product.info['longName']}
        )
        if not created:
            # Update field if name has changed
            ativo.nome = product.info['longName']
        ativo.preco = preco
        ativo.save()
        # Create AtivoDetalhe
        ativo_detalhe = AtivoDetalhe(
            usuario=self.request.user,
            ativo=ativo,
            periodicidade=form.cleaned_data['periodicidade'],
            limite_superior=form.cleaned_data['limite_superior'],
            limite_inferior=form.cleaned_data['limite_inferior']
        )

        ativo_detalhe.save()
        # Schedule the task for this ativo
        interval, created = IntervalSchedule.objects.get_or_create(
            every=ativo_detalhe.periodicidade,
            period=IntervalSchedule.MINUTES
        )

        PeriodicTask.objects.create(
            interval=interval,
            name=f"Atualiza preço de ativo {ativo_detalhe.id}",
            task='core.tasks.atualiza_preco_ativo',
            args=json.dumps([ativo_detalhe.id]),
        )

        messages.success(self.request, 'Ativo is now being monitored.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Form submission failed.')
        return super().form_invalid(form)

class AtivosSalvosView(LoginRequiredMixin, TemplateView):
    template_name = 'ativos_salvos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Editable Fields
        campos_editaveis = ['periodicidade', 'limite_inferior', 'limite_superior']

        detalhes = AtivoDetalhe.objects.filter(usuario=self.request.user).select_related('ativo')

        data = []
        for detalhe in detalhes:
            # Combine fields from AtivoDetalhe and Ativo
            combined_data = {
                'nome': detalhe.ativo.nome,
                'ticker': detalhe.ativo.ticker,
                'preco': detalhe.ativo.preco,
                'id': detalhe.id,
                'periodicidade': detalhe.periodicidade,
                'limite_inferior': detalhe.limite_inferior,
                'limite_superior': detalhe.limite_superior,
            }
            data.append(combined_data)

        # Buscando ativos salvos na base de dados
        context['ativos'] = data
        context['editaveis'] = campos_editaveis
        return context

    def post(self, request, *args, **kwargs):
        # takes the selected ids in order to delete them
        selected_ids = request.POST.getlist('selected_ativos')
        if selected_ids:
            AtivoDetalhe.objects.filter(id__in=selected_ids).delete()
            messages.success(request, "Ativos selecionados foram excluídos com sucesso.")
        else:
            messages.warning(request, "Nenhum ativo selecionado para exclusão.")
        # The ones that remain will also be updated according to their id and the fields that were changed
        for chave, valor in request.POST.items():
            if chave.startswith('ativo_'):
                _, id, campo = chave.split('_', 2)
                try:
                    ativo = AtivoDetalhe.objects.get(id=id)
                    setattr(ativo, campo, valor.replace(',', '.'))
                    ativo.save()
                except AtivoDetalhe.DoesNotExist:
                    continue
        messages.success(request, 'Ativos Foram Modificados/Salvos com Sucesso.')
        return redirect('core:salvos')

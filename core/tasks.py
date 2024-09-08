from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import yfinance as yf
from .models import Ativo
from django.conf import settings
from django.core.mail import send_mail


class PriceNotFoundException(Exception):
    """Custom exception for when no price data is found."""
    pass


@shared_task
def update_ativo_price(ativo_id):
    try:
        ativo = Ativo.objects.get(id=ativo_id)
        ticker = yf.Ticker(ativo.ticker)
        preco = ticker.history(period='1m', interval='1m')
        if not preco.empty:
            ultimo = preco.iloc[0]
            preco = ultimo['Close']
            print("Ultimo preço registrado atualizado.")
        else:
            # caso não haja dado nenhum preco (O mercado para aquele ativo provavelmente ainda não está aberto)
            # use o preço de fechamento do dia anterior
            preco_dia_anterior = ticker.history(period='1d', interval='1d')  # Dados do último pregão
            if not preco_dia_anterior.empty:
                previous_close = preco_dia_anterior['Close'].iloc[-1]
                preco = previous_close
                print("Nenhum preço encontrado no dia de hoje, atualizando o valor de fechamento do pregão anterior")
            else:
                raise PriceNotFoundException("Nenhum preço encontrado para o ativo.")
        ativo.preco = preco
        ativo.save()

        if preco < ativo.limite_inferior:
            enviar_email(ativo, ticker, 'Oportunidade de Compra!', False)
        elif preco > ativo.limite_superior:
            enviar_email(ativo, ticker, 'Oportunidade de Venda!', True)

    except ObjectDoesNotExist:
        print(f"Ativo com ID {ativo_id} não encontrado.")
    except PriceNotFoundException as e:
        print(e)
    except Exception as e:
        print(f"Erro inesperado: {e}")


def enviar_email(self, ativo, ticker, message, tipo):
    """Send an alert email."""
    current_user = ativo.usuario.email
    if tipo:
        direcao = 'superior'
        limite = ativo.limite_superior
    else:
        direcao = 'inferior'
        limite = ativo.limite_inferior
    send_mail(
        subject=f'{message}: {ativo.ticker} - {ativo.nome}',
        message=f'O preço da ({ativo.ticker}) ultrapassou o limite {direcao} definido.\n'
                f'Limite {direcao} definido: {limite}\nPreço atual: {ativo.preco}\nBid: {ticker.info["bid"]}'
                f'\nAsk: {ticker.info["ask"]}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=current_user,  # Assuming Ativo has a related 'cliente' with an 'email' field
    )




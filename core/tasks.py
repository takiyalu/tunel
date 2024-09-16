import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import yfinance as yf
from .models import AtivoDetalhe
from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


class PriceNotFoundException(Exception):
    """Custom exception for when no price data is found."""
    pass


@shared_task
def atualiza_preco_ativo(detalhe_id):
    try:
        detalhe = AtivoDetalhe.objects.get(id=detalhe_id)
        ticker = yf.Ticker(detalhe.ativo.ticker)
        preco = ticker.history(period='1d')
        if not preco.empty:
            preco = preco.iloc[0]['Close']
        else:
            # caso não haja dado nenhum preco (O mercado para aquele ativo provavelmente ainda não está aberto ou ja
            # fechou) utilizamos o último valor registrado
            preco = ticker.info['previousClose']
            if preco is None:
                raise PriceNotFoundException("Nenhum preço encontrado para o ativo.")
        detalhe.ativo.preco = preco
        detalhe.ativo.save()
        if not detalhe.email_enviado:
            if preco < detalhe.limite_inferior:
                enviar_email(detalhe, ticker, tipo=False)
            elif preco > detalhe.limite_superior:
                enviar_email(detalhe, ticker, tipo=True)
        else:
            if detalhe.limite_inferior < preco < detalhe.limite_superior:
                detalhe.email_enviado = False
                detalhe.save()
        return preco

    except ObjectDoesNotExist:
        logger.error(f"Ativo com ID {detalhe_id} não encontrado.")
    except PriceNotFoundException as e:
        logger.error(f"Erro ao atualizar preço para o ativo {detalhe_id}: {e}")
    except Exception as ex:
        logger.error(f"Erro ao atualizar preço para o ativo {detalhe_id}: {ex}")


def enviar_email(detalhe, ticker, tipo):
    current_user = detalhe.usuario.email
    if tipo:
        message = 'Oportunidade de Venda!'
        direcao = 'superior'
        limite = detalhe.limite_superior
    else:
        message = 'Oportunidade de Compra!'
        direcao = 'inferior'
        limite = detalhe.limite_inferior

    send_mail(
        subject=f'{message}: {detalhe.ativo.ticker} - {detalhe.ativo.nome}',
        message=f'O preço da ({detalhe.ativo.ticker}) ultrapassou o limite {direcao} definido.\n'
                f'Limite {direcao} definido: {limite}\nPreço atual: {detalhe.ativo.preco}\nBid: {ticker.info["bid"]}'
                f'\nAsk: {ticker.info["ask"]}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[current_user],
    )
    detalhe.email_enviado = True
    detalhe.save()


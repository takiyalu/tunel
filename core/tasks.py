import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import yfinance as yf
from .models import Ativo
from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


class PriceNotFoundException(Exception):
    """Custom exception for when no price data is found."""
    pass


@shared_task
def atualiza_preco_ativo(ativo_id, **kwargs):
    logger.debug(f"Task atualiza_preco_ativo started with ativo_id: {ativo_id}")
    try:
        ativo = Ativo.objects.get(id=ativo_id)
        ticker = yf.Ticker(ativo.ticker)
        preco = ticker.history(period='1d')
        if not preco.empty:
            preco = preco.iloc[0]['Close']
        else:
            # caso não haja dado nenhum preco (O mercado para aquele ativo provavelmente ainda não está aberto ou ja
            # fechou) utilizamos o último valor registrado
            preco = ticker.info['previousClose']
            if preco is None:
                raise PriceNotFoundException("Nenhum preço encontrado para o ativo.")
        ativo.preco = preco
        ativo.save()

        if preco < ativo.limite_inferior:
            enviar_email(ativo, ticker, tipo=False)
        elif preco > ativo.limite_superior:
            enviar_email(ativo, ticker, tipo=True)
        return preco
    except ObjectDoesNotExist:
        logger.error(f"Ativo com ID {ativo_id} não encontrado.")
    except PriceNotFoundException as e:
        logger.error(f"Erro ao atualizar preço para o ativo {ativo_id}: {e}")
    except Exception as ex:
        logger.error(f"Erro ao atualizar preço para o ativo {ativo_id}: {ex}")


def enviar_email(ativo, ticker, tipo):
    current_user = ativo.usuario.email
    if tipo:
        message = 'Oportunidade de Venda!'
        direcao = 'superior'
        limite = ativo.limite_superior
    else:
        message = 'Oportunidade de Compra!'
        direcao = 'inferior'
        limite = ativo.limite_inferior

    send_mail(
        subject=f'{message}: {ativo.ticker} - {ativo.nome}',
        message=f'O preço da ({ativo.ticker}) ultrapassou o limite {direcao} definido.\n'
                f'Limite {direcao} definido: {limite}\nPreço atual: {ativo.preco}\nBid: {ticker.info["bid"]}'
                f'\nAsk: {ticker.info["ask"]}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[current_user],
    )

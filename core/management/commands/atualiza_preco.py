import yfinance as yf
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from core.models import Ativo


class Command(BaseCommand):
    help = ('Atualiza o preço do ativo de acordo com o ultimo valor atualizado ou o preço de fechamento do pregão'
            ' anterior em caso de abertura')

    def handle(self, *args, **kwargs):
        ativos = Ativo.objects.all()  # Retrieve all Ativo instances

        for ativo in ativos:
            symbol = ativo.ticker
            ticker = yf.Ticker(symbol)

            # Attempt to fetch the last minute's data for today
            data = ticker.history(period='1m', interval='1m')

            if not data.empty:
                # If there is data for today, use the latest price
                ultimo = data.iloc[0]
                preco = ultimo['Close']
                self.stdout.write(self.style.SUCCESS(f'Updated {symbol} with today\'s latest price: {preco}'))
            else:
                # caso não haja dado nenhum (O mercado para aquele ativo provavelmente ainda não esta aberto)
                # use o preço de fechamento do dia anterior
                previous_data = ticker.history(period='1d', interval='1d')  # Dados do último pregão
                if not previous_data.empty:
                    previous_close = previous_data['Close'].iloc[-1]
                    preco = previous_close
                    self.stdout.write(
                        self.style.WARNING(f'Nenhuma atualização de preço encontrada hoje para {symbol}. '
                                           f'Utilizando preço de fechamento do dia anterior: {preco}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Ativo não encontrado {symbol}.'))
                    continue  # Pula este ativo caso nenhum dado seja encontrado

            # Atualiza o preço e salva no banco de dados
            ativo.preco = preco
            ativo.save(update_fields=['preco'])

            if preco < ativo.limite_inferior:
                self.enviar_email(ativo, ticker, 'Oportunidade de Compra!', False)
            elif preco > ativo.limite_superior:
                self.enviar_email(ativo, ticker, 'Oportunidade de Venda!', True)

    def enviar_email(self, ativo, ticker, message, tipo):
        """Send an alert email."""
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
            recipient_list=[ativo.cliente.email],  # Assuming Ativo has a related 'cliente' with an 'email' field
        )
import yfinance as yf
from django.core.management.base import BaseCommand
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
                latest = data.iloc[0]
                price = latest['Close']
                self.stdout.write(self.style.SUCCESS(f'Updated {symbol} with today\'s latest price: {price}'))
            else:
                # If no data is available (likely the market just opened), use the previous day's closing price
                previous_data = ticker.history(period='1d', interval='1d')  # Fetch yesterday's data
                if not previous_data.empty:
                    previous_close = previous_data['Close'].iloc[-1]
                    price = previous_close
                    self.stdout.write(
                        self.style.WARNING(f'Nenhuma atualização de preço encontrada hoje para {symbol}. '
                                           f'Utilizando preço de fechamento do dia anterior: {price}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Ativo não encontrado {symbol}.'))
                    continue  # Pula este ativo caso nenhum dado seja encontrado

            # Update the preco field for the current Ativo instance
            ativo.preco = price
            ativo.save(update_fields=['preco'])

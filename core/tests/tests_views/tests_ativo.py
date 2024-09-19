from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from core.models import Ativo, AtivoDetalhe
import pandas as pd
from decimal import Decimal

User = get_user_model()

class AtivoViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('core:ativo-detail', kwargs={'symbol': 'AAPL'})
        self.ativo = Ativo.objects.create(
            nome='Test Asset',
            ticker='AAPL',
            preco=Decimal('150.00'),
        )
        self.detalhe = AtivoDetalhe.objects.create(
            ativo=self.ativo,
            usuario=self.user,
            periodicidade=5,
            limite_inferior=Decimal('200.00'),
            limite_superior=Decimal('100.50')
        )

    @patch('yfinance.Ticker')
    def test_ativo_view_get(self, mock_ticker):
        mock_ticker_instance = mock_ticker.return_value
        mock_ticker_instance.history.return_value = pd.DataFrame({
            'Open': [Decimal('100.00'), Decimal('100.00')],
            'High': [Decimal('110.00'), Decimal('110.00')],
            'Low': [Decimal('95.00'), Decimal('95.00')],
            'Close': [Decimal('150.00'), Decimal('140.00')],
            'Adj Close': [Decimal('150.00'), Decimal('150.00')],
            'Volume': [1000, 1000]
        })
        mock_ticker_instance.info = {
            'previousClose': 100.00,
            'longName': 'Apple Inc.',
            'symbol': 'AAPL'
        }
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ativo.html')

    @patch('yfinance.Ticker')
    def test_ativo_view_post(self, mock_ticker):
        mock_ticker_instance = mock_ticker.return_value
        mock_ticker_instance.history.return_value = pd.DataFrame({
            'Open': [Decimal('100.00'), Decimal('100.00')],
            'High': [Decimal('110.00'), Decimal('110.00')],
            'Low': [Decimal('95.00'), Decimal('95.00')],
            'Close': [Decimal('150.00'), Decimal('140.00')],
            'Adj Close': [Decimal('150.00'), Decimal('150.00')],
            'Volume': [1000, 1000]
        })
        mock_ticker_instance.info = {
            'previousClose': 100.00,
            'longName': 'Apple Inc.',
            'symbol': 'AAPL'
        }
        form_data = {
            'periodicidade': 5,
            'limite_superior': '200.00',
            'limite_inferior': '100.00'
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ativo.objects.filter(ticker='AAPL').exists())

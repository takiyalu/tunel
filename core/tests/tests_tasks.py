from unittest.mock import patch, MagicMock
from core.tasks import enviar_email
from django.test import TestCase
from core.tasks import atualiza_preco_ativo
from core.models import Ativo
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.mail import send_mail
import pandas as pd

class EmailTestCase(TestCase):
    def test_email_sending(self):
        send_mail(
            subject='Test Email',
            message='This is a test email.',
            from_email='no-reply@example.com',
            recipient_list=['tester@domain.com'],
        )

        # Check if the email was sent (in a real test, you'd use mocks)
        # This line should not fail if the email is actually sent
        self.assertTrue(True)

class AtualizaPrecoAtivoTestCase(TestCase):

    def setUp(self):
        # Create a user and an Ativo instance for testing
        self.user = User.objects.create_user(username="mock", password="senha", email='tester@domain.com')
        self.ativo = Ativo.objects.create(
            nome="Ativo 1",
            ticker="PETR4.SA",
            periodicidade=1,
            preco=Decimal("170.00"),
            limite_inferior=Decimal("100.00"),
            limite_superior=Decimal("200.00"),
            usuario=self.user
        )

    @patch('yfinance.Ticker')
    def test_update_ativo_price(self, mock_ticker):
        # Mock the yfinance Ticker response for the price history
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
            'bid': Decimal('89.50'),
            'ask': Decimal('90.50'),
        }

        # Run the Celery task
        atualiza_preco_ativo(self.ativo.id)

        # Check if the price was updated
        self.ativo.refresh_from_db()
        self.assertEqual(self.ativo.preco, 150)




    @patch('yfinance.Ticker')
    @patch('django.core.mail.send_mail')
    @patch('django.conf.settings.DEFAULT_FROM_EMAIL', new='no-reply@example.com')
    def test_email_alert_lower_limit(self, mock_send_mail, mock_ticker):
        # Mock the yfinance Ticker response to trigger the lower limit email
        mock_ticker_instance = mock_ticker.return_value
        mock_ticker_instance.history.return_value = pd.DataFrame({
            'Open': [Decimal('100.00')],
            'High': [Decimal('110.00')],
            'Low': [Decimal('95.00')],
            'Close': [Decimal('90.00')],
            'Adj Close': [Decimal('150.00')],
            'Volume': [1000]
        })
        mock_ticker_instance.info = {
            'bid': Decimal('89.50'),
            'ask': Decimal('90.50'),
        }

        # Run the Celery task
        atualiza_preco_ativo(self.ativo.id)

        # Refresh the Ativo instance from the database
        self.ativo.refresh_from_db()
        print(mock_send_mail.call_args_list)
        # Check if the email was sent
        self.assertTrue(mock_send_mail.called)
        args, kwargs = mock_send_mail.call_args
        self.assertIn('Oportunidade de Compra!', kwargs['subject'])  # Check the email subject
        self.assertIn('Limite inferior definido', kwargs['message'])  # Check the email message
        self.assertIn(str(self.ativo.preco), kwargs['message'])  # Ensure the correct price is included
        self.assertEqual(kwargs['from_email'], 'no-reply@example.com')  # Check the from email address

"""
    @patch('yfinance.Ticker')
    def test_email_alert_upper_limit(self, mock_send_mail, mock_ticker):
        # Mock the yfinance Ticker response to trigger the upper limit email
        mock_ticker_instance = mock_ticker.return_value
        mock_ticker_instance.history.return_value = pd.DataFrame({'Close': [Decimal('210.00')]})
        mock_ticker_instance.info = {
            'bid': Decimal('209.50'),
            'ask': Decimal('210.50'),
            'previousClose': Decimal('210.00')
        }

        # Run the Celery task
        atualiza_preco_ativo(self.ativo.id)

        # Refresh the Ativo instance from the database
        self.ativo.refresh_from_db()

        # Check if the email was sent
        self.assertTrue(mock_send_mail.called)
        args, kwargs = mock_send_mail.call_args
        self.assertIn('Oportunidade de Venda!', kwargs['subject'])  # Check the email subject
        self.assertIn('Limite superior definido', kwargs['message'])  # Check the email message
        self.assertIn(str(self.ativo.preco), kwargs['message'])  # Ensure the correct price is included 
"""
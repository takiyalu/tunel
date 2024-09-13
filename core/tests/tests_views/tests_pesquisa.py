from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User

class PesquisaViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')  # Ensure login
        self.url = reverse('core:pesquisa')

    @patch('requests.get')
    def test_pesquisa_view_get(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'symbol,region\nAAPL,US'
        response = self.client.get(self.url, {'palavra_chave': 'AAPL'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pesquisa.html')
        self.assertContains(response, 'AAPL')
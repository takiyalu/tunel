from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Ativo

User = get_user_model()

class AtivosSalvosViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('core:salvos')
        self.ativo = Ativo.objects.create(
            nome='Test Asset',
            ticker='AAPL',
            preco=150.00,
            periodicidade=5,
            limite_superior=200.00,
            limite_inferior=100.00,
            usuario=self.user
        )

    def test_ativos_salvos_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ativos_salvos.html')
        self.assertContains(response, 'Test Asset')

    def test_atualiza_ativo_post(self):
        form_data = {
            f'ativo_{self.ativo.id}_periodicidade': 10  # Ensure this matches the expected format
        }
        response = self.client.post(self.url, data=form_data)

        # Check if the response is a redirect
        self.assertRedirects(response, reverse('core:salvos'))

        # Refresh the Ativo instance and check the updated value
        self.ativo.refresh_from_db()
        self.assertEqual(self.ativo.periodicidade, 10)

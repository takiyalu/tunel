from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from core.forms import CadastroForm

User = get_user_model()

class CadastroViewTest(TestCase):

    def setUp(self):
        self.url = reverse('core:cadastro')

    def test_cadastro_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro.html')

    def test_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password1': 'A$ecurePassw0rd123!',
            'password2': 'A$ecurePassw0rd123!',
            'email': 'tester@domain.com'
        }
        response = self.client.post(self.url, data=form_data)
        if response.status_code == 200:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(response, reverse('core:login'))
        # Ensure the user was created in the database
        self.assertTrue(User.objects.filter(username='testuser').exists())

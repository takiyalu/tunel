from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AtualizaPerfilViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('core:atualiza-perfil')  # Ensure this is the correct name

    def test_form_valid_redirect(self):
        form_data = {
            'username': 'newusername',  # Ensure these match the fields in your form
            'first_name': 'New First Name',
            'last_name': 'New Last Name',
            'email': 'tester@example.com',
            'date_joined': self.user.date_joined.date().strftime('%Y-%m-%d')
            # Add any other required fields
        }
        response = self.client.post(self.url, data=form_data)
        if response.status_code == 200:
            print(response.context['form'].errors)
        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)
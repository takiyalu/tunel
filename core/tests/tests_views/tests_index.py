from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class IndexViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')  # Ensure login
        self.url = reverse('core:index')

    def test_index_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_form_valid_redirect(self):
        form_data = {'palavra_chave': 'test'}
        response = self.client.get(self.url, data=form_data)

        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)

        # Extract the redirect URL
        redirect_url = response.headers['Location']

        # Expected redirect URL without csrfmiddlewaretoken
        expected_redirect_url = reverse('core:pesquisa') + '?palavra_chave=test'

        # Compare URLs while ignoring the CSRF token
        self.assertTrue(redirect_url.startswith(expected_redirect_url))

        # Follow the redirect to ensure the final response is correct
        response = self.client.get(redirect_url)

        # Check the final response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pesquisa.html')
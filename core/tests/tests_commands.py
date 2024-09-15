from django.core.management import call_command
from django.test import TestCase
from core.models import Ativo
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.models import User
<<<<<<< HEAD
=======
from django.core.cache import cache
from unittest.mock import patch
from django.conf import settings
>>>>>>> 554fc60bbd804f2a07422eeeb118d230d2125621

class AtualizaPrecoCommandTestCase(TestCase):

    def setUp(self):
        # Cria usuário
        self.user = User.objects.create_user(username="tester", password="senha")
        # Create some Ativo objects for testing
        Ativo.objects.create(nome="Ativo 1", ticker="PETR4.SA", periodicidade=1, preco=38.30, limite_inferior=38.00,
                             limite_superior=38.50)
        Ativo.objects.create(nome="Ativo 2", ticker="CSAN3.SA", periodicidade=1, preco=13.42, limite_inferior=13.35,
                             limite_superior=13.50)

    def test_task_scheduling(self):
        # Call the command
        call_command('atualiza_preco')

        # Check if PeriodicTask objects were created
        tasks = PeriodicTask.objects.all()
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.first().name, "Atualiza preço de ativo 1")
<<<<<<< HEAD
=======


class ClearCacheCommandTest(TestCase):
    @patch('django.core.cache.cache.clear')
    def test_cache_cleared(self, mock_clear):
        # Set some data in the cache
        cache.set('key', 'value')

        # Check that data exists in the cache before running the command
        self.assertEqual(cache.get('key'), 'value')

        # Run the management command
        call_command('limpar_cache')

        # Check that the cache was cleared
        self.assertIsNone(cache.get('key'))

    @patch('sys.stdout.write')
    def test_command_output(self, mock_write):
        # Run the management command
        call_command('limpar_cache')

        # Check that the command output is as expected
        mock_write.assert_called_with('Cache cleared successfully\n')


class CacheBackendTest(TestCase):

    def test_cache_backend(self):
        cache_backend = settings.CACHES['default']['BACKEND']
        print(f"Cache backend in use: {cache_backend}")
        self.assertEqual(cache_backend, 'django.core.cache.backends.locmem.LocMemCache')


class UniqueCacheKeysTest(TestCase):

    def test_unique_cache_keys(self):
        cache.set('user_data_1', 'user_1_data')
        cache.set('user_data_2', 'user_2_data')

        # Assert both cache keys hold different values
        self.assertEqual(cache.get('user_data_1'), 'user_1_data')
        self.assertEqual(cache.get('user_data_2'), 'user_2_data')

        # Ensure key uniqueness by checking they don't override each other
        self.assertNotEqual(cache.get('user_data_1'), cache.get('user_data_2'))
>>>>>>> 554fc60bbd804f2a07422eeeb118d230d2125621

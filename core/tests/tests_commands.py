from django.core.management import call_command
from django.test import TestCase
from core.models import Ativo
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.models import User

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

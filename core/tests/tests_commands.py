from django.core.management import call_command
from django.test import TestCase
from core.models import Ativo, AtivoDetalhe
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.models import User
from decimal import Decimal

class AtualizaPrecoCommandTestCase(TestCase):

    def setUp(self):
        # Cria usuário
        self.user = User.objects.create_user(username="tester", password="senha")
        # Create some Ativo objects for testing
        # Create a sample Ativo instance
        ativo1 = Ativo.objects.create(
            nome='Ativo 1',
            ticker='PETR4.SA',
            preco=Decimal('38.30')
        )

        self.detalhe = AtivoDetalhe.objects.create(
            ativo=ativo1,
            usuario=self.user,
            periodicidade=1,
            limite_inferior=Decimal('38.00'),
            limite_superior=Decimal('38.50')
        )

        ativo2 = Ativo.objects.create(
            nome='Ativo 2',
            ticker='CSAN3.SA',
            preco=Decimal('13.42')
        )

        self.detalhe = AtivoDetalhe.objects.create(
            ativo=ativo2,
            usuario=self.user,
            periodicidade=1,
            limite_inferior=Decimal('13.35'),
            limite_superior=Decimal('13.50')
        )

    def test_task_scheduling(self):
        # Call the command
        call_command('atualiza_preco')

        # Check if PeriodicTask objects were created
        tasks = PeriodicTask.objects.all()
        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks.first().name, "Atualiza preço de ativo 1")

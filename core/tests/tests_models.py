from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import Ativo, AtivoDetalhe


class AtivoDetalheModelTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create a sample Ativo instance
        self.ativo = Ativo.objects.create(
            nome='Test Ativo',
            ticker='TEST',
            preco=Decimal('100.50')
        )

        self.detalhe = AtivoDetalhe.objects.create(
            ativo=self.ativo,
            usuario=self.user,
            periodicidade=30,
            limite_inferior=Decimal('90.00'),
            limite_superior=Decimal('110.00')
        )

    def test_ativo_creation(self):
        """Test that the Ativo model is correctly created."""
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo.nome, 'Test Ativo')
        self.assertEqual(ativo.ticker, 'TEST')
        self.assertEqual(ativo.preco, Decimal('100.50'))

    def test_detalhe_creation(self):
        """Test that the Ativo model is correctly created."""
        detalhe = AtivoDetalhe.objects.get(id=self.detalhe.id)
        self.assertEqual(detalhe.ativo, self.ativo)
        self.assertEqual(detalhe.usuario, self.user)
        self.assertEqual(detalhe.periodicidade, 30)
        self.assertEqual(detalhe.limite_inferior, Decimal('90.00'))
        self.assertEqual(detalhe.limite_superior, Decimal('110.00'))


    def test_auto_fields(self):
        """Test that the auto fields (created, updated, active) are correctly set."""
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertTrue(ativo.created)
        self.assertTrue(ativo.updated)
        self.assertTrue(ativo.active)
        detalhe = AtivoDetalhe.objects.get(id=self.detalhe.id)
        self.assertTrue(detalhe.created)
        self.assertTrue(detalhe.updated)
        self.assertTrue(detalhe.active)

    def test_ativo_related_to_user(self):
        """Test the relationship between Ativo and User."""
        self.assertEqual(self.detalhe.usuario.username, 'testuser')
        self.assertEqual(self.user.ativo_detalhes.count(), 1)  # The user should have 1 ativo linked to them

    def test_ativo_limited_value_constraints(self):
        """Test that the ativo price falls between the limits."""
        self.assertGreaterEqual(self.ativo.preco, self.detalhe.limite_inferior)
        self.assertLessEqual(self.ativo.preco, self.detalhe.limite_superior)

    def test_ativo_upper_limit_violation(self):
        """Test if the upper limit is violated."""
        self.ativo.preco = Decimal('120.00')
        self.ativo.save()
        self.assertGreater(self.ativo.preco, self.detalhe.limite_superior)

    def test_ativo_lower_limit_violation(self):
        """Test if the lower limit is violated."""
        self.ativo.preco = Decimal('80.00')
        self.ativo.save()
        self.assertLess(self.ativo.preco, self.detalhe.limite_inferior)
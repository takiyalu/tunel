from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import Ativo


class AtivoModelTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create a sample Ativo instance
        self.ativo = Ativo.objects.create(
            nome='Test Ativo',
            ticker='TEST',
            periodicidade=30,
            preco=Decimal('100.50'),
            limite_inferior=Decimal('90.00'),
            limite_superior=Decimal('110.00'),
            usuario=self.user
        )

    def test_ativo_creation(self):
        """Test that the Ativo model is correctly created."""
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo.nome, 'Test Ativo')
        self.assertEqual(ativo.ticker, 'TEST')
        self.assertEqual(ativo.periodicidade, 30)
        self.assertEqual(ativo.preco, Decimal('100.50'))
        self.assertEqual(ativo.limite_inferior, Decimal('90.00'))
        self.assertEqual(ativo.limite_superior, Decimal('110.00'))
        self.assertEqual(ativo.usuario, self.user)

    def test_string_representation(self):
        """Test the __str__ method of the Ativo model."""
        self.assertEqual(str(self.ativo), f'TEST - 100.50 at {self.ativo.updated}')

    def test_auto_fields(self):
        """Test that the auto fields (created, updated, active) are correctly set."""
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertTrue(ativo.created)
        self.assertTrue(ativo.updated)
        self.assertTrue(ativo.active)

    def test_ativo_related_to_user(self):
        """Test the relationship between Ativo and User."""
        self.assertEqual(self.ativo.usuario.username, 'testuser')
        self.assertEqual(self.user.ativos.count(), 1)  # The user should have 1 ativo linked to them

    def test_ativo_limited_value_constraints(self):
        """Test that the ativo price falls between the limits."""
        self.assertGreaterEqual(self.ativo.preco, self.ativo.limite_inferior)
        self.assertLessEqual(self.ativo.preco, self.ativo.limite_superior)

    def test_ativo_upper_limit_violation(self):
        """Test if the upper limit is violated."""
        self.ativo.preco = Decimal('120.00')
        self.ativo.save()
        self.assertGreater(self.ativo.preco, self.ativo.limite_superior)

    def test_ativo_lower_limit_violation(self):
        """Test if the lower limit is violated."""
        self.ativo.preco = Decimal('80.00')
        self.ativo.save()
        self.assertLess(self.ativo.preco, self.ativo.limite_inferior)
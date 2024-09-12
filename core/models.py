from django.db import models
from django.contrib.auth.models import User


class Base(models.Model):
    created = models.DateTimeField('Creation', auto_now_add=True)
    updated = models.DateTimeField('Last Update', auto_now=True)
    active = models.BooleanField('Active?', default=True)

    class Meta:
        abstract = True


class Ativo(Base):
    nome = models.CharField('Nome', max_length=100)
    ticker = models.CharField('Ticker', max_length=10)
    periodicidade = models.IntegerField('Periodicidade')
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=20)
    limite_inferior = models.DecimalField('Inferior', decimal_places=2, max_digits=20)
    limite_superior = models.DecimalField('Superior', decimal_places=2, max_digits=20)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ativos', default=1)

    class Meta:
        verbose_name = 'Ativo'
        verbose_name_plural = 'Ativos'

    def __str__(self):
        return f'{self.ticker} - {self.preco} at {self.updated}'


